# tests/conftest.py
import os
import time

from .fixtures.authenticate_fixture import *  # noqa: F403
from .fixtures.db_fixture import *  # noqa: F403
from .fixtures.logging_fixture import *  # noqa: F403

# タイムゾーンをJST（日本標準時）に設定
os.environ["TZ"] = "Asia/Tokyo"
time.tzset()
