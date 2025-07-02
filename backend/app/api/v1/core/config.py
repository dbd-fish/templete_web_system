"""
アプリケーション設定管理（FastAPI公式テンプレート準拠）
"""

import secrets
from typing import Annotated, Any, Literal
from pydantic import (
    AnyUrl,
    BeforeValidator,
    Field,
    PostgresDsn,
    computed_field,
    model_validator,
)
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


def parse_cors(v: Any) -> list[str] | str:
    """CORS設定のパース"""
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",")]
    elif isinstance(v, list | str):
        return v
    raise ValueError(v)


class Settings(BaseSettings):
    """アプリケーション設定クラス"""
    
    model_config = SettingsConfigDict(
        env_file=".env", env_ignore_empty=True, extra="ignore"
    )
    
    # API設定
    API_V1_STR: str = "/api/v1"
    
    # アプリケーション基本設定
    PROJECT_NAME: str = "MyApp"
    ENVIRONMENT: Literal["local", "staging", "production"] = "local"
    FRONTEND_HOST: str = "https://localhost:5173"
    
    # セキュリティ設定
    SECRET_KEY: str = Field(..., description="JWT署名用の秘密鍵")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8日間
    
    # CORS設定
    BACKEND_CORS_ORIGINS: Annotated[
        list[AnyUrl] | str, BeforeValidator(parse_cors)
    ] = []
    
    @computed_field  # type: ignore[misc]
    @property
    def all_cors_origins(self) -> list[str]:
        return [str(origin).rstrip("/") for origin in self.BACKEND_CORS_ORIGINS] + [
            self.FRONTEND_HOST
        ]
    
    # データベース設定
    POSTGRES_SERVER: str
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str = Field(..., description="PostgreSQLパスワード（必須）")
    POSTGRES_DB: str = ""
    
    @computed_field  # type: ignore[misc]
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> PostgresDsn:
        return MultiHostUrl.build(
            scheme="postgresql+asyncpg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_SERVER,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB,
        )
    
    # メール設定
    SMTP_TLS: bool = True
    SMTP_SSL: bool = False
    SMTP_PORT: int = 587
    SMTP_HOST: str = Field(..., description="SMTPサーバーアドレス（必須）")
    SMTP_USER: str = Field(..., description="SMTPユーザー名（必須）")
    SMTP_PASSWORD: str = Field(..., description="SMTPパスワード（必須）")
    
    # ログ設定
    APP_LOG_DIRECTORY: str = "logs/server/app"
    SQL_LOG_DIRECTORY: str = "logs/server/sql"
    PYTEST_APP_LOG_DIRECTORY: str = "logs/pytest/app"
    PYTEST_SQL_LOG_DIRECTORY: str = "logs/pytest/sql"
    
    # 管理者ユーザー設定
    FIRST_SUPERUSER: str = Field(..., description="初期管理者メールアドレス（必須）")
    FIRST_SUPERUSER_PASSWORD: str = Field(..., description="初期管理者パスワード（必須）")
    
    # ユーザー登録設定
    USERS_OPEN_REGISTRATION: bool = False
    
    @model_validator(mode="after")
    def _set_default_secret_key(self) -> "Settings":
        """開発環境でのデフォルト秘密鍵設定"""
        return self
    
    @property
    def DEV_MODE(self) -> bool:
        """開発モード判定（後方互換性）"""
        return self.ENVIRONMENT == "local"


settings = Settings()  # type: ignore