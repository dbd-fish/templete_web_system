"""SQLite用のシードデータ生成（共通のseed_user関数を使用）"""
from sqlalchemy.ext.asyncio import AsyncSession

from api.v1.features.feature_dev.seed_user import seed_user


async def seed_sqlite_data(session: AsyncSession) -> None:
    """SQLite用のテストデータを挿入する関数（共通のseed_user関数を使用）"""
    print("SQLite用シードデータの挿入を開始（共通関数使用）")
    
    try:
        # 共通のseed_user関数を直接使用
        await seed_user(session)
        print("SQLite用シードデータの挿入が完了しました（共通関数使用）")
        
    except Exception as e:
        print(f"SQLite用シードデータ挿入中にエラーが発生: {e}")
        await session.rollback()
        raise