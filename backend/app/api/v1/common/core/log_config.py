import logging
import os
from datetime import datetime
from zoneinfo import ZoneInfo

import structlog
from structlog.processors import CallsiteParameter

from app.common.setting import setting


def create_log_directory(directory: str) -> None:
    """指定されたログディレクトリを作成します。

    Args:
        directory (str): 作成するログディレクトリのパス。

    """
    print(f"Creating log directory at: {directory}")
    os.makedirs(directory, exist_ok=True)


def get_log_file_path(directory: str, filename_template: str = "app_{date}.log") -> str:
    """現在の日付を基にログファイルのパスを生成します。

    Args:
        directory (str): ログファイルを保存するディレクトリ。
        filename_template (str): ログファイル名のテンプレート。

    Returns:
        str: 生成されたログファイルのフルパス。

    """
    current_date = datetime.now(ZoneInfo("Asia/Tokyo")).strftime("%Y-%m-%d")
    log_file_path = os.path.join(directory, filename_template.format(date=current_date))
    print(f"Generated log file path: {log_file_path}")
    return log_file_path


def configure_logging(test_env: int = 0) -> structlog.BoundLogger:
    """ログ設定を行います。ファイルハンドラーやカスタムフォーマッタの設定、
    structlog用のプロセッサを含みます。
    Args:
        test_env (int): 環境指定フラグ (0: 本番環境、1: Pytest)。
    Returns:
        structlog.BoundLogger: 設定済みのstructlogロガーインスタンス。
    """
    print(f"Configuring logging for environment: {test_env}")
    if test_env == 1:
        create_log_directory(setting.PYTEST_APP_LOG_DIRECTORY)
        app_log_file_path = get_log_file_path(setting.PYTEST_APP_LOG_DIRECTORY)
    else:
        create_log_directory(setting.APP_LOG_DIRECTORY)
        app_log_file_path = get_log_file_path(setting.APP_LOG_DIRECTORY)

    class JSTFormatter(logging.Formatter):
        """日本時間（JST）でタイムスタンプをフォーマットするカスタムフォーマッタ。
        """

        def formatTime(self, record, datefmt=None):
            dt = datetime.fromtimestamp(record.created, ZoneInfo("Asia/Tokyo"))
            formatted_time = dt.strftime(datefmt) if datefmt else dt.isoformat()
            return formatted_time

    # アプリケーションログのファイルハンドラ設定
    app_file_handler = logging.FileHandler(app_log_file_path, encoding="utf-8")
    app_file_handler.setLevel(logging.INFO)
    app_formatter = JSTFormatter("[%(asctime)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    app_file_handler.setFormatter(app_formatter)

# アプリケーション用のロガー設定
    app_logger = logging.getLogger("app")
    app_logger.handlers = []
    app_logger.setLevel(logging.INFO)
    app_logger.addHandler(app_file_handler)
    print("App logger configured.")

    # SQLAlchemyログの設定
    configure_sqlalchemy_logging(test_env)

    # structlogの設定
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,  # リクエストスコープでの変数をログに統合
            structlog.processors.TimeStamper(fmt="iso", utc=False),  # ISOフォーマットのタイムスタンプを追加
            structlog.processors.add_log_level,  # ログレベルを追加
            structlog.stdlib.add_logger_name,  # ロガー名を追加
            structlog.processors.format_exc_info,  # 例外情報をフォーマット
            structlog.processors.CallsiteParameterAdder(  # ログ発生箇所の情報を追加
                [
                    CallsiteParameter.PATHNAME,  # ファイルのパス
                    # CallsiteParameter.MODULE,  # モジュール名
                    CallsiteParameter.FUNC_NAME,  # 関数名
                    CallsiteParameter.LINENO,  # 行番号
                ],
            ),
            structlog.processors.JSONRenderer(indent=4, sort_keys=True),  # JSON形式で出力
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    print("Structlog configured.")
    return structlog.get_logger()


def configure_sqlalchemy_logging(test_env: int = 0) -> None:
    """SQLAlchemyのログ設定を行います。
    Args:
        test_env (int): 環境指定フラグ (0: 本番環境、1: Pytest)。
    """
    print(f"Configuring SQLAlchemy logging for environment: {test_env}")
    if test_env == 1:
        create_log_directory(setting.PYTEST_SQL_LOG_DIRECTORY)
        sqlalchemy_log_file_path = get_log_file_path(setting.PYTEST_SQL_LOG_DIRECTORY, "sqlalchemy_{date}.log")
    else:
        create_log_directory(setting.SQL_LOG_DIRECTORY)
        sqlalchemy_log_file_path = get_log_file_path(setting.SQL_LOG_DIRECTORY, "sqlalchemy_{date}.log")

    # SQLAlchemy専用ロガーを設定
    sqlalchemy_logger = logging.getLogger("sqlalchemy")
    sqlalchemy_logger.handlers = []  # 既存ハンドラをクリア
    sqlalchemy_logger.setLevel(logging.WARNING)

    sqlalchemy_file_handler = logging.FileHandler(sqlalchemy_log_file_path, encoding="utf-8")
    sqlalchemy_file_handler.setLevel(logging.WARNING)  # ハンドラのレベルもWARNINGに設定
    sqlalchemy_formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S",
    )
    sqlalchemy_file_handler.setFormatter(sqlalchemy_formatter)

    sqlalchemy_logger.addHandler(sqlalchemy_file_handler)
    sqlalchemy_logger.propagate = False  # 親ロガーへの伝播を防ぐ

    # サブロガーにも同じ設定を適用
    for sub_logger_name in ["sqlalchemy.engine", "sqlalchemy.pool"]:
        sub_logger = logging.getLogger(sub_logger_name)
        sub_logger.handlers = []  # 既存ハンドラをクリア
        sub_logger.setLevel(logging.WARNING)  # サブロガーのレベルをWARNINGに設定
        sub_logger.addHandler(sqlalchemy_file_handler)  # ハンドラを追加
        sub_logger.propagate = False  # 親ロガーへの伝播を防ぐ

    print("SQLAlchemy logging configured.")

# ロガー作成
logger = configure_logging()
