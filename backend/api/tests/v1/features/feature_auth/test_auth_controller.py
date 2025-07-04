from datetime import timedelta

import pytest
from httpx import ASGITransport, AsyncClient

from api.common.test_data import TestData
from api.v1.features.feature_auth.security import create_access_token
from main import app

# =============================================================================
# テストヘルパー関数
# =============================================================================


async def setup_authenticated_client_with_manual_token(client: AsyncClient, email: str, password: str) -> str:
    """手動でJWTトークンを生成して認証済みクライアントを作成するヘルパー関数

    【使用方法】
    実際のJWTトークンを生成してクッキーに設定し、実際のユーザー操作をテストします。

    【テスト対象エンドポイント】
    - DELETE /api/v1/auth/me - アカウント削除（論理削除）
    - POST /api/v1/auth/signup - ユーザー登録（復活機能テスト）
    - PATCH /api/v1/auth/me - ユーザー情報更新
    - その他実際のデータ変更を伴う操作

    【テスト内容】
    - 論理削除済みユーザーの復活機能テスト
    - 削除済みユーザーでの操作拒否テスト
    - 期限切れJWTトークンでの操作拒否テスト
    - 実際のデータベース状態変更を伴うエンドツーエンドテスト

    【特徴】
    - 実際のJWTトークン生成
    - データベース操作を伴う（統合テスト）
    - AsyncClientのクッキー処理問題を回避
    - 実際のユーザー認証フローに近い動作

    【authenticated_client フィクスチャとの違い】
    - authenticated_client: 依存性注入のオーバーライドでモックユーザーを提供（推奨・高速）
    - この関数: 実際のJWTトークンを生成してクッキーに設定（特殊用途・重い）

    【使用シナリオ】
    - 論理削除後の復活テスト
    - 削除済みユーザーでの操作テスト
    - JWT期限切れテスト
    - 実際のデータ変更が必要なテスト

    NOTE: 通常のテストでは authenticated_client フィクスチャ（fixtures/authenticate_fixture.py）を使用してください。
    この関数は論理削除など、実際のユーザー操作が必要な特別なシナリオでのみ使用します。
    """
    # 手動でJWTトークンを生成して設定（AsyncClientのクッキー処理問題を回避）
    auth_token = create_access_token(data={"sub": email, "client_ip": "127.0.0.1"})
    client.cookies.set("authToken", auth_token)
    return auth_token


# NOTE: 重い処理を伴うテストはパフォーマンス向上のため軽量化済み。DB検証が必要な場合は別途統合テストとして実装。


@pytest.mark.asyncio(loop_scope="session")
async def test_login_user() -> None:
    """POST /api/v1/auth/login

    【正常系】テーブルに存在するユーザーでログインする
    """
    # 既存のPostgreSQLベースのテスト環境を使用（実行時間短縮）
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost:8000/") as client:
        # シードデータを使用（既に高速化済み）
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
        response_json.get("message", "")
        assert "ログインに成功しました" == response_json.get("message", "")


@pytest.mark.asyncio(loop_scope="session")
async def test_login_with_invalid_credentials() -> None:
    """POST /api/v1/auth/login

    【異常系】存在しないユーザーでログインする
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
    """POST /api/v1/auth/signup

    【正常系】JWTトークンを使用してユーザー登録を行う
    """
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
    """POST /api/v1/auth/reset-password

    【正常系】JWTトークンを使用してパスワードリセットを行う（軽量版・レスポンス確認のみ）
    """
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
    """POST /api/v1/auth/send-verify-email

    【正常系】仮登録用メール送信を行う（メール送信無効化）
    """
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
    """POST /api/v1/auth/send-password-reset-email

    【正常系】パスワードリセット用メール送信を行う（メール送信無効化）
    """
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
    """POST /api/v1/auth/logout

    【正常系】認証済みユーザーのログアウト処理を行う
    """

    response = await authenticated_client.post(
        "/api/v1/auth/logout",
        json={"email": TestData.TEST_USER_EMAIL_1},
    )

    assert response.status_code == 200, response.text
    assert response.json()["message"] == "ログアウトしました"


@pytest.mark.asyncio(loop_scope="session")
async def test_register_with_invalid_token() -> None:
    """POST /api/v1/auth/signup

    【異常系】無効なJWTトークンでユーザー登録を試みる
    """
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
    """POST /api/v1/auth/send-password-reset-email

    【異常系】存在しないメールアドレスでパスワードリセットメール送信を試みる"""
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
    """POST /api/v1/auth/reset-password

    【異常系】無効なJWTトークンでパスワードリセットを試みる"""
    new_password = "newpassword123!"

    response = await authenticated_client.post(
        "/api/v1/auth/reset-password",
        json={"token": "invalid_token", "new_password": new_password},
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 400, response.text


@pytest.mark.asyncio(loop_scope="session")
async def test_logout_with_invalid_token() -> None:
    """POST /api/v1/auth/logout

    【異常系】無効なAuthorizationヘッダーでログアウトを試みる"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost:8000") as client:
        response = await client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": "Bearer invalid_token"},
        )
        assert response.status_code == 401, response.text


