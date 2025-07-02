

from pydantic import Field
from pydantic_settings import BaseSettings


# NOTE: .envファイルから必須設定を読み取る
class Setting(BaseSettings):
    # アプリケーション基本設定
    APP_NAME: str = "MyApp"
    DEV_MODE: bool = True
    APP_URL: str = "https://localhost:5173"

    # セキュリティ設定（必須）
    SECRET_KEY: str = Field(..., description="JWT署名用の秘密鍵（必須）")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 240

    # ログの保存先
    APP_LOG_DIRECTORY: str = "logs/server/app"
    SQL_LOG_DIRECTORY: str = "logs/server/sql"
    PYTEST_APP_LOG_DIRECTORY: str = "logs/Pytest/app"
    PYTEST_SQL_LOG_DIRECTORY: str = "logs/Pytest/sql"

    # メールサーバー設定（必須）
    SMTP_SERVER: str = Field(..., description="SMTPサーバーアドレス（必須）")
    SMTP_PORT: int = 587
    SMTP_PASSWORD: str = Field(..., description="SMTPパスワード（必須）")
    SMTP_USERNAME: str = Field(..., description="SMTPユーザー名（必須）")

    class Config:
        env_file = ".env"  # .env ファイルを指定

setting = Setting()
