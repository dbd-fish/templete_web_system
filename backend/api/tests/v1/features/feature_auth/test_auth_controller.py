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
    # Arrange: テスト環境とクライアントを準備
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost:8000/") as client:
        await client.post("/api/v1/dev/clear_data")
        await client.post("/api/v1/dev/seed_data")

        login_data = {"username": TestData.TEST_USER_EMAIL_1, "password": TestData.TEST_USER_PASSWORD}
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        # Act: ログインAPIを実行
        response = await client.post(
            "/api/v1/auth/login",
            data=login_data,
            headers=headers,
        )

        # Assert: ログイン成功レスポンスを検証
        assert response.status_code == 200
        response_json = response.json()
        assert "ログインに成功しました" == response_json.get("message", "")


@pytest.mark.asyncio(loop_scope="session")
async def test_login_with_invalid_credentials() -> None:
    """POST /api/v1/auth/login

    【異常系】存在しないユーザーでログインする
    """
    # Arrange: 不正な認証情報とクライアントを準備
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost:8000/") as client:
        invalid_credentials = {"username": "wronguser@example.com", "password": "wrongpassword"}
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        # Act: 不正な認証情報でログインを試行
        response = await client.post(
            "/api/v1/auth/login",
            data=invalid_credentials,
            headers=headers,
        )

        # Assert: 認証エラーレスポンスを検証
        assert response.status_code == 401
        assert "メールアドレスまたはパスワードが無効です" == response.json()["message"]


@pytest.mark.asyncio(loop_scope="session")
async def test_register_user() -> None:
    """POST /api/v1/auth/signup

    【正常系】JWTトークンを使用してユーザー登録を行う
    """
    # Arrange: 新規ユーザー情報とトークンを準備
    import uuid

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost:8000") as client:
        user_data = {
            "email": f"test_{uuid.uuid4().hex[:8]}@example.com",
            "username": f"test_{uuid.uuid4().hex[:6]}",
            "password": "password123!",
        }
        token = create_access_token(data=user_data, expires_delta=timedelta(minutes=60))
        signup_payload = {"token": token}
        headers = {"Content-Type": "application/json"}

        # Act: ユーザー登録APIを実行
        response = await client.post(
            "/api/v1/auth/signup",
            json=signup_payload,
            headers=headers,
        )

        # Assert: 登録成功レスポンスを検証
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
    # Arrange: パスワードリセット用トークンとデータを準備
    new_password = TestData.TEST_USER_PASSWORD + "123"
    token = create_access_token(data={"email": TestData.TEST_USER_EMAIL_1}, expires_delta=timedelta(minutes=60))
    reset_payload = {"token": token, "new_password": new_password}
    headers = {"Content-Type": "application/json"}

    # Arrange: トークンが正常に生成されていることを確認
    assert token is not None, "Reset token is missing in the response"

    # Act: パスワードリセットAPIを実行
    response = await authenticated_client.post(
        "/api/v1/auth/reset-password",
        json=reset_payload,
        headers=headers,
    )

    # Assert: リセット成功レスポンスを検証
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
    # Arrange: 仮登録用ユーザー情報とクライアントを準備
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost:8000") as client:
        verification_data = {"email": "newuser@example.com", "username": "newuser", "password": "Test1234!"}

        # Act: 認証メール送信APIを実行
        response = await client.post(
            "/api/v1/auth/send-verify-email",
            json=verification_data,
        )

        # Assert: メール送信成功レスポンスを検証（メール送信は無効化済み）
        assert response.status_code == 200
        assert "認証メールを送信しました。メールをご確認ください" == response.json()["message"]


@pytest.mark.asyncio(loop_scope="session")
async def test_send_reset_password_email(disable_email_sending) -> None:
    """POST /api/v1/auth/send-password-reset-email

    【正常系】パスワードリセット用メール送信を行う（メール送信無効化）
    """
    # Arrange: テストデータとクライアントを準備
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost:8000") as client:
        await client.post("/api/v1/dev/clear_data")
        await client.post("/api/v1/dev/seed_data")

        reset_email_data = {"email": TestData.TEST_USER_EMAIL_1}

        # Act: パスワードリセットメール送信APIを実行
        response = await client.post(
            "/api/v1/auth/send-password-reset-email",
            json=reset_email_data,
        )

        # Assert: メール送信成功レスポンスを検証（メール送信は無効化済み）
        assert response.status_code == 200
        assert "パスワードリセットメールを送信しました" == response.json()["message"]


