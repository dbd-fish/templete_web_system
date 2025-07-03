"""モックベースのテスト用フィクスチャ"""
from unittest.mock import AsyncMock, MagicMock
from collections.abc import AsyncGenerator

import pytest_asyncio

from api.common.test_data import TestData
from api.v1.features.feature_auth.models.user import User
from api.v1.features.feature_auth.security import hash_password
from api.common.database import get_db
from main import app


@pytest_asyncio.fixture(scope="function")
async def mock_db():
    """モックデータベースフィクスチャ。
    実際のデータベースを使用せず、メモリ上でユーザーデータを管理する軽量なフィクスチャ。
    """
    print("モックDBの作成を開始")
    
    # メモリ上のユーザーデータストア
    mock_users = {}
    
    # テストユーザーを作成
    test_user = User(
        user_id=TestData.TEST_USER_ID_1,
        username=TestData.TEST_USERNAME_1,
        email=TestData.TEST_USER_EMAIL_1,
        hashed_password=hash_password(TestData.TEST_USER_PASSWORD),
        user_role=User.ROLE_FREE,
        user_status=User.STATUS_ACTIVE,
    )
    
    mock_users[test_user.email] = test_user
    mock_users[test_user.username] = test_user
    
    # モックセッションの作成
    mock_session = AsyncMock()
    
    # モックの動作を定義
    async def mock_execute(query):
        # ユーザー検索のモック
        mock_result = MagicMock()
        
        # クエリパラメータを解析してユーザーを返す
        if hasattr(query, 'compile'):
            compiled = query.compile(compile_kwargs={"literal_binds": True})
            query_str = str(compiled)
            
            # ログイン用の検索クエリ
            if "user.email = " in query_str or "user.username = " in query_str:
                # 簡単な検索実装
                for identifier, user in mock_users.items():
                    if identifier == TestData.TEST_USER_EMAIL_1:
                        mock_result.scalars.return_value.first.return_value = user
                        return mock_result
                        
        # デフォルトは見つからない
        mock_result.scalars.return_value.first.return_value = None
        return mock_result
    
    mock_session.execute = mock_execute
    mock_session.add = MagicMock()
    mock_session.commit = AsyncMock()
    mock_session.flush = AsyncMock()
    mock_session.rollback = AsyncMock()
    
    # get_dbのオーバーライド関数を定義
    async def override_get_db() -> AsyncGenerator:
        yield mock_session

    # 依存関係をオーバーライド
    app.dependency_overrides[get_db] = override_get_db
    
    print("モックDBのセットアップ完了")
    
    yield {"override_get_db": override_get_db, "mock_session": mock_session, "mock_users": mock_users}
    
    # テスト終了時のクリーンアップ
    print("モックDBのクリーンアップを開始")
    
    # 依存関係のオーバーライドをクリア
    app.dependency_overrides.clear()
    
    print("モックDBのクリーンアップ完了")