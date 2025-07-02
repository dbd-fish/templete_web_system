

from datetime import timedelta

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select

from app.common.test_data import TestData
from app.features.feature_auth.security import create_access_token, verify_password
from app.models.user import User
from main import app

# NOTE: setup_test_dbはfixture(scope="function", autouse=True)だが、戻り値を利用する場合はテスト関数の引数として実装する必要あり。


@pytest.mark.asyncio(loop_scope="session")
async def test_login_user() -> None:
    """ログイン処理のテスト。
    """
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost:8000/") as client:
        response = await client.post(
            "/api/auth/login",
            data={"username": TestData.TEST_USER_EMAIL_1, "password": TestData.TEST_USER_PASSWORD},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert response.status_code == 200
        response_json = response.json()
        message = response_json.get("message", "")
        assert "successful" in message

@pytest.mark.asyncio(loop_scope="session")
async def test_login_with_invalid_credentials() -> None:
    """誤った資格情報でログインを試みた場合のテスト。
    """
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost:8000/") as client:
        response = await client.post(
            "/api/auth/login",
            data={"username": "wronguser@example.com", "password": "wrongpassword"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert response.status_code == 401
        assert "Invalid email or password" in response.json()["detail"]



@pytest.mark.asyncio(loop_scope="session")
async def test_register_user(setup_test_db) -> None:
    """ユーザー登録のテスト (DBの内容を確認)"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost:8000") as client:
        # 仮登録用のユーザー情報
        user_data = {
            "email": "registuser@example.com",
            "username": "registuser",
            "password": "password123!",  # 必要なパスワード要件を満たす
        }

        # **オーバーライドした `get_db()` から DB 操作を行う**
        override_get_db = setup_test_db["override_get_db"]

        # **登録前に `user` テーブルに対象のユーザーが存在しないことを確認**
        async for db_session in override_get_db():
            result = await db_session.execute(select(User).where(User.email == user_data["email"]))
            user_before: User | None = result.scalars().first()
            assert user_before is None, "登録前にユーザーが既に存在しています"

        # **仮登録用JWTトークンを生成**
        token = create_access_token(data=user_data, expires_delta=timedelta(minutes=60))

        # **トークンを `/api/auth/signup` に送信**
        response = await client.post(
            "/api/auth/signup",
            json={"token": token},
            headers={"Content-Type": "application/json"},
        )
        assert response.status_code == 200, response.text  # エラーメッセージ

        # **登録後に `user` テーブルに対象のユーザーが登録されていることを確認**
        async for db_session in override_get_db():
            result = await db_session.execute(select(User).where(User.email == user_data["email"]))
            user_after: User | None = result.scalars().first()
            assert user_after is not None, "ユーザー登録が成功していません"
            assert user_after.email == user_data["email"]
            assert user_after.username == user_data["username"]

@pytest.mark.asyncio(loop_scope="session")
async def test_reset_password(authenticated_client: AsyncClient, setup_test_db) -> None:
    """パスワードリセットのテスト (DBからパスワード変更を確認)"""
    new_password = TestData.TEST_USER_PASSWORD + "123"

    # NOTE: オーバーライドした `get_db()` から DB 操作を行う
    override_get_db = setup_test_db["override_get_db"]

    # **パスワード変更前の `password` を取得**
    async for db_session in override_get_db():
        result = await db_session.execute(select(User).where(User.email == TestData.TEST_USER_EMAIL_1))
        user_before: User | None = result.scalars().first()
        assert user_before is not None, "ユーザーが存在しません"
        old_hashed_password = user_before.hashed_password

    # **パスワードリセット用JWTトークンを生成**
    token = create_access_token(data={"email": TestData.TEST_USER_EMAIL_1}, expires_delta=timedelta(minutes=60))

    # トークンが取得できているか確認
    assert token is not None, "Reset token is missing in the response"

    # 取得したトークンを使ってパスワードを変更
    response = await authenticated_client.post(
        "/api/auth/reset-password",
        json={"token": token, "new_password": new_password},
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 200, response.text  # エラーメッセージを出力

    # **パスワード変更後の `password` を取得**
    async for db_session in override_get_db():
        result = await db_session.execute(select(User).where(User.email == TestData.TEST_USER_EMAIL_1))
        user_after: User | None = result.scalars().first()
        assert user_after is not None, "ユーザーが存在しません"
        new_hashed_password = user_after.hashed_password

    # **パスワードが変更されていることを確認**
    assert old_hashed_password != new_hashed_password, "パスワードが変更されていません"

    # **新しいパスワードが正しく適用されているか確認**
    assert verify_password(new_password, new_hashed_password), "新しいパスワードが正しく設定されていません"

@pytest.mark.asyncio(loop_scope="session")
async def test_send_verify_email() -> None:
    """仮登録用メール送信のテスト"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost:8000") as client:
        response = await client.post(
            "/api/auth/send-verify-email",
            json={"email": "newuser@example.com", "username": "newuser", "password": "Test1234!"},
        )
        assert response.status_code == 200
        assert "User created successfully" in response.json()["msg"]

@pytest.mark.asyncio(loop_scope="session")
async def test_send_reset_password_email() -> None:
    """パスワードリセットメール送信のテスト"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost:8000") as client:
        response = await client.post(
            "/api/auth/send-password-reset-email",
            json={"email": TestData.TEST_USER_EMAIL_1},
        )
        assert response.status_code == 200
        assert "Password reset email send successful" in response.json()["msg"]

# NOTE: ログイン中のAPIのテストを実施する場合はauthenticated_clientを引数に追加して、authenticated_clientからAPIを呼び出す
@pytest.mark.asyncio(loop_scope="session")
async def test_logout_user(authenticated_client: AsyncClient) -> None:
    """ログアウト処理のテスト"""

    response = await authenticated_client.post(
        "/api/auth/logout",
        json={"email": TestData.TEST_USER_EMAIL_1},
    )

    assert response.status_code == 200, response.text
    assert response.json()["msg"] == "Logged out successfully"



@pytest.mark.asyncio(loop_scope="session")
async def test_register_existing_user(setup_test_db) -> None:
    """既に登録されているユーザーで仮登録を試みる（異常系）"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost:8000") as client:
        user_data = {
            "email": TestData.TEST_USER_EMAIL_1,
            "username": "testuser",
            "password": "password123!",
        }

        token = create_access_token(data=user_data, expires_delta=timedelta(minutes=60))

        response = await client.post(
            "/api/auth/signup",
            json={"token": token},
            headers={"Content-Type": "application/json"},
        )
        assert response.status_code == 400, response.text
        assert "User already exists" in response.json()["detail"]


@pytest.mark.asyncio(loop_scope="session")
async def test_register_with_invalid_token() -> None:
    """無効なトークンでユーザー登録を試みる（異常系）"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost:8000") as client:
        invalid_token = "invalid.jwt.token"

        response = await client.post(
            "/api/auth/signup",
            json={"token": invalid_token},
            headers={"Content-Type": "application/json"},
        )
        assert response.status_code == 401, response.text


@pytest.mark.asyncio(loop_scope="session")
async def test_reset_password_with_invalid_email() -> None:
    """存在しないメールアドレスでパスワードリセット（異常系）"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost:8000") as client:
        response = await client.post(
            "/api/auth/send-password-reset-email",
            json={"email": "nonexistent@example.com"},
        )
        assert response.status_code == 400, response.text


@pytest.mark.asyncio(loop_scope="session")
async def test_reset_password_with_invalid_token(authenticated_client: AsyncClient) -> None:
    """無効なトークンでパスワードリセット（異常系）"""
    new_password = "newpassword123!"

    response = await authenticated_client.post(
        "/api/auth/reset-password",
        json={"token": "invalid_token", "new_password": new_password},
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 401, response.text


@pytest.mark.asyncio(loop_scope="session")
async def test_logout_with_invalid_token() -> None:
    """誤ったトークンでログアウトを試みる（異常系）"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost:8000") as client:
        response = await client.post(
            "/api/auth/logout",
            headers={"Authorization": "Bearer invalid_token"},
        )
        assert response.status_code == 401, response.text


@pytest.mark.asyncio(loop_scope="session")
async def test_logout_without_authentication() -> None:
    """認証なしでログアウトを試みる（異常系）"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost:8000") as client:
        response = await client.post("/api/auth/logout")
        assert response.status_code == 401, response.text
