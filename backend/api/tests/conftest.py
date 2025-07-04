# tests/conftest.py
import os
import time

# 使用中のフィクスチャのみインポート
from .fixtures.authenticate_fixture import *  # noqa: F403 - authenticated_client
from .fixtures.db_fixture import *  # noqa: F403 - setup_basic_test_env
from .fixtures.logging_fixture import *  # noqa: F403 - setup_logging (autouse)
from .fixtures.mock_email_fixture import *  # noqa: F403 - disable_email_sending

# タイムゾーンをJST（日本標準時）に設定
os.environ["TZ"] = "Asia/Tokyo"
time.tzset()
