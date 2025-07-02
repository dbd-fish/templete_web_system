"""
開発用API（FastAPI公式テンプレート準拠）
開発環境でのみ利用可能
"""

import structlog
from fastapi import APIRouter

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from api.v1.common.database import get_db

# 段階的移行: 既存の開発機能を継続使用
from api.v1.features.feature_dev.seed_data import clear_data, seed_data

# ログの設定
logger = structlog.get_logger()

router = APIRouter()


@router.post("/clear_data", response_model=dict)
async def clear_data_endpoint(session: AsyncSession = Depends(get_db)) -> dict:
    """
    【開発用】全テーブルのクリア処理
    
    Args:
        session: データベースセッション
        
    Returns:
        dict: 成功メッセージ
    """
    logger.info("clear_data_endpoint - start")
    try:
        await clear_data(session)
        logger.info("clear_data_endpoint - success")
        return {"msg": "clear_data API successfully"}
    finally:
        logger.info("clear_data_endpoint - end")


@router.post("/seed_data", response_model=dict)
async def seed_data_endpoint(session: AsyncSession = Depends(get_db)) -> dict:
    """
    【開発用】全テーブルのシーダー処理
    
    Args:
        session: データベースセッション
        
    Returns:
        dict: 成功メッセージ
    """
    logger.info("seed_data_endpoint - start")
    try:
        await seed_data(session)
        logger.info("seed_data_endpoint - success")
        return {"msg": "seed_data API successfully"}
    finally:
        logger.info("seed_data_endpoint - end")