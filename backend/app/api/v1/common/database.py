import configparser
from collections.abc import AsyncGenerator

from databases import Database
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import AsyncAdaptedQueuePool

from app.common.setting import setting

Base = declarative_base()

def get_database_url(test_env: int = 0) -> str:
    """環境に応じてデータベース接続URLを取得します。

    Args:
        test_env (int): 環境指定フラグ (0: 本番環境、1: Pytest)。

    Returns:
        str: データベース接続URL。

    """
    if test_env == 1:
        return "postgresql+asyncpg://template_user:template_password@db:5432/pytest_template_db"
    config = configparser.ConfigParser()
    config.read("alembic.ini")
    return config.get("alembic", "sqlalchemy.url")


def configure_database(test_env: int = 0):
    """データベース接続とセッションを設定します。

    Args:
        test_env (int): 環境指定フラグ (0: 本番、1: Pytest)。

    Returns:
        dict: データベース、エンジン、セッション情報を含む辞書。

    """
    database_url = get_database_url(test_env)
    database = Database(database_url)

    # NOTE: AsyncAdaptedQueuePoolではPytest時にイベントループ絡みで失敗するため、開発時はNullPoolにする
    if setting.DEV_MODE:
        # 開発時はコネクションプーリングを保持せずに都度接続＆開放するように設定
        print("Pytest用のDB環境設定")
        engine = create_async_engine(database_url, echo=False, poolclass=NullPool)
    else:
        # 本番環境では非同期でもコネクションプーリングを使いまわすように設定
        engine = create_async_engine(database_url, echo=False, poolclass=AsyncAdaptedQueuePool)

    # TODO: autoflushとexpire_on_commitについて調査
    # NOTE: AsyncSessionを使用する場合はbindをasync withのタイミングにしなとmypyエラーとなる
    async_session_local = sessionmaker(
        class_=AsyncSession,
        autoflush=True,
        expire_on_commit=True,
    )

    return {
        "database": database,
        "engine": engine,
        "sessionmaker": async_session_local,
    }


# 本番環境のデフォルト設定
# NOTE: 本番環境用DBとPytest用DBの使い分けをするために、engineとget_dbは外部ファイルから直接読み取らない。
#       engineについて、
#           本番環境であればAPIのdb: AsyncSession = Depends(get_db)からdb.bindでengineを取得して使用する。
#           pytestではフィクスチャ関数であるsetup_test_dbで前処理をしているため読み取る必要はないはず。
#       get_db()について、
#           本番環境ではAPIのdb: AsyncSession = Depends(get_db)からDB操作をする。
#           Pytestのテスト関数ではオーバーライドしたoverride_get_dbからDB操作をする。
db_config = configure_database()
database = db_config["database"]
engine = db_config["engine"]
AsyncSessionLocal = db_config["sessionmaker"]

async def get_db() -> AsyncGenerator:
    """非同期データベースセッションを生成するジェネレーター関数。

    Yields:
        AsyncSession: 非同期セッションインスタンス。

    """
    async with AsyncSessionLocal(bind=engine) as session:
        yield session
