"""
開発用API（FastAPI公式テンプレート準拠）
開発環境でのみ利用可能
"""

import structlog
from fastapi import APIRouter

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from api.common.database import get_db

# 段階的移行: 既存の開発機能を継続使用
from api.v1.features.feature_dev.seed_data import clear_data, seed_data
from api.common.response_schemas import (
    create_success_response,
    SuccessResponse
)

# ログ設定
logger = structlog.get_logger()

router = APIRouter()


@router.post(
    "/clear_data",
    response_model=SuccessResponse[None],
    summary="【開発用】データベースクリア",
    description="""開発環境用のデータベース全テーブルクリア機能です。
    
    **❗️ 警告: この操作は元に戻せません**
    
    **実行内容:**
    - 全テーブルのデータを完全削除
    - シーケンスのリセット
    - インデックスの再作成
    
    **使用ケース:**
    - 開発環境の初期化
    - テストデータのリセット
    - マイグレーションテストの事前準備
    
    **注意事項:**
    - 開発環境でのみ使用可能
    - 実行後はデータベースが空になります
    - バックアップが取られていることを確認してください
    """,
    responses={
        200: {
            "description": "データベースクリア成功",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "データベースのクリアが正常に完了しました",
                        "timestamp": "2025-07-02T12:00:00+09:00",
                        "data": None
                    }
                }
            }
        },
        500: {
            "description": "データベースエラー",
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "message": "データベースエラーが発生しました",
                        "error_code": "SERVER_002",
                        "timestamp": "2025-07-02T12:00:00+09:00"
                    }
                }
            }
        }
    },
    tags=["開発ツール"]
)
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
        return create_success_response(
            message="データベースのクリアが正常に完了しました"
        )
    finally:
        logger.info("clear_data_endpoint - end")


@router.post(
    "/seed_data",
    response_model=SuccessResponse[None],
    summary="【開発用】テストデータ投入",
    description="""開発環境用のテストデータ投入機能です。
    
    **機能概要:**
    事前に定義されたテストデータをデータベースに投入します。
    
    **投入されるデータ:**
    - サンプルユーザーアカウント
    - テスト用コンテンツ
    - マスターデータの初期値
    - 機能テスト用のサンプルデータ
    
    **使用ケース:**
    - 開発環境の初期セットアップ
    - フロントエンド開発時のテストデータ作成
    - APIテストの事前準備
    - デモンストレーション環境の構築
    
    **注意事項:**
    - 開発環境でのみ使用可能
    - 既存データと重複する可能性があります
    - 事前に `/clear_data` でクリアすることを推奨
    """,
    responses={
        200: {
            "description": "テストデータ投入成功",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "テストデータの投入が正常に完了しました",
                        "timestamp": "2025-07-02T12:00:00+09:00",
                        "data": None
                    }
                }
            }
        },
        500: {
            "description": "データベースエラー",
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "message": "データベースエラーが発生しました",
                        "error_code": "SERVER_002",
                        "timestamp": "2025-07-02T12:00:00+09:00"
                    }
                }
            }
        }
    },
    tags=["開発ツール"]
)
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
        return create_success_response(
            message="テストデータの投入が正常に完了しました"
        )
    finally:
        logger.info("seed_data_endpoint - end")