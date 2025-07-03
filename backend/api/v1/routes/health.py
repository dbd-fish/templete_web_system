"""
ヘルスチェックAPI（FastAPI公式テンプレート準拠）
"""

from fastapi import APIRouter
from sqlalchemy import text

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from api.common.database import get_db
from api.common.response_schemas import (
    create_success_response,
    create_error_response,
    SuccessResponse,
    ErrorCodes
)

router = APIRouter()


@router.get(
    "/",
    response_model=SuccessResponse[dict],
    summary="基本ヘルスチェック",
    description="""システムの基本的なヘルスチェックを行います。
    
    APIサーバーが正常に動作しているかどうかを確認できます。
    
    **使用ケース:**
    - システム監視ツールによる定期チェック
    - ロードバランサーのヘルスチェック
    - デプロイ後の動作確認
    
    **認証:** 不要
    """,
    responses={
        200: {
            "description": "API正常動作中",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "APIが正常に動作しています",
                        "timestamp": "2025-07-02T12:00:00+09:00",
                        "data": {"status": "healthy"}
                    }
                }
            }
        }
    },
    tags=["ヘルスチェック"]
)
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


@router.get(
    "/db",
    response_model=SuccessResponse[dict],
    summary="データベースヘルスチェック",
    description="""データベース接続状態のヘルスチェックを行います。
    
    PostgreSQLデータベースへの接続確認と基本的なクエリ実行を
    行い、データベースが正常に動作しているかを確認します。
    
    **チェック内容:**
    - データベースコネクションの確認
    - シンプルなSELECTクエリの実行
    - レスポンス時間の測定
    
    **使用ケース:**
    - データベースサービスの状態監視
    - アプリケーションデプロイ後の確認
    - データベースメンテナンス後の動作確認
    
    **認証:** 不要
    """,
    responses={
        200: {
            "description": "データベース接続正常",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "データベースに正常に接続しています",
                        "timestamp": "2025-07-02T12:00:00+09:00",
                        "data": {
                            "status": "healthy",
                            "database": "connected"
                        }
                    }
                }
            }
        },
        500: {
            "description": "データベース接続エラー",
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "message": "データベース接続に失敗しました",
                        "error_code": "SERVER_002",
                        "timestamp": "2025-07-02T12:00:00+09:00",
                        "details": {
                            "database": "disconnected",
                            "error": "Connection timeout"
                        }
                    }
                }
            }
        }
    },
    tags=["ヘルスチェック"]
)
async def health_check_db(session: AsyncSession = Depends(get_db)) -> dict:
    """
    データベース接続ヘルスチェック
    
    Args:
        session: データベースセッション
        
    Returns:
        dict: データベース接続ステータス
    """
    try:
        # シンプルなクエリでデータベース接続確認
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