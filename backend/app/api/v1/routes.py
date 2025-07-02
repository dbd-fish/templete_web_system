"""
API v1 ルーター統合（FastAPI公式テンプレート準拠）
"""

from fastapi import APIRouter

from app.core.config import settings
from app.api.v1.routes import auth, users, dev, health

router = APIRouter()

# 認証関連API
router.include_router(auth.router, prefix="/auth", tags=["auth"])

# ユーザー管理API
router.include_router(users.router, prefix="/users", tags=["users"])

# ヘルスチェックAPI
router.include_router(health.router, prefix="/health", tags=["health"])

# 開発用API（開発環境でのみ有効）
if settings.DEV_MODE:
    router.include_router(dev.router, prefix="/dev", tags=["dev"])