# NOTE: ログイン中のAPIのテストを実施する場合はauthenticated_clientを引数に追加して、authenticated_clientからAPIを呼び出す
@pytest.mark.asyncio(loop_scope="session")
async def test_logout_user(authenticated_client: AsyncClient) -> None:
    """POST /api/v1/auth/logout

    【正常系】認証済みユーザーのログアウト処理を行う
    """
    # Arrange: ログアウト用データを準備
    logout_data = {"email": TestData.TEST_USER_EMAIL_1}

    # Act: ログアウトAPIを実行
    response = await authenticated_client.post(
        "/api/v1/auth/logout",
        json=logout_data,
    )

    # Assert: ログアウト成功レスポンスを検証
    assert response.status_code == 200, response.text
    assert response.json()["message"] == "ログアウトしました"


@pytest.mark.asyncio(loop_scope="session")
async def test_register_with_invalid_token() -> None:
    """POST /api/v1/auth/signup

    【異常系】無効なJWTトークンでユーザー登録を試みる
    """
    # Arrange: 無効なトークンとクライアントを準備
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost:8000") as client:
        invalid_token = "invalid.jwt.token"
        invalid_payload = {"token": invalid_token}
        headers = {"Content-Type": "application/json"}

        # Act: 無効なトークンでユーザー登録を試行
        response = await client.post(
            "/api/v1/auth/signup",
            json=invalid_payload,
            headers=headers,
        )

        # Assert: 無効トークンエラーレスポンスを検証
        assert response.status_code == 400, response.text


@pytest.mark.asyncio(loop_scope="session")
async def test_reset_password_with_invalid_email() -> None:
    """POST /api/v1/auth/send-password-reset-email

    【異常系】存在しないメールアドレスでパスワードリセットメール送信を試みる
    """
    # Arrange: 存在しないメールアドレスとクライアントを準備
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost:8000") as client:
        nonexistent_email_data = {"email": "nonexistent@example.com"}

        # Act: 存在しないメールアドレスでリセットメール送信を試行
        response = await client.post(
            "/api/v1/auth/send-password-reset-email",
            json=nonexistent_email_data,
        )

        # Assert: ユーザー未発見エラーレスポンスを検証
        assert response.status_code == 404, response.text
        response_json = response.json()
        assert response_json["success"] is False
        assert "指定されたメールアドレスのユーザーが見つかりません" in response_json["message"]


@pytest.mark.asyncio(loop_scope="session")
async def test_reset_password_with_invalid_token(authenticated_client: AsyncClient) -> None:
    """POST /api/v1/auth/reset-password

    【異常系】無効なJWTトークンでパスワードリセットを試みる
    """
    # Arrange: 無効なトークンとパスワードリセットデータを準備
    new_password = "newpassword123!"
    invalid_reset_payload = {"token": "invalid_token", "new_password": new_password}
    headers = {"Content-Type": "application/json"}

    # Act: 無効なトークンでパスワードリセットを試行
    response = await authenticated_client.post(
        "/api/v1/auth/reset-password",
        json=invalid_reset_payload,
        headers=headers,
    )

    # Assert: 無効トークンエラーレスポンスを検証
    assert response.status_code == 400, response.text


@pytest.mark.asyncio(loop_scope="session")
async def test_logout_with_invalid_token() -> None:
    """POST /api/v1/auth/logout

    【異常系】無効なAuthorizationヘッダーでログアウトを試みる
    """
    # Arrange: 無効な認証ヘッダーとクライアントを準備
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost:8000") as client:
        invalid_headers = {"Authorization": "Bearer invalid_token"}

        # Act: 無効な認証情報でログアウトを試行
        response = await client.post(
            "/api/v1/auth/logout",
            headers=invalid_headers,
        )

        # Assert: 認証エラーレスポンスを検証
        assert response.status_code == 401, response.text


@pytest.mark.asyncio(loop_scope="session")
async def test_logout_without_authentication() -> None:
    """POST /api/v1/auth/logout

    【異常系】認証情報なしでログアウトを試みる
    """
    # Arrange: 認証情報なしのクライアントを準備
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost:8000") as client:
        # Act: 認証情報なしでログアウトを試行
        response = await client.post("/api/v1/auth/logout")

        # Assert: 認証エラーレスポンスを検証
        assert response.status_code == 401, response.text


# =============================================================================
# 追加テストケース - 各種ユーザー状態とJWT有効期限のテスト
# =============================================================================


@pytest.mark.asyncio(loop_scope="session")
async def test_register_user_already_exists() -> None:
    """POST /api/v1/auth/signup

    【異常系】既にアクティブなユーザーが存在するメールアドレスで登録を試みる
    """
    # Arrange: 既存ユーザーと重複するメールアドレスのテストデータを準備
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost:8000") as client:
        await client.post("/api/v1/dev/clear_data")
        await client.post("/api/v1/dev/seed_data")

        duplicate_user_data = {
            "email": TestData.TEST_USER_EMAIL_1,  # 既に存在するメールアドレス
            "username": "newusername",
            "password": "newpassword123!",
        }
        token = create_access_token(data=duplicate_user_data, expires_delta=timedelta(minutes=60))
        signup_payload = {"token": token}
        headers = {"Content-Type": "application/json"}

        # Act: 重複メールアドレスでユーザー登録を試行
        response = await client.post(
            "/api/v1/auth/signup",
            json=signup_payload,
            headers=headers,
        )

        # Assert: 重複エラーレスポンスを検証
        assert response.status_code == 409, response.text
        response_json = response.json()
        assert response_json["success"] is False
        assert "このメールアドレスは既に使用されています" in response_json["message"]


