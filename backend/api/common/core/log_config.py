import logging
import os
from datetime import datetime
from zoneinfo import ZoneInfo

import structlog
from structlog.processors import CallsiteParameter

from api.common.setting import setting


def create_log_directory(directory: str) -> None:
    """指定されたログディレクトリを作成します。

    Args:
        directory (str): 作成するログディレクトリのパス。

    """
    print(f"Creating log directory: {directory}")
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

    # structlog用のProcessorFormatterを設定（ファイル出力用）
    file_formatter = structlog.stdlib.ProcessorFormatter(
        processor=structlog.processors.JSONRenderer(indent=4, sort_keys=True),
        foreign_pre_chain=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.TimeStamper(fmt="%Y-%m-%dT%H:%M:%S.%f", utc=False),
            structlog.processors.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.processors.format_exc_info,
            structlog.processors.CallsiteParameterAdder([CallsiteParameter.PATHNAME, CallsiteParameter.FUNC_NAME, CallsiteParameter.LINENO]),
        ],
    )
    
    # コンソール出力用フォーマッタ
    console_formatter = structlog.stdlib.ProcessorFormatter(
        processor=structlog.dev.ConsoleRenderer(colors=True),
        foreign_pre_chain=[structlog.contextvars.merge_contextvars, structlog.processors.TimeStamper(fmt="%Y-%m-%dT%H:%M:%S.%f", utc=False), structlog.processors.add_log_level, structlog.stdlib.add_logger_name],
    )

    # ファイルハンドラ設定
    app_file_handler = logging.FileHandler(app_log_file_path, encoding="utf-8")
    app_file_handler.setLevel(logging.INFO)
    app_file_handler.setFormatter(file_formatter)

    # コンソールハンドラ設定
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)

    # ルートロガー設定
    root_logger = logging.getLogger()
    root_logger.handlers.clear()  # 既存ハンドラをクリア
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(app_file_handler)
    
    # コンソール出力制御（環境変数による制御）
    if setting.ENABLE_CONSOLE_LOG:
        root_logger.addHandler(console_handler)
        print("Console logging enabled")
    else:
        print("Console logging disabled - logs will only be written to files")
    
    print("Application logger configuration completed.")

    # SQLAlchemyログの設定
    configure_sqlalchemy_logging(test_env)

    # structlogの設定
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,  # ログレベルでフィルタリング
            structlog.contextvars.merge_contextvars,  # リクエストスコープでの変数をログに統合
             structlog.processors.TimeStamper(fmt="iso", utc=False),  # ISOフォーマットのタイムスタンプを追加
            structlog.stdlib.add_logger_name,  # ロガー名を追加
            structlog.stdlib.add_log_level,  # ログレベルを追加
            structlog.stdlib.PositionalArgumentsFormatter(),  # 位置引数をフォーマット
            structlog.processors.StackInfoRenderer(),  # スタック情報をレンダリング
            structlog.processors.format_exc_info,  # 例外情報をフォーマット
            structlog.processors.UnicodeDecoder(),  # Unicode文字をデコード
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,  # stdlibハンドラで使用可能にする
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    print("Structlog configuration completed.")
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
    
    # ISO形式でマイクロ秒まで含むSQLAlchemy用フォーマッタ
    class SQLAlchemyJSTFormatter(logging.Formatter):
        """SQLAlchemy用のJST時間フォーマッタ"""
        def formatTime(self, record, datefmt=None):
            dt = datetime.fromtimestamp(record.created, ZoneInfo("Asia/Tokyo"))
            return dt.strftime(datefmt) if datefmt else dt.isoformat()
    
    sqlalchemy_formatter = SQLAlchemyJSTFormatter("[%(asctime)s] [%(levelname)s] %(message)s", datefmt="%Y-%m-%dT%H:%M:%S.%f")
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

    print("SQLAlchemy logging configuration completed.")

# ロガー作成
logger = configure_logging()
