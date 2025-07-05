from pydantic_settings import BaseSettings, SettingsConfigDict


class Setting(BaseSettings):
    """
    アプリケーション設定クラス

    環境変数または.envファイルから設定を読み込みます。
    環境変数が存在しない場合はデフォルト値を使用します。
    """

    # アプリケーション基本設定
    APP_NAME: str = "Template Web System"
    DEV_MODE: bool = True
    APP_URL: str = "http://localhost:3000"

    # セキュリティ設定
    SECRET_KEY: str = "your-secret-key-here-change-in-production-please"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 240

    # データベース設定
    DATABASE_HOST: str = "db"
    DATABASE_PORT: int = 5432
    DATABASE_NAME: str = "template_db"
    DATABASE_USER: str = "template_user"
    DATABASE_PASSWORD: str = "template_password"

    # ログの保存先
    APP_LOG_DIRECTORY: str = "logs/server/app"
    SQL_LOG_DIRECTORY: str = "logs/server/sql"
    PYTEST_APP_LOG_DIRECTORY: str = "logs/test/app"
    PYTEST_SQL_LOG_DIRECTORY: str = "logs/test/sql"

    # メールサーバー設定
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""

    # テスト環境でのメール送信設定
    ENABLE_EMAIL_SENDING: bool = True
    TEST_SMTP_SERVER: str = "localhost"
    TEST_SMTP_PORT: int = 1025
    PYTEST_MODE: bool = False

    # その他の設定
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173,http://frontend:5173"
    LOG_LEVEL: str = "INFO"
    TIMEZONE: str = "Asia/Tokyo"

    # ログ出力設定
    ENABLE_CONSOLE_LOG: bool = False

    # API仕様書用のサンプルJWTトークン（実際のトークンではない）
    DOC_JWT_TOKEN_EXAMPLE: str = "test"
    DOC_RESET_TOKEN_EXAMPLE: str = "test"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=True)


# 設定インスタンス作成
setting = Setting()
