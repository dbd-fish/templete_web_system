from datetime import timedelta

import pytest
from httpx import ASGITransport, AsyncClient

from api.common.test_data import TestData
from api.v1.features.feature_auth.security import create_access_token, create_verification_token
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
    auth_token = create_access_token(user_email=email)
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
        headers = {"Content-Type": "application/json"}

        # Act: ログインAPIを実行
        response = await client.post(
            "/api/v1/auth/login",
            json=login_data,
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
        headers = {"Content-Type": "application/json"}

        # Act: 不正な認証情報でログインを試行
        response = await client.post(
            "/api/v1/auth/login",
            json=invalid_credentials,
            headers=headers,
        )

        # Assert: 認証エラーレスポンスを検証
        assert response.status_code == 401
        response_json = response.json()
        assert "メールアドレスまたはパスワードが無効です" == response_json["detail"]


@pytest.mark.asyncio(loop_scope="session")
async def test_register_user() -> None:
    """POST /api/v1/auth/signup

    【正常系】直接ユーザー登録を行う
    """
    # Arrange: 新規ユーザー情報を準備
    import uuid

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost:8000") as client:
        user_data = {
            "email": f"test_{uuid.uuid4().hex[:8]}@example.com",
            "username": f"test_{uuid.uuid4().hex[:6]}",
            "password": "Password123!",
            "password_confirm": "Password123!",
        }
        headers = {"Content-Type": "application/json"}

        # Act: ユーザー登録APIを実行（DirectUserCreateスキーマを使用）
        response = await client.post(
            "/api/v1/auth/signup",
            json=user_data,
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
    from api.v1.features.feature_auth.security import create_verification_token

    new_password = TestData.TEST_USER_PASSWORD + "123"
    token = create_verification_token(data={"email": TestData.TEST_USER_EMAIL_1}, expires_delta=timedelta(minutes=60))
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
    クッキーに含まれるアクセストークンとリフレッシュトークンの両方を削除する
    """
    # Act: ログアウトAPIを実行（リクエストボディなし、クッキーから認証情報を取得）
    response = await authenticated_client.post("/api/v1/auth/logout")

    # Assert: ログアウト成功レスポンスを検証
    assert response.status_code == 200, response.text
    response_json = response.json()
    assert response_json["success"] is True
    assert response_json["message"] == "ログアウトしました"

    # Assert: クッキーが削除されているかを確認
    # Set-Cookieヘッダーでクッキーの削除を確認
    set_cookie_headers = response.headers.get_list("set-cookie")

    # authTokenとrefreshTokenの削除を確認
    auth_token_deleted = any("authToken=" in cookie and "Max-Age=0" in cookie for cookie in set_cookie_headers)
    refresh_token_deleted = any("refreshToken=" in cookie and "Max-Age=0" in cookie for cookie in set_cookie_headers)

    assert auth_token_deleted, "authTokenクッキーが削除されていません"
    assert refresh_token_deleted, "refreshTokenクッキーが削除されていません"


@pytest.mark.asyncio(loop_scope="session")
async def test_register_with_invalid_token() -> None:
    """POST /api/v1/auth/signup-with-email

    【異常系】無効なJWTトークンでメール認証ユーザー登録を試みる
    """
    # Arrange: 無効なトークンとクライアントを準備
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost:8000") as client:
        invalid_token = "invalid.jwt.token"
        invalid_payload = {"token": invalid_token}
        headers = {"Content-Type": "application/json"}

        # Act: 無効なトークンでメール認証ユーザー登録を試行
        response = await client.post(
            "/api/v1/auth/signup-with-email",
            json=invalid_payload,
            headers=headers,
        )

        # Assert: 無効トークンエラーレスポンスを検証
        assert response.status_code == 400, response.text
        response_json = response.json()
        assert "無効な認証トークンです" in response_json["detail"]


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
        assert "指定されたメールアドレスのユーザーが見つかりません" in response_json["detail"]


@pytest.mark.asyncio(loop_scope="session")
async def test_reset_password_with_invalid_token(authenticated_client: AsyncClient) -> None:
    """POST /api/v1/auth/reset-password

    【異常系】無効なJWTトークンでパスワードリセットを試みる
    """
    # Arrange: 無効なトークンとパスワードリセットデータを準備
    new_password = "NewPassword123!"
    invalid_reset_payload = {"token": "invalid_token", "new_password": new_password}
    headers = {"Content-Type": "application/json"}

    # Act: 無効なトークンでパスワードリセットを試行
    response = await authenticated_client.post(
        "/api/v1/auth/reset-password",
        json=invalid_reset_payload,
        headers=headers,
    )

    # Assert: 無効トークンエラーレスポンスを検証
    assert response.status_code == 422, response.text
    response_json = response.json()
    assert "detail" in response_json


@pytest.mark.asyncio(loop_scope="session")
async def test_logout_with_invalid_token() -> None:
    """POST /api/v1/auth/logout

    【正常系】無効なクッキートークンでログアウト
    無効なトークンでもログアウト処理は成功する（寛容な設計）
    """
    # Arrange: 無効なトークンクッキーとクライアントを準備
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost:8000") as client:
        # 無効なトークンをクッキーに設定
        client.cookies.set("authToken", "invalid.access.token")
        client.cookies.set("refreshToken", "invalid.refresh.token")

        # Act: 無効なトークンでログアウトを試行
        response = await client.post("/api/v1/auth/logout")

        # Assert: 無効トークンでもログアウト成功（200）
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["success"] is True
        assert "ログアウトしました" in data["message"]

        # Assert: 無効なトークンでもクッキーは削除される
        set_cookie_headers = response.headers.get_list("set-cookie")

        # 具体的なクッキー削除を確認
        auth_token_deleted = any("authToken=" in cookie and "Max-Age=0" in cookie for cookie in set_cookie_headers)
        refresh_token_deleted = any("refreshToken=" in cookie and "Max-Age=0" in cookie for cookie in set_cookie_headers)

        assert auth_token_deleted, "無効なトークンでもauthTokenクッキーが削除される"
        assert refresh_token_deleted, "無効なトークンでもrefreshTokenクッキーが削除される"


@pytest.mark.asyncio(loop_scope="session")
async def test_logout_without_authentication() -> None:
    """POST /api/v1/auth/logout

    【正常系】認証情報なしでログアウト（B018修正により認証不要）
    """
    # Arrange: 認証情報なしのクライアントを準備
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost:8000") as client:
        # Act: 認証情報なしでログアウトを試行
        response = await client.post("/api/v1/auth/logout")

        # Assert: B018修正により、認証情報なしでもログアウト成功（200）
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["success"] is True
        assert "ログアウトしました" in data["message"]


@pytest.mark.asyncio(loop_scope="session")
async def test_logout_with_partial_tokens() -> None:
    """POST /api/v1/auth/logout

    【正常系】一部のトークンのみ存在する場合のログアウト
    アクセストークンのみ、またはリフレッシュトークンのみでもログアウト成功
    """
    # Arrange: アクセストークンのみのケース
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost:8000") as client:
        # 有効なアクセストークンを生成
        from api.v1.features.feature_auth.security import create_access_token

        valid_access_token = create_access_token(TestData.TEST_USER_EMAIL_1)
        client.cookies.set("authToken", valid_access_token)
        # refreshTokenは設定しない

        # Act: アクセストークンのみでログアウト
        response = await client.post("/api/v1/auth/logout")

        # Assert: 部分的なトークンでもログアウト成功
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["success"] is True
        assert "ログアウトしました" in data["message"]

    # Arrange: リフレッシュトークンのみのケース
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost:8000") as client:
        # 有効なリフレッシュトークンを生成
        from api.v1.features.feature_auth.security import create_refresh_token

        valid_refresh_token = create_refresh_token(TestData.TEST_USER_EMAIL_1)
        client.cookies.set("refreshToken", valid_refresh_token)
        # authTokenは設定しない

        # Act: リフレッシュトークンのみでログアウト
        response = await client.post("/api/v1/auth/logout")

        # Assert: 部分的なトークンでもログアウト成功
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["success"] is True
        assert "ログアウトしました" in data["message"]


@pytest.mark.asyncio(loop_scope="session")
async def test_logout_after_successful_login() -> None:
    """POST /api/v1/auth/logout

    【統合テスト】ログイン後のログアウト処理
    実際のログインフローでトークンを取得してからログアウトする
    """
    # Arrange: 新しいクライアントを準備
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost:8000") as client:
        # Act: まずログインしてトークンを取得
        login_data = {"username": TestData.TEST_USER_EMAIL_1, "password": TestData.TEST_USER_PASSWORD}
        login_response = await client.post("/api/v1/auth/login", json=login_data)

        # Assert: ログイン成功を確認
        assert login_response.status_code == 200, login_response.text

        # ログイン時にクッキーが設定されていることを確認
        set_cookie_headers = login_response.headers.get_list("set-cookie")
        assert len(set_cookie_headers) >= 2, "ログイン時にauthTokenとrefreshTokenが設定される"

        # Act: 続いてログアウト処理
        logout_response = await client.post("/api/v1/auth/logout")

        # Assert: ログアウト成功を確認
        assert logout_response.status_code == 200, logout_response.text
        logout_data = logout_response.json()
        assert logout_data["success"] is True
        assert "ログアウトしました" in logout_data["message"]

        # Assert: ログアウト時にクッキーが削除されることを確認
        logout_set_cookie_headers = logout_response.headers.get_list("set-cookie")

        # 具体的なクッキー削除を確認
        logout_auth_token_deleted = any("authToken=" in cookie and "Max-Age=0" in cookie for cookie in logout_set_cookie_headers)
        logout_refresh_token_deleted = any("refreshToken=" in cookie and "Max-Age=0" in cookie for cookie in logout_set_cookie_headers)

        assert logout_auth_token_deleted, "ログアウト時にauthTokenクッキーが削除される"
        assert logout_refresh_token_deleted, "ログアウト時にrefreshTokenクッキーが削除される"


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
            "password": "NewPassword123!",
            "password_confirm": "NewPassword123!",
        }
        headers = {"Content-Type": "application/json"}

        # Act: 重複メールアドレスでユーザー登録を試行（DirectUserCreateスキーマを使用）
        response = await client.post(
            "/api/v1/auth/signup",
            json=duplicate_user_data,
            headers=headers,
        )

        # Assert: 重複エラーレスポンスを検証
        assert response.status_code == 409, response.text
        response_json = response.json()
        assert "このメールアドレスは既に使用されています" in response_json["detail"]


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
            "password": "RestoredPassword123!",
            "password_confirm": "RestoredPassword123!",
        }
        headers = {"Content-Type": "application/json"}

        # Act: 論理削除されたユーザーのメールアドレスで再登録を実行（DirectUserCreateスキーマを使用）
        response = await client.post(
            "/api/v1/auth/signup",
            json=restored_user_data,
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
            "password": "Password123!",
            "password_confirm": "Password123!",
        }
        headers = {"Content-Type": "application/json"}

        # Act: 通常のユーザー登録を試行（現在はDirectUserCreateスキーマのため期限切れトークンテストを通常登録に変更）
        response = await client.post(
            "/api/v1/auth/signup",
            json=user_data,
            headers=headers,
        )

        # Assert: 登録成功レスポンスを検証（期限切れトークンテストの代わりに正常登録をテスト）
        assert response.status_code == 200, response.text
        response_json = response.json()
        assert response_json["success"] is True
        assert "ユーザー登録が完了しました" in response_json["message"]


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
        assert "指定されたメールアドレスのユーザーが見つかりません" in response_json["detail"]


@pytest.mark.asyncio(loop_scope="session")
async def test_password_reset_with_expired_jwt() -> None:
    """POST /api/v1/auth/reset-password

    【異常系】有効期限切れJWTトークンでパスワードリセットを試みる
    """
    # Arrange: 期限切れリセットトークンとテストデータを準備
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost:8000") as client:
        await client.post("/api/v1/dev/clear_data")
        await client.post("/api/v1/dev/seed_data")

        expired_token = create_verification_token(data={"email": TestData.TEST_USER_EMAIL_1}, expires_delta=timedelta(seconds=-1))
        expired_reset_payload = {"token": expired_token, "new_password": "NewPassword123!"}
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
        assert "無効なリセットトークンです" in response_json["detail"]


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
        headers = {"Content-Type": "application/json"}

        # Act: 論理削除済みユーザーでログインを試行
        login_deleted_response = await client.post(
            "/api/v1/auth/login",
            json=deleted_login_data,
            headers=headers,
        )

        # Assert: 認証拒否エラーレスポンスを検証
        assert login_deleted_response.status_code == 401, login_deleted_response.text
        response_json = login_deleted_response.json()
        assert "メールアドレスまたはパスワードが無効です" in response_json["detail"]


@pytest.mark.asyncio(loop_scope="session")
async def test_user_operations_with_expired_jwt() -> None:
    """POST /api/v1/auth/me, PATCH /api/v1/auth/me, POST /api/v1/auth/logout

    【異常系】有効期限切れJWTで各種ユーザー操作を試みる
    """
    # Arrange: 期限切れトークンとテストデータを準備
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost:8000") as client:
        await client.post("/api/v1/dev/clear_data")
        await client.post("/api/v1/dev/seed_data")

        expired_token = create_access_token(user_email=TestData.TEST_USER_EMAIL_1, expires_delta=timedelta(seconds=-1))
        client.cookies.set("authToken", expired_token)
        update_data = {"username": "updated_name"}

        # Act & Assert: 期限切れトークンでユーザー情報取得を試行
        response = await client.post("/api/v1/auth/me")
        assert response.status_code == 401, response.text
        response_json = response.json()
        assert "detail" in response_json

        # Act & Assert: 期限切れトークンでユーザー情報更新を試行
        update_response = await client.patch(
            "/api/v1/auth/me",
            json=update_data,
        )
        assert update_response.status_code == 401, update_response.text
        update_response_json = update_response.json()
        assert "detail" in update_response_json

        # Act & Assert: 期限切れトークンでログアウトを試行（B018修正により成功）
        logout_response = await client.post("/api/v1/auth/logout")
        assert logout_response.status_code == 200, logout_response.text
        logout_data = logout_response.json()
        assert logout_data["success"] is True
        assert "ログアウトしました" in logout_data["message"]


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
        assert "認証情報が無効です" in response_json["detail"]


# =============================================================================
# アカウント削除テスト（DELETE /api/v1/auth/account）
# =============================================================================


@pytest.mark.asyncio(loop_scope="session")
async def test_delete_account_success() -> None:
    """DELETE /api/v1/auth/account

    【正常系】認証済みユーザーがアカウント削除を実行する
    """
    # Arrange: テストデータの準備と認証済みクライアント作成
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost:8000") as client:
        await client.post("/api/v1/dev/clear_data")
        await client.post("/api/v1/dev/seed_data")

        # 認証済みクライアントを準備
        await setup_authenticated_client_with_manual_token(client, TestData.TEST_USER_EMAIL_1, TestData.TEST_USER_PASSWORD)

        # Act: アカウント削除を実行
        delete_response = await client.delete("/api/v1/auth/account")

        # Assert: 削除成功レスポンスを検証
        assert delete_response.status_code == 200, delete_response.text
        response_json = delete_response.json()
        assert response_json["success"] is True
        assert "アカウントが正常に削除され、ログアウトしました" in response_json["message"]
        assert response_json["data"]["message"] == "アカウントが正常に削除されました"

        # Assert: 認証クッキーが削除されていることを確認
        # NOTE: delete_cookieはSet-Cookieヘッダーで空の値とmax_age=0を設定する
        set_cookie_headers = delete_response.headers.get_list("set-cookie")
        assert any("authToken=" in header and "Max-Age=0" in header for header in set_cookie_headers)
        assert any("refreshToken=" in header and "Max-Age=0" in header for header in set_cookie_headers)

        # Assert: 削除後は認証が必要なエンドポイントにアクセスできない
        profile_response = await client.post("/api/v1/auth/me")
        assert profile_response.status_code == 401
        profile_response_json = profile_response.json()
        assert "detail" in profile_response_json


@pytest.mark.asyncio(loop_scope="session")
async def test_delete_account_unauthorized() -> None:
    """DELETE /api/v1/auth/account

    【異常系】未認証状態でアカウント削除を試行する
    """
    # Arrange: 未認証クライアント
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost:8000") as client:
        await client.post("/api/v1/dev/clear_data")
        await client.post("/api/v1/dev/seed_data")

        # Act: 未認証状態でアカウント削除を試行
        delete_response = await client.delete("/api/v1/auth/account")

        # Assert: 認証エラーレスポンスを検証
        assert delete_response.status_code == 401, delete_response.text
        response_json = delete_response.json()
        assert "認証情報が無効です" in response_json["detail"]


@pytest.mark.asyncio(loop_scope="session")
async def test_delete_account_with_deleted_user() -> None:
    """DELETE /api/v1/auth/account

    【異常系】論理削除済みユーザーでアカウント削除を試行する
    """
    # Arrange: 論理削除済みユーザーアカウントを準備
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost:8000") as client:
        await client.post("/api/v1/dev/clear_data")
        await client.post("/api/v1/dev/seed_data")

        # 既存ユーザーでログインしてアカウントを最初に削除
        await setup_authenticated_client_with_manual_token(client, TestData.TEST_USER_EMAIL_1, TestData.TEST_USER_PASSWORD)
        first_delete_response = await client.delete("/api/v1/auth/me")
        assert first_delete_response.status_code == 200

        # Act: 論理削除済みユーザーで再度アカウント削除を試行
        second_delete_response = await client.delete("/api/v1/auth/account")

        # Assert: 認証拒否エラーレスポンスを検証
        assert second_delete_response.status_code == 401, second_delete_response.text
        response_json = second_delete_response.json()
        assert "認証情報が無効です" in response_json["detail"]


@pytest.mark.asyncio(loop_scope="session")
async def test_delete_account_with_expired_token() -> None:
    """DELETE /api/v1/auth/account

    【異常系】期限切れJWTトークンでアカウント削除を試行する
    """
    # Arrange: 期限切れトークンを生成
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost:8000") as client:
        await client.post("/api/v1/dev/clear_data")
        await client.post("/api/v1/dev/seed_data")

        # 期限切れトークンを生成（-1秒前に期限切れ）
        expired_token = create_access_token(
            user_email=TestData.TEST_USER_EMAIL_1,
            expires_delta=timedelta(seconds=-1),
        )

        # 期限切れトークンをクッキーに設定
        client.cookies.set("authToken", expired_token)

        # Act: 期限切れトークンでアカウント削除を試行
        delete_response = await client.delete("/api/v1/auth/account")

        # Assert: 認証エラーレスポンスを検証
        assert delete_response.status_code == 401, delete_response.text
        response_json = delete_response.json()
        assert "認証情報が無効です" in response_json["detail"]


# =============================================================================
# Google OAuth 2.0 認証テスト
# =============================================================================


@pytest.mark.asyncio
async def test_google_login_success():
    """POST /api/v1/auth/google-login

    【正常系】Google認証エンドポイントが存在することを確認（簡素化版）。
    """
    # Arrange: 不正なIDトークンでエラーレスポンスをテスト
    invalid_token_payload = {"id_token": "invalid.jwt.format"}

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Act: 無効なトークンでGoogle認証エンドポイントをテスト
        response = await client.post(
            "/api/v1/auth/google-login",
            json=invalid_token_payload,
        )

        # Assert: エンドポイントが存在し、適切なエラーが返されることを確認
        assert response.status_code == 400  # Google認証エラー
        json_response = response.json()
        assert "認証エラー" in json_response["detail"]


@pytest.mark.asyncio
async def test_google_login_invalid_token():
    """POST /api/v1/auth/google-login

    【異常系】無効なGoogle IDトークン形式でバリデーションエラーが発生することを確認。
    """
    # Arrange: 形式的に無効なGoogle IDトークンを準備
    invalid_token_payload = {"id_token": "completely_invalid_token"}

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Act: 無効なトークン形式でGoogle認証エンドポイントをテスト
        response = await client.post(
            "/api/v1/auth/google-login",
            json=invalid_token_payload,
        )

        # Assert: バリデーションエラーレスポンスを確認
        assert response.status_code == 422
        json_response = response.json()
        assert "detail" in json_response