@pytest.mark.asyncio(loop_scope="session")
async def test_logout_without_authentication() -> None:
    """POST /api/v1/auth/logout

    【異常系】認証情報なしでログアウトを試みる"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost:8000") as client:
        response = await client.post("/api/v1/auth/logout")
        assert response.status_code == 401, response.text


# =============================================================================
# 追加テストケース - 各種ユーザー状態とJWT有効期限のテスト
# =============================================================================


@pytest.mark.asyncio(loop_scope="session")
async def test_register_user_already_exists() -> None:
    """POST /api/v1/auth/signup

    【異常系】既にアクティブなユーザーが存在するメールアドレスで登録を試みる"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost:8000") as client:
        # テストデータを準備
        await client.post("/api/v1/dev/clear_data")
        await client.post("/api/v1/dev/seed_data")

        # 既存ユーザーと同じメールアドレスで登録を試行
        user_data = {
            "email": TestData.TEST_USER_EMAIL_1,  # 既に存在するメールアドレス
            "username": "newusername",
            "password": "newpassword123!",
        }

        # 仮登録用JWTトークンを生成
        token = create_access_token(data=user_data, expires_delta=timedelta(minutes=60))

        # ユーザー登録を試行
        response = await client.post(
            "/api/v1/auth/signup",
            json={"token": token},
            headers={"Content-Type": "application/json"},
        )

        # 409 Conflictエラーが返されることを確認
        assert response.status_code == 409, response.text
        response_json = response.json()
        assert response_json["success"] is False
        assert "このメールアドレスは既に使用されています" in response_json["message"]


@pytest.mark.asyncio(loop_scope="session")
async def test_register_user_with_deleted_user() -> None:
    """POST /api/v1/auth/signup

    【正常系】論理削除済みユーザーと同じメールアドレスでユーザー登録を行う（復活機能テスト）"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost:8000") as client:
        # テストデータを準備
        await client.post("/api/v1/dev/clear_data")
        await client.post("/api/v1/dev/seed_data")

        # 既存ユーザーでログインしてアカウント削除
        await setup_authenticated_client_with_manual_token(client, TestData.TEST_USER_EMAIL_1, TestData.TEST_USER_PASSWORD)

        # アカウント削除（論理削除）
        delete_response = await client.delete("/api/v1/auth/me")
        assert delete_response.status_code == 200

        # 削除されたユーザーと同じメールアドレスで新規登録（復活）
        user_data = {
            "email": TestData.TEST_USER_EMAIL_1,
            "username": "restored_user",
            "password": "restoredpassword123!",
        }

        # 仮登録用JWTトークンを生成
        token = create_access_token(data=user_data, expires_delta=timedelta(minutes=60))

        # ユーザー登録（復活）を実行
        response = await client.post(
            "/api/v1/auth/signup",
            json={"token": token},
            headers={"Content-Type": "application/json"},
        )

        # 正常に復活されることを確認
        assert response.status_code == 200, response.text
        response_json = response.json()
        assert response_json["success"] is True
        assert "ユーザー登録が完了しました" in response_json["message"]
        assert response_json["data"]["email"] == TestData.TEST_USER_EMAIL_1
        assert response_json["data"]["username"] == "restored_user"


@pytest.mark.asyncio(loop_scope="session")
async def test_register_user_with_expired_jwt() -> None:
    """POST /api/v1/auth/signup

    【異常系】有効期限切れJWTトークンでユーザー登録を試みる"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost:8000") as client:
        import uuid

        user_data = {
            "email": f"test_{uuid.uuid4().hex[:8]}@example.com",
            "username": f"test_{uuid.uuid4().hex[:6]}",
            "password": "password123!",
        }

        # 期限切れのJWTトークンを生成（負の時間で即座に期限切れ）
        expired_token = create_access_token(data=user_data, expires_delta=timedelta(seconds=-1))

        # 期限切れトークンでユーザー登録を試行
        response = await client.post(
            "/api/v1/auth/signup",
            json={"token": expired_token},
            headers={"Content-Type": "application/json"},
        )

        # 400 Bad Requestエラーが返されることを確認
        assert response.status_code == 400, response.text
        response_json = response.json()
        assert response_json["success"] is False
        assert "無効な認証トークンです" in response_json["message"]


