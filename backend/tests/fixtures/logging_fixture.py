import pytest_asyncio

from app.common.core.log_config import configure_logging


@pytest_asyncio.fixture(scope="function", autouse=True)
def setup_test_logging():
    """pytestの実行時にログ出力をテスト用に切り替える。
    """
    print("ログ出力をテスト用に切り替え")
    configure_logging(test_env=1)  # 結合テスト用
    yield
    print("ログ出力を本番用に切り替え")
    configure_logging(test_env=0)  # 本番環境用
