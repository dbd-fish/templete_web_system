from collections.abc import AsyncGenerator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from passlib.context import CryptContext

from app.common.test_data import TestData
from app.features.feature_auth.auth_service import get_current_user
from app.models.user import User
from main import app


@pytest_asyncio.fixture(scope="function")
def login_user_data() -> User:
    """テスト用のログイン中ユーザーデータ。
    NOTE: 本来はJWTトークンからユーザー情報を復元するべきだが、テスト対象の処理が狭めるため、本メソッドからログイン情報を取得する。
    """
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    return User(
        user_id=TestData.TEST_USER_ID_1,
        email=TestData.TEST_USER_EMAIL_1,
        username=TestData.TEST_USERNAME_1,
        hashed_password=pwd_context.hash(TestData.TEST_USER_PASSWORD),
        user_role=User.ROLE_FREE,
        user_status=User.STATUS_ACTIVE,
    )


@pytest_asyncio.fixture(scope="function")
async def authenticated_client() -> AsyncGenerator[AsyncClient, None]:
    """認証済みのクライアントを提供するフィクスチャ。
    """
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    # モックユーザーを定義
    mock_user = User(
        user_id=TestData.TEST_USER_ID_1,
        email=TestData.TEST_USER_EMAIL_1,
        username=TestData.TEST_USERNAME_1,
        hashed_password=pwd_context.hash(TestData.TEST_USER_PASSWORD),
        user_role=User.ROLE_FREE,
        user_status=User.STATUS_ACTIVE,
    )

    # get_current_userのオーバーライド関数を定義
    async def override_get_current_user() -> User:
        return mock_user

    # 依存関係をオーバーライド
    app.dependency_overrides[get_current_user] = override_get_current_user

    # 認証済みのクライアントを作成
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost:8000/") as client:
        yield client

    # テスト後にオーバーライドをクリア
    app.dependency_overrides.clear()
