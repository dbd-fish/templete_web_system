"""
既存コードとの互換性維持モジュール
段階的移行期間中の後方互換性を提供
"""

from app.core.config import settings

# 既存のsetting.pyとの互換性を保つためのエイリアス
class CompatSetting:
    """既存コードとの互換性を維持するための設定クラス"""
    
    @property
    def APP_NAME(self) -> str:
        return settings.PROJECT_NAME
    
    @property
    def DEV_MODE(self) -> bool:
        return settings.DEV_MODE
    
    @property
    def APP_URL(self) -> str:
        return settings.FRONTEND_HOST
    
    @property
    def SECRET_KEY(self) -> str:
        return settings.SECRET_KEY
    
    @property
    def ALGORITHM(self) -> str:
        return settings.ALGORITHM
    
    @property
    def ACCESS_TOKEN_EXPIRE_MINUTES(self) -> int:
        return settings.ACCESS_TOKEN_EXPIRE_MINUTES
    
    @property
    def APP_LOG_DIRECTORY(self) -> str:
        return settings.APP_LOG_DIRECTORY
    
    @property
    def SQL_LOG_DIRECTORY(self) -> str:
        return settings.SQL_LOG_DIRECTORY
    
    @property
    def PYTEST_APP_LOG_DIRECTORY(self) -> str:
        return settings.PYTEST_APP_LOG_DIRECTORY
    
    @property
    def PYTEST_SQL_LOG_DIRECTORY(self) -> str:
        return settings.PYTEST_SQL_LOG_DIRECTORY
    
    @property
    def SMTP_SERVER(self) -> str:
        return settings.SMTP_HOST
    
    @property
    def SMTP_PORT(self) -> int:
        return settings.SMTP_PORT
    
    @property
    def SMTP_PASSWORD(self) -> str:
        return settings.SMTP_PASSWORD
    
    @property
    def SMTP_USERNAME(self) -> str:
        return settings.SMTP_USER


# 既存コード用の互換性インスタンス
setting = CompatSetting()