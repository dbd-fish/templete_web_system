"""
ヘルスチェックAPI（FastAPI公式テンプレート準拠）
"""

from fastapi import APIRouter
from sqlalchemy import text

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from api.v1.common.database import get_db

router = APIRouter()


@router.get("/")
async def health_check() -> dict:
    """
    基本的なヘルスチェック
    
    Returns:
        dict: ステータス情報
    """
    return {"status": "healthy", "message": "API is running"}


@router.get("/db")
async def health_check_db(session: AsyncSession = Depends(get_db)) -> dict:
    """
    データベース接続ヘルスチェック
    
    Args:
        session: データベースセッション
        
    Returns:
        dict: データベース接続ステータス
    """
    try:
        # シンプルなクエリでDB接続確認
        result = await session.execute(text("SELECT 1"))
        result.scalar()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}