@pytest.mark.asyncio(loop_scope="session")
async def test_register_user_with_deleted_user() -> None:
    """POST /api/v1/auth/signup

    【正常系】論理削除済みユーザーと同じメールアドレスでユーザー登録を行う（復活機能テスト）
    """
    # Arrange: 論理削除済みユーザーアカウントと復活用データを準備
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost:8000") as client:
        await client.post("/api/v1/dev/clear_data")
        await client.post("/api/v1/dev/seed_data")

        # 既存ユーザーでログインしてアカウント削除
        await setup_authenticated_client_with_manual_token(client, TestData.TEST_USER_EMAIL_1, TestData.TEST_USER_PASSWORD)
        delete_response = await client.delete("/api/v1/auth/me")
        assert delete_response.status_code == 200

        # 復活用の新しいユーザーデータ
        restored_user_data = {
            "email": TestData.TEST_USER_EMAIL_1,
            "username": "restored_user",
            "password": "restoredpassword123!",
        }
        token = create_access_token(data=restored_user_data, expires_delta=timedelta(minutes=60))
        signup_payload = {"token": token}
        headers = {"Content-Type": "application/json"}

        # Act: 論理削除されたユーザーのメールアドレスで再登録を実行
        response = await client.post(
            "/api/v1/auth/signup",
            json=signup_payload,
            headers=headers,
        )

        # Assert: ユーザー復活成功レスポンスを検証
        assert response.status_code == 200, response.text
        response_json = response.json()
        assert response_json["success"] is True
        assert "ユーザー登録が完了しました" in response_json["message"]
        assert response_json["data"]["email"] == TestData.TEST_USER_EMAIL_1
        assert response_json["data"]["username"] == "restored_user"


@pytest.mark.asyncio(loop_scope="session")
async def test_register_user_with_expired_jwt() -> None:
    """POST /api/v1/auth/signup

    【異常系】有効期限切れJWTトークンでユーザー登録を試みる
    """
    # Arrange: 期限切れトークンとユーザーデータを準備
    import uuid

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost:8000") as client:
        user_data = {
            "email": f"test_{uuid.uuid4().hex[:8]}@example.com",
            "username": f"test_{uuid.uuid4().hex[:6]}",
            "password": "password123!",
        }
        expired_token = create_access_token(data=user_data, expires_delta=timedelta(seconds=-1))
        expired_payload = {"token": expired_token}
        headers = {"Content-Type": "application/json"}

        # Act: 期限切れトークンでユーザー登録を試行
        response = await client.post(
            "/api/v1/auth/signup",
            json=expired_payload,
            headers=headers,
        )

        # Assert: 期限切れトークンエラーレスポンスを検証
        assert response.status_code == 400, response.text
        response_json = response.json()
        assert response_json["success"] is False
        assert "無効な認証トークンです" in response_json["message"]


@pytest.mark.asyncio(loop_scope="session")
async def test_password_reset_with_deleted_user() -> None:
    """POST /api/v1/auth/send-password-reset-email

    【異常系】論理削除済みユーザーでパスワードリセットメール送信を試みる
    """
    # Arrange: 論理削除済みユーザーアカウントを準備
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost:8000") as client:
        await client.post("/api/v1/dev/clear_data")
        await client.post("/api/v1/dev/seed_data")

        # 既存ユーザーでログインしてアカウント削除
        await setup_authenticated_client_with_manual_token(client, TestData.TEST_USER_EMAIL_1, TestData.TEST_USER_PASSWORD)
        delete_response = await client.delete("/api/v1/auth/me")
        assert delete_response.status_code == 200

        deleted_user_email_data = {"email": TestData.TEST_USER_EMAIL_1}

        # Act: 論理削除済みユーザーでパスワードリセットメール送信を試行
        response = await client.post(
            "/api/v1/auth/send-password-reset-email",
            json=deleted_user_email_data,
        )

        # Assert: ユーザー未発見エラーレスポンスを検証
        assert response.status_code == 404, response.text
        response_json = response.json()
        assert response_json["success"] is False
        assert "指定されたメールアドレスのユーザーが見つかりません" in response_json["message"]