@pytest.mark.asyncio(loop_scope="session")
async def test_password_reset_with_deleted_user() -> None:
    """POST /api/v1/auth/send-password-reset-email

    【異常系】論理削除済みユーザーでパスワードリセットメール送信を試みる"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost:8000") as client:
        # テストデータを準備
        await client.post("/api/v1/dev/clear_data")
        await client.post("/api/v1/dev/seed_data")

        # 既存ユーザーでログインしてアカウント削除
        await setup_authenticated_client_with_manual_token(client, TestData.TEST_USER_EMAIL_1, TestData.TEST_USER_PASSWORD)

        # アカウント削除（論理削除）
        delete_response = await client.delete("/api/v1/auth/me")
        assert delete_response.status_code == 200

        # 削除されたユーザーでパスワードリセットメール送信を試行
        response = await client.post(
            "/api/v1/auth/send-password-reset-email",
            json={"email": TestData.TEST_USER_EMAIL_1},
        )

        # 404エラーが返されることを確認（論理削除済みユーザーは見つからない）
        assert response.status_code == 404, response.text
        response_json = response.json()
        assert response_json["success"] is False
        assert "指定されたメールアドレスのユーザーが見つかりません" in response_json["message"]


@pytest.mark.asyncio(loop_scope="session")
async def test_password_reset_with_expired_jwt() -> None:
    """POST /api/v1/auth/reset-password

    【異常系】有効期限切れJWTトークンでパスワードリセットを試みる"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost:8000") as client:
        # テストデータを準備
        await client.post("/api/v1/dev/clear_data")
        await client.post("/api/v1/dev/seed_data")

        # 期限切れのパスワードリセットトークンを生成
        expired_token = create_access_token(data={"email": TestData.TEST_USER_EMAIL_1}, expires_delta=timedelta(seconds=-1))

        # 期限切れトークンでパスワードリセットを試行
        response = await client.post(
            "/api/v1/auth/reset-password",
            json={"token": expired_token, "new_password": "newpassword123!"},
            headers={"Content-Type": "application/json"},
        )

        # 400 Bad Requestエラーが返されることを確認
        assert response.status_code == 400, response.text
        response_json = response.json()
        assert response_json["success"] is False
        assert "無効なリセットトークンです" in response_json["message"]


@pytest.mark.asyncio(loop_scope="session")
async def test_authentication_with_deleted_user() -> None:
    """POST /api/v1/auth/login

    【異常系】論理削除済みユーザーでログインを試みる"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost:8000") as client:
        # テストデータを準備
        await client.post("/api/v1/dev/clear_data")
        await client.post("/api/v1/dev/seed_data")

        # 既存ユーザーでログインしてアカウント削除
        await setup_authenticated_client_with_manual_token(client, TestData.TEST_USER_EMAIL_1, TestData.TEST_USER_PASSWORD)

        # アカウント削除（論理削除）
        delete_response = await client.delete("/api/v1/auth/me")
        assert delete_response.status_code == 200

        # 削除されたユーザーでログインを試行
        login_deleted_response = await client.post(
            "/api/v1/auth/login",
            data={"username": TestData.TEST_USER_EMAIL_1, "password": TestData.TEST_USER_PASSWORD},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        # 401エラーが返されることを確認（削除済みユーザーはログインできない）
        assert login_deleted_response.status_code == 401, login_deleted_response.text
        response_json = login_deleted_response.json()
        assert response_json["success"] is False
        assert "メールアドレスまたはパスワードが無効です" in response_json["message"]


@pytest.mark.asyncio(loop_scope="session")
async def test_user_operations_with_expired_jwt() -> None:
    """POST /api/v1/auth/me, PATCH /api/v1/auth/me, POST /api/v1/auth/logout

    【異常系】有効期限切れJWTで各種ユーザー操作を試みる"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost:8000") as client:
        # テストデータを準備
        await client.post("/api/v1/dev/clear_data")
        await client.post("/api/v1/dev/seed_data")

        # 期限切れのアクセストークンを生成
        expired_token = create_access_token(data={"sub": TestData.TEST_USER_EMAIL_1, "client_ip": "127.0.0.1"}, expires_delta=timedelta(seconds=-1))

        # 期限切れトークンを使ってCookie設定
        client.cookies.set("authToken", expired_token)

        # 現在のユーザー情報取得を試行
        response = await client.post("/api/v1/auth/me")
        assert response.status_code == 401, response.text

        # ユーザー情報更新を試行
        update_response = await client.patch(
            "/api/v1/auth/me",
            json={"username": "updated_name"},
        )
        assert update_response.status_code == 401, update_response.text

        # ログアウトを試行
        logout_response = await client.post("/api/v1/auth/logout")
        assert logout_response.status_code == 401, logout_response.text


@pytest.mark.asyncio(loop_scope="session")
async def test_update_user_info_with_deleted_user() -> None:
    """PATCH /api/v1/auth/me

    【異常系】論理削除済みユーザーでユーザー情報更新を試みる"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost:8000") as client:
        # テストデータを準備
        await client.post("/api/v1/dev/clear_data")
        await client.post("/api/v1/dev/seed_data")

        # 既存ユーザーでログインしてアカウント削除
        await setup_authenticated_client_with_manual_token(client, TestData.TEST_USER_EMAIL_1, TestData.TEST_USER_PASSWORD)

        # アカウント削除（論理削除）
        delete_response = await client.delete("/api/v1/auth/me")
        assert delete_response.status_code == 200

        # 削除されたユーザーでユーザー情報更新を試行
        update_response = await client.patch(
            "/api/v1/auth/me",
            json={"username": "updated_deleted_user"},
        )

        # 401エラーが返されることを確認（削除済みユーザーは操作できない）
        assert update_response.status_code == 401, update_response.text
        response_json = update_response.json()
        assert response_json["success"] is False
        assert "認証情報が無効です" in response_json["message"]
