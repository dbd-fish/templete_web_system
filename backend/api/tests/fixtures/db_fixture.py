from collections.abc import AsyncGenerator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from api.common.database import Base, configure_database, get_db
from main import app


@pytest_asyncio.fixture(scope="function")
async def clean_test_db():
    """クリーンなテスト用データベースフィクスチャ。
    各テスト実行時にテーブルをクリアし、シードデータを挿入、テスト終了後にテーブルをクリアする。
    PostgreSQLテストDBを使用するため、型の互換性問題を回避。
    """
    print("クリーンテストDBの作成を開始")
    
    # テスト用データベースの設定
    db_config = configure_database(test_env=1)
    AsyncSessionLocal = db_config["sessionmaker"]
    engine = db_config["engine"]
    
    # get_dbのオーバーライド関数を定義
    async def override_get_db() -> AsyncGenerator:
        async with AsyncSessionLocal(bind=engine) as session:
            yield session

    # 依存関係をオーバーライド
    app.dependency_overrides[get_db] = override_get_db
    
    # テーブルをクリア
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        print("テーブルをクリア・再作成しました")
    
    # シードデータの挿入（共通関数を使用）
    try:
        from api.v1.features.feature_dev.seed_user import seed_user
        async with AsyncSessionLocal(bind=engine) as session:
            await seed_user(session)
            await session.commit()
        print("シードデータの挿入完了（共通関数使用）")
    except Exception as e:
        print(f"シードデータ挿入中にエラー: {e}")
    
    print("クリーンテストDBのセットアップ完了")
    
    yield {"override_get_db": override_get_db, "engine": engine}
    
    # テスト終了時のクリーンアップ
    print("クリーンテストDBのクリーンアップを開始")
    
    # テーブルをクリア
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    # 依存関係のオーバーライドをクリア
    app.dependency_overrides.clear()
    
    print("クリーンテストDBのクリーンアップ完了")


# インメモリDBフィクスチャは削除済み（PostgreSQL統合テスト方式を採用）

@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_basic_test_env():
    """基本的なテスト環境をセットアップするフィクスチャ（セッション全体で一度だけ実行）。
    """
    print("基本テスト環境のセットアップを開始（セッション全体）")
    
    # 依存関係のオーバーライドは各テストで必要に応じて実行
    yield
    
    # セッション終了時のクリーンアップ
    app.dependency_overrides.clear()

# @pytest_asyncio.fixture(scope="function")
# async def db_session() -> AsyncGenerator[AsyncSession, None]:
#     """
#     テスト用のデータベースセッションを提供するフィクスチャ。
#     """
#     async for session in get_db():
#     yield session
#     await session.close()