@pytest.mark.asyncio(loop_scope="session")
async def test_password_reset_with_expired_jwt() -> None:
    """POST /api/v1/auth/reset-password

    【異常系】有効期限切れJWTトークンでパスワードリセットを試みる
    """
    # Arrange: 期限切れリセットトークンとテストデータを準備
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost:8000") as client:
        await client.post("/api/v1/dev/clear_data")
        await client.post("/api/v1/dev/seed_data")

        expired_token = create_access_token(data={"email": TestData.TEST_USER_EMAIL_1}, expires_delta=timedelta(seconds=-1))
        expired_reset_payload = {"token": expired_token, "new_password": "newpassword123!"}
        headers = {"Content-Type": "application/json"}

        # Act: 期限切れトークンでパスワードリセットを試行
        response = await client.post(
            "/api/v1/auth/reset-password",
            json=expired_reset_payload,
            headers=headers,
        )

        # Assert: 期限切れトークンエラーレスポンスを検証
        assert response.status_code == 400, response.text
        response_json = response.json()
        assert response_json["success"] is False
        assert "無効なリセットトークンです" in response_json["message"]


@pytest.mark.asyncio(loop_scope="session")
async def test_authentication_with_deleted_user() -> None:
    """POST /api/v1/auth/login

    【異常系】論理削除済みユーザーでログインを試みる
    """
    # Arrange: 論理削除済みユーザーアカウントを準備
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost:8000") as client:
        await client.post("/api/v1/dev/clear_data")
        await client.post("/api/v1/dev/seed_data")

        # 既存ユーザーでログインしてアカウント削除
        await setup_authenticated_client_with_manual_token(client, TestData.TEST_USER_EMAIL_1, TestData.TEST_USER_PASSWORD)
        delete_response = await client.delete("/api/v1/auth/me")
        assert delete_response.status_code == 200

        deleted_login_data = {"username": TestData.TEST_USER_EMAIL_1, "password": TestData.TEST_USER_PASSWORD}
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        # Act: 論理削除済みユーザーでログインを試行
        login_deleted_response = await client.post(
            "/api/v1/auth/login",
            data=deleted_login_data,
            headers=headers,
        )

        # Assert: 認証拒否エラーレスポンスを検証
        assert login_deleted_response.status_code == 401, login_deleted_response.text
        response_json = login_deleted_response.json()
        assert response_json["success"] is False
        assert "メールアドレスまたはパスワードが無効です" in response_json["message"]


@pytest.mark.asyncio(loop_scope="session")
async def test_user_operations_with_expired_jwt() -> None:
    """POST /api/v1/auth/me, PATCH /api/v1/auth/me, POST /api/v1/auth/logout

    【異常系】有効期限切れJWTで各種ユーザー操作を試みる
    """
    # Arrange: 期限切れトークンとテストデータを準備
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost:8000") as client:
        await client.post("/api/v1/dev/clear_data")
        await client.post("/api/v1/dev/seed_data")

        expired_token = create_access_token(data={"sub": TestData.TEST_USER_EMAIL_1, "client_ip": "127.0.0.1"}, expires_delta=timedelta(seconds=-1))
        client.cookies.set("authToken", expired_token)
        update_data = {"username": "updated_name"}

        # Act & Assert: 期限切れトークンでユーザー情報取得を試行
        response = await client.post("/api/v1/auth/me")
        assert response.status_code == 401, response.text

        # Act & Assert: 期限切れトークンでユーザー情報更新を試行
        update_response = await client.patch(
            "/api/v1/auth/me",
            json=update_data,
        )
        assert update_response.status_code == 401, update_response.text

        # Act & Assert: 期限切れトークンでログアウトを試行
        logout_response = await client.post("/api/v1/auth/logout")
        assert logout_response.status_code == 401, logout_response.text


@pytest.mark.asyncio(loop_scope="session")
async def test_update_user_info_with_deleted_user() -> None:
    """PATCH /api/v1/auth/me

    【異常系】論理削除済みユーザーでユーザー情報更新を試みる
    """
    # Arrange: 論理削除済みユーザーアカウントを準備
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost:8000") as client:
        await client.post("/api/v1/dev/clear_data")
        await client.post("/api/v1/dev/seed_data")

        # 既存ユーザーでログインしてアカウント削除
        await setup_authenticated_client_with_manual_token(client, TestData.TEST_USER_EMAIL_1, TestData.TEST_USER_PASSWORD)
        delete_response = await client.delete("/api/v1/auth/me")
        assert delete_response.status_code == 200

        update_data = {"username": "updated_deleted_user"}

        # Act: 論理削除済みユーザーでユーザー情報更新を試行
        update_response = await client.patch(
            "/api/v1/auth/me",
            json=update_data,
        )

        # Assert: 認証拒否エラーレスポンスを検証
        assert update_response.status_code == 401, update_response.text
        response_json = update_response.json()
        assert response_json["success"] is False
        assert "認証情報が無効です" in response_json["message"]
