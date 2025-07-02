"""
ヘルスチェックAPI（FastAPI公式テンプレート準拠）
"""

from fastapi import APIRouter
from sqlalchemy import text

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from api.v1.common.database import get_db
from ..common.response_schemas import (
    create_success_response,
    create_error_response,
    SuccessResponse,
    ErrorCodes
)

router = APIRouter()


@router.get("/", response_model=SuccessResponse[dict])
async def health_check() -> dict:
    """
    基本的なヘルスチェック
    
    Returns:
        dict: ステータス情報
    """
    return create_success_response(
        message="APIが正常に動作しています",
        data={"status": "healthy"}
    )


@router.get("/db", response_model=SuccessResponse[dict])
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
        return create_success_response(
            message="データベースに正常に接続しています",
            data={"status": "healthy", "database": "connected"}
        )
    except Exception as e:
        return create_error_response(
            message="データベース接続に失敗しました",
            error_code=ErrorCodes.DATABASE_ERROR,
            details={"database": "disconnected", "error": str(e)}
        )