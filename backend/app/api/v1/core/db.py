"""
データベース設定（FastAPI公式テンプレート準拠）
"""

from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from app.core.config import settings

# SQLAlchemy基底クラス
Base = declarative_base()

# 非同期エンジンの作成
engine = create_async_engine(
    str(settings.SQLALCHEMY_DATABASE_URI),
    echo=settings.ENVIRONMENT == "local",  # ローカル環境でのみSQLログ出力
    pool_pre_ping=True,
)

# セッションファクトリーの作成
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    データベースセッションの依存性注入用ジェネレーター
    
    Yields:
        AsyncSession: データベースセッション
    """
    async with AsyncSessionLocal() as session:
        yield session