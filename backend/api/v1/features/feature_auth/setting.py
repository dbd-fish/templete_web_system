from pydantic_settings import BaseSettings, SettingsConfigDict


class AuthSetting(BaseSettings):
    """
    認証機能に関する設定クラス

    環境変数または.envファイルから設定を読み込みます。
    環境変数が存在しない場合はデフォルト値を使用します。
    """

    # セキュリティ設定
    SECRET_KEY: str = "your-secret-key-here-change-in-production-please"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30  # アクセストークンは短期間（30分）- H034一般的JWT実装
    REFRESH_TOKEN_EXPIRE_DAYS: int = 5  # リフレッシュトークンは短期間（5日）- J056要件

    # Cookie有効期限設定（JWTトークンと整合性を保つ）
    COOKIE_EXPIRE_BUFFER_MINUTES: int = 5  # Cookie期限をJWTより5分長く設定

    # Google OAuth 2.0設定
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/api/v1/auth/google/callback"

    # API仕様書用のサンプルJWTトークン（実際のトークンではない）
    DOC_JWT_TOKEN_EXAMPLE: str = "test"
    DOC_RESET_TOKEN_EXAMPLE: str = "test"

    @property
    def ACCESS_TOKEN_COOKIE_MAX_AGE(self) -> int:
        """アクセストークンCookie有効期限（JWTより若干長め：35分）"""
        return 60 * (self.ACCESS_TOKEN_EXPIRE_MINUTES + self.COOKIE_EXPIRE_BUFFER_MINUTES)  # 30分+5分=35分

    @property
    def REFRESH_TOKEN_COOKIE_MAX_AGE(self) -> int:
        """リフレッシュトークンCookie有効期限"""
        return 60 * 60 * 24 * self.REFRESH_TOKEN_EXPIRE_DAYS

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",  # 認証関連以外の環境変数を無視
    )


# 認証設定インスタンス作成
auth_setting = AuthSetting()
