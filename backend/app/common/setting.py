

from pydantic_settings import BaseSettings


# NOTE: template_backend_container\.envから下記を読み取る
class Setting(BaseSettings):
    # アプリケーション基本設定
    APP_NAME: str = "MyApp"
    DEV_MODE: bool = True
    APP_URL: str = "https://localhost:5173"

    # セキュリティ設定
    SECRET_KEY: str = "default_secret_key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 240

    # ログの保存先
    APP_LOG_DIRECTORY: str = "logs/server/app"
    SQL_LOG_DIRECTORY: str = "logs/server/sql"
    PYTEST_APP_LOG_DIRECTORY: str = "logs/Pytest/app"
    PYTEST_SQL_LOG_DIRECTORY: str = "logs/Pytest/sql"

    # メールサーバー設定
    SMTP_SERVER: str = "smtp.example.com"
    SMTP_PORT: int = 587
    SMTP_PASSWORD: str = "default_password"
    SMTP_USERNAME: str = "user@example.com"

    class Config:
        env_file = ".env"  # .env ファイルを指定

setting = Setting()
