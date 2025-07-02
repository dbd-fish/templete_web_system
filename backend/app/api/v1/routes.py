"""
API v1 ルーター統合
"""

from fastapi import APIRouter

from app.common.setting import setting
from app.api.v1.endpoints import auth, dev

router = APIRouter()

# 認証関連API
router.include_router(auth.router, prefix="/auth", tags=["auth"])

# 開発用API（開発環境でのみ有効）
if setting.DEV_MODE:
    router.include_router(dev.router, prefix="/dev", tags=["dev"])