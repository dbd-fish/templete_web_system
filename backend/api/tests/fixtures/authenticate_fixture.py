from collections.abc import AsyncGenerator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from passlib.context import CryptContext

from api.common.test_data import TestData
from api.v1.features.feature_auth.crud import get_current_user
from api.v1.features.feature_auth.models.user import User
from main import app


@pytest_asyncio.fixture(scope="function")
async def authenticated_client() -> AsyncGenerator[AsyncClient, None]:
    """認証済みのクライアントを提供するフィクスチャ。

    依存性注入でget_current_userをオーバーライドし、モックユーザーを提供します。
    通常の認証テストに使用してください。
    """
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    # テスト用モックユーザーを作成
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
