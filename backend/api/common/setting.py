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
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 240  # アクセストークンは長期間（4時間）- 401エラー緊急対策
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30  # リフレッシュトークンは長期間（30日）
    
    # Cookie有効期限設定（JWTトークンと整合性を保つ）
    COOKIE_EXPIRE_BUFFER_MINUTES: int = 5  # Cookie期限をJWTより5分長く設定

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

    # 本番環境モード（監視ポート制限用）
    PROD_MODE: bool = False

    # その他の設定
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173,https://localhost:5173,http://frontend:5173"
    LOG_LEVEL: str = "INFO"
    TIMEZONE: str = "Asia/Tokyo"

    # ログ出力設定
    ENABLE_CONSOLE_LOG: bool = False

    # Redis設定
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str = ""

    @property
    def REDIS_SESSION_EXPIRE_SECONDS(self) -> int:
        """Redisセッション期限をREFRESH_TOKEN_EXPIRE_DAYSに同期"""
        return 60 * 60 * 24 * self.REFRESH_TOKEN_EXPIRE_DAYS
    
    @property
    def ACCESS_TOKEN_COOKIE_MAX_AGE(self) -> int:
        """アクセストークンCookie有効期限（JWTより若干長め）"""
        return 60 * (self.ACCESS_TOKEN_EXPIRE_MINUTES + self.COOKIE_EXPIRE_BUFFER_MINUTES)
    
    @property
    def REFRESH_TOKEN_COOKIE_MAX_AGE(self) -> int:
        """リフレッシュトークンCookie有効期限"""
        return 60 * 60 * 24 * self.REFRESH_TOKEN_EXPIRE_DAYS

    # Google OAuth 2.0設定
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/api/v1/auth/google/callback"

    # API仕様書用のサンプルJWTトークン（実際のトークンではない）
    DOC_JWT_TOKEN_EXAMPLE: str = "test"
    DOC_RESET_TOKEN_EXAMPLE: str = "test"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=True)


# 設定インスタンス作成
setting = Setting()
