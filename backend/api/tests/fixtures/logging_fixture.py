import logging
from typing import Any

import pytest
import structlog


@pytest.fixture(scope="function", autouse=True)
def setup_logging() -> None:
    """
    テスト用のログ設定を行うフィクスチャ。
    各テストが実行される前にログレベルを設定し、構造化ログを初期化します。
    """
    # ログレベルをINFOに設定
    logging.basicConfig(level=logging.INFO)
    
    # structlogの設定
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


@pytest.fixture(scope="function")
def logger() -> Any:
    """
    テスト用のロガーを提供するフィクスチャ。
    """
    return structlog.get_logger()