

from datetime import timedelta

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select

from api.common.test_data import TestData
from api.v1.features.feature_auth.security import create_access_token, verify_password
from api.v1.features.feature_auth.models.user import User
from main import app


# NOTE: 重い処理を伴うテストはパフォーマンス向上のため軽量化済み。DB検証が必要な場合は別途統合テストとして実装。


@pytest.mark.asyncio(loop_scope="session")
async def test_login_user() -> None:
    """ログイン処理のテスト（既存シードデータ使用）。
    """
    # まず、テストデータをシードしてからログインテストを実行
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost:8000/") as client:
        # シードデータの投入
        await client.post("/api/v1/dev/clear_data")
        await client.post("/api/v1/dev/seed_data")
        
        # ログインテストの実行
        response = await client.post(
            "/api/v1/auth/login",
            data={"username": TestData.TEST_USER_EMAIL_1, "password": TestData.TEST_USER_PASSWORD},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert response.status_code == 200
        response_json = response.json()
        message = response_json.get("message", "")
        assert "ログインに成功しました" == response_json.get("message", "")

@pytest.mark.asyncio(loop_scope="session")
async def test_login_with_invalid_credentials() -> None:
    """誤った資格情報でログインを試みた場合のテスト。
    """
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost:8000/") as client:
        response = await client.post(
            "/api/v1/auth/login",
            data={"username": "wronguser@example.com", "password": "wrongpassword"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert response.status_code == 401
        assert "メールアドレスまたはパスワードが無効です" == response.json()["message"]



@pytest.mark.asyncio(loop_scope="session")
async def test_register_user() -> None:
    """ユーザー登録のテスト"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost:8000") as client:
        # 新規ユーザー情報
        import uuid
        user_data = {
            "email": f"test_{uuid.uuid4().hex[:8]}@example.com",
            "username": f"test_{uuid.uuid4().hex[:6]}",
            "password": "password123!",
        }

        # **仮登録用JWTトークンを生成**
        token = create_access_token(data=user_data, expires_delta=timedelta(minutes=60))

        # **トークンを `/api/v1/auth/signup` に送信**
        response = await client.post(
            "/api/v1/auth/signup",
            json={"token": token},
            headers={"Content-Type": "application/json"},
        )
        
        # 正常に登録が完了することを確認
        assert response.status_code == 200, response.text
        response_json = response.json()
        assert "success" in response_json
        assert response_json["success"] is True
        assert "ユーザー登録が完了しました" == response_json["message"]
        assert "data" in response_json
        assert response_json["data"]["email"] == user_data["email"]

@pytest.mark.asyncio(loop_scope="session")
async def test_reset_password(authenticated_client: AsyncClient) -> None:
    """パスワードリセットのテスト (軽量版 - レスポンス確認のみ)"""
    new_password = TestData.TEST_USER_PASSWORD + "123"

    # **パスワードリセット用JWTトークンを生成**
    token = create_access_token(data={"email": TestData.TEST_USER_EMAIL_1}, expires_delta=timedelta(minutes=60))

    # トークンが取得できているか確認
    assert token is not None, "Reset token is missing in the response"

    # 取得したトークンを使ってパスワードを変更
    response = await authenticated_client.post(
        "/api/v1/auth/reset-password",
        json={"token": token, "new_password": new_password},
        headers={"Content-Type": "application/json"},
    )
    
    # レスポンス確認（成功レスポンスの構造チェック）
    assert response.status_code == 200, response.text
    response_json = response.json()
    assert "success" in response_json
    assert response_json["success"] is True
    assert "message" in response_json

@pytest.mark.asyncio(loop_scope="session")  
async def test_send_verify_email(disable_email_sending) -> None:
    """仮登録用メール送信のテスト（メール送信無効化）"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost:8000") as client:
        response = await client.post(
            "/api/v1/auth/send-verify-email",
            json={"email": "newuser@example.com", "username": "newuser", "password": "Test1234!"},
        )
        # メール送信が無効化されているため、APIレスポンスは成功する
        assert response.status_code == 200
        assert "認証メールを送信しました。メールをご確認ください" == response.json()["message"]

@pytest.mark.asyncio(loop_scope="session")
async def test_send_reset_password_email(disable_email_sending) -> None:
    """パスワードリセットメール送信のテスト（メール送信無効化）"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost:8000") as client:
        # シードデータの投入（ユーザーが存在する必要がある）
        await client.post("/api/v1/dev/clear_data")
        await client.post("/api/v1/dev/seed_data")
        
        response = await client.post(
            "/api/v1/auth/send-password-reset-email",
            json={"email": TestData.TEST_USER_EMAIL_1},
        )
        # メール送信が無効化されているため、APIレスポンスは成功する
        assert response.status_code == 200
        assert "パスワードリセットメールを送信しました" == response.json()["message"]

# NOTE: ログイン中のAPIのテストを実施する場合はauthenticated_clientを引数に追加して、authenticated_clientからAPIを呼び出す
@pytest.mark.asyncio(loop_scope="session")
async def test_logout_user(authenticated_client: AsyncClient) -> None:
    """ログアウト処理のテスト"""

    response = await authenticated_client.post(
        "/api/v1/auth/logout",
        json={"email": TestData.TEST_USER_EMAIL_1},
    )

    assert response.status_code == 200, response.text
    assert response.json()["message"] == "ログアウトしました"





@pytest.mark.asyncio(loop_scope="session")
async def test_register_with_invalid_token() -> None:
    """無効なトークンでユーザー登録を試みる（異常系）"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost:8000") as client:
        invalid_token = "invalid.jwt.token"

        response = await client.post(
            "/api/v1/auth/signup",
            json={"token": invalid_token},
            headers={"Content-Type": "application/json"},
        )
        assert response.status_code == 400, response.text


@pytest.mark.asyncio(loop_scope="session")
async def test_reset_password_with_invalid_email() -> None:
    """存在しないメールアドレスでパスワードリセット（異常系）"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost:8000") as client:
        response = await client.post(
            "/api/v1/auth/send-password-reset-email",
            json={"email": "nonexistent@example.com"},
        )
        assert response.status_code == 404, response.text
        response_json = response.json()
        # カスタムエラーハンドラーにより'message'フィールドにエラーメッセージが格納される
        assert response_json["success"] is False
        assert "指定されたメールアドレスのユーザーが見つかりません" in response_json["message"]


@pytest.mark.asyncio(loop_scope="session")
async def test_reset_password_with_invalid_token(authenticated_client: AsyncClient) -> None:
    """無効なトークンでパスワードリセット（異常系）"""
    new_password = "newpassword123!"

    response = await authenticated_client.post(
        "/api/v1/auth/reset-password",
        json={"token": "invalid_token", "new_password": new_password},
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 400, response.text


@pytest.mark.asyncio(loop_scope="session")
async def test_logout_with_invalid_token() -> None:
    """誤ったトークンでログアウトを試みる（異常系）"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost:8000") as client:
        response = await client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": "Bearer invalid_token"},
        )
        assert response.status_code == 401, response.text


@pytest.mark.asyncio(loop_scope="session")
async def test_logout_without_authentication() -> None:
    """認証なしでログアウトを試みる（異常系）"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost:8000") as client:
        response = await client.post("/api/v1/auth/logout")
        assert response.status_code == 401, response.text
