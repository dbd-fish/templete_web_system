import asyncio

from passlib.context import CryptContext  # type: ignore
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql import text

import app.models
from app.common.common import datetime_now
from app.common.database import AsyncSessionLocal, Base
from app.common.test_data import TestData

# パスワードハッシュ用のコンテキスト
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def seed_user(session: AsyncSession):
    """ユーザーデータをチェックして存在しなければ挿入します。"""
    try:
        # ユーザーデータを定義
        users = [
            {
                "user_id": TestData.TEST_USER_ID_1,
                "username": TestData.TEST_USERNAME_1,
                "email": TestData.TEST_USER_EMAIL_1,
                "password": TestData.TEST_USER_PASSWORD,
                "contact_number": TestData.TEST_USER_CONTACT_1,
                "user_role": 1,
            },
            {
                "user_id": TestData.TEST_USER_ID_2,
                "username": TestData.TEST_USERNAME_2,
                "email": TestData.TEST_USER_EMAIL_2,
                "password": TestData.TEST_USER_PASSWORD,
                "contact_number": TestData.TEST_USER_CONTACT_2,
                "user_role": 2,
            },
        ]

        # 各ユーザーのデータを処理
        for user_data in users:
            result = await session.execute(
                select(app.models.User).where(app.models.User.username == user_data["username"]),
            )
            if not result.scalars().first():
                new_user = app.models.User(
                    user_id=user_data["user_id"],
                    username=user_data["username"],
                    email=user_data["email"],
                    hashed_password=pwd_context.hash(str(user_data["password"])),
                    contact_number=user_data["contact_number"],
                    user_role=user_data["user_role"],
                    user_status=1,
                    created_at=datetime_now(),
                    updated_at=datetime_now(),
                )
                session.add(new_user)
                print(f"User {user_data['username']} added.")

        await session.commit()
        print("All users seeded successfully!")

    except Exception as e:
        await session.rollback()
        print(f"An error occurred while processing users: {e}")


async def seed_data(db: AsyncSession):
    """テーブルへデータを挿入します。"""
    # db.bind の型を明示的にチェック
    if not isinstance(db.bind, AsyncEngine):
        raise TypeError("db.bind is not an AsyncEngine")
    engine: AsyncEngine = db.bind

    async with AsyncSessionLocal(bind=engine) as session:
        try:
            # ユーザーデータを一括処理
            await seed_data(session)

        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            await session.close()


async def clear_data(db: AsyncSession):
    """データベースをクリアします。すべてのテーブルを削除し、再作成します。"""
    if not isinstance(db.bind, AsyncEngine):
        raise TypeError("db.bind is not an AsyncEngine")
    engine: AsyncEngine = db.bind

    async with engine.begin() as conn:
        try:
            print("データベースURL:", engine.url)
            print("すべてのテーブルを削除中...")
            # テーブルを CASCADE で削除
            await conn.execute(text('DROP SCHEMA public CASCADE'))
            # スキーマを再作成
            await conn.execute(text('CREATE SCHEMA public'))
            print("すべてのテーブルを作成中...")
            await conn.run_sync(Base.metadata.create_all)  # テーブルを作成
            print("データベースのクリアが完了しました。")
        except Exception as e:
            print(f"データベースクリア中にエラーが発生しました: {e}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Seed or clear database.")
    parser.add_argument("--clear", action="store_true", help="Clear all database data")
    parser.add_argument("--seed", action="store_true", help="Seed the database with initial data")
    args = parser.parse_args()

    async def main():
        if args.clear:
            print("Clearing database...")
            async with AsyncSessionLocal() as db:
                await clear_data(db)
        elif args.seed:
            print("Seeding database...")
            async with AsyncSessionLocal() as db:
                await seed_data(db)
        else:
            # 引数なしの場合、両方を実行
            print("No arguments provided. Clearing and seeding database...")
            async with AsyncSessionLocal() as db:
                await clear_data(db)
                await seed_data(db)

    asyncio.run(main())
