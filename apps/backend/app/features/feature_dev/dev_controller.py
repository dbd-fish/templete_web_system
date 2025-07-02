import structlog
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.database import get_db
from app.features.feature_dev.seed_data import clear_data, seed_data

# ロガーの設定
logger = structlog.get_logger()

router = APIRouter()


@router.post("/clear_data", response_model=dict)
async def clear_data_endpoint(
    db: AsyncSession = Depends(get_db),
):
    """【開発用】
    全テーブルのクリア処理

    Args:
        db (AsyncSession): データベースセッション。

    Returns:
        dict: 成功メッセージ

    """
    logger.info("clear_data_endpoint - start")
    try:
        await clear_data(db)
        logger.info("clear_data_endpoint - success")
        return   {"msg": "clear_data API successfully"}
    finally:
        logger.info("clear_data_endpoint - end")

@router.post("/seed_data", response_model=dict)
async def seed_data_endpoint(
    db: AsyncSession = Depends(get_db),
):
    """【開発用】
    全テーブルのシーダー処理
    Args:
        db (AsyncSession): データベースセッション。

    Returns:
        dict: 成功メッセージ

    """
    logger.info("seed_data_endpoint - start")
    try:
        await seed_data(db)
        logger.info("seed_data_endpoint - success")
        return  {"msg": "seed_data API successfully"}
    finally:
        logger.info("seed_data_endpoint - end")

