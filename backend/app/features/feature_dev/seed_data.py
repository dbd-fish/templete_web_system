
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlalchemy.sql import text

from app.common.database import AsyncSessionLocal, Base
from app.features.feature_dev.seed_user import seed_user


async def clear_data(db: AsyncSession):
    """データベースをクリアします。すべてのテーブルを削除し、再作成します。
    """
        # db.bind の型を明示的にチェック
    if not isinstance(db.bind, AsyncEngine):
        raise TypeError("db.bind is not an AsyncEngine")
    engine: AsyncEngine = db.bind
    async with engine.begin() as conn:

        try:
            print("データベースURL:", engine.url)
            print("すべてのテーブルを削除中...")
            # テーブルを CASCADE で削除
            # スキーマ全体を削除
            await conn.execute(text('DROP SCHEMA public CASCADE'))
            # スキーマを再作成
            await conn.execute(text('CREATE SCHEMA public'))
            print("すべてのテーブルを作成中...")
            await conn.run_sync(Base.metadata.create_all)  # テーブルを作成
            print("データベースのクリアが完了しました。")
        except Exception as e:
            print(f"データベースクリア中にエラーが発生しました: {e}")


async def seed_data(db: AsyncSession):
    """テーブルへデータを挿入します。
    """
    # db.bind の型を明示的にチェック
    if not isinstance(db.bind, AsyncEngine):
        raise TypeError("db.bind is not an AsyncEngine")
    engine: AsyncEngine = db.bind

    async with AsyncSessionLocal(bind=engine) as session:
        try:
            await seed_user(session)

        except Exception as e:
            await session.rollback()
            print(f"An error occurred: {e}")
        finally:
            await session.close()
