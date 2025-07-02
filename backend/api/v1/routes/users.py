"""
ユーザー管理API（FastAPI公式テンプレート準拠）
"""

import structlog
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from api.v1.common.database import get_db
from api.v1.features.feature_auth.auth_service import get_current_user
from api.v1.features.feature_auth.schemas.user import UserResponse, UserUpdate
from api.v1.models.user import User
from ..common.response_schemas import (
    create_success_response,
    SuccessResponse,
    ErrorCodes
)
from ..common.exception_handlers import BusinessLogicError

# ログ設定
logger = structlog.get_logger()

router = APIRouter()


@router.get(
    "/me",
    response_model=SuccessResponse[UserResponse],
    summary="現在のユーザー情報取得",
    description="""現在ログインしているユーザーの詳細情報を取得します。
    
    **認証必須:** JWTトークンが必要です。
    
    **取得できる情報:**
    - ユーザーID
    - ユーザー名
    - メールアドレス
    - 登録日時
    - 更新日時
    - アカウント状態
    """,
    responses={
        200: {
            "description": "ユーザー情報取得成功",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "ユーザー情報を取得しました",
                        "timestamp": "2025-07-02T12:00:00+09:00",
                        "data": {
                            "user_id": "123e4567-e89b-12d3-a456-426614174000",
                            "username": "example_user",
                            "email": "user@example.com",
                            "created_at": "2025-01-01T00:00:00+09:00",
                            "updated_at": "2025-07-02T12:00:00+09:00",
                            "is_active": True
                        }
                    }
                }
            }
        },
        401: {
            "description": "認証エラー",
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "message": "認証が必要です",
                        "error_code": "AUTH_001",
                        "timestamp": "2025-07-02T12:00:00+09:00"
                    }
                }
            }
        }
    },
    tags=["ユーザー管理"]
)
async def get_me(
    current_user: UserResponse = Depends(get_current_user)
) -> dict:
    """
    現在ログインしているユーザーの情報を取得
    
    Returns:
        dict: ユーザー情報
    """
    logger.info("get_me - start", user_id=current_user.user_id)
    try:
        user_data = UserResponse.model_validate(current_user)
        return create_success_response(
            message="ユーザー情報を取得しました",
            data=user_data.model_dump()
        )
    finally:
        logger.info("get_me - end")


@router.patch(
    "/me",
    response_model=SuccessResponse[UserResponse],
    summary="ユーザー情報更新",
    description="""現在ログイン中のユーザーの情報を部分的に更新します。
    
    **認証必須:** JWTトークンが必要です。
    
    **更新可能なフィールド:**
    - ユーザー名
    - メールアドレス（再認証が必要になる可能性あり）
    - その他のプロフィール情報
    
    **注意事項:**
    - メールアドレス変更時は再認証が必要になる場合があります
    - パスワード変更は別エンドポイントで行ってください
    
    **現在の状態:** 実装中です。
    """,
    responses={
        200: {
            "description": "ユーザー情報更新成功",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "ユーザー情報が正常に更新されました",
                        "timestamp": "2025-07-02T12:00:00+09:00",
                        "data": {
                            "user_id": "123e4567-e89b-12d3-a456-426614174000",
                            "username": "updated_user",
                            "email": "updated@example.com",
                            "updated_at": "2025-07-02T12:00:00+09:00"
                        }
                    }
                }
            }
        },
        400: {
            "description": "実装中エラー",
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "message": "ユーザー更新機能は現在実装中です",
                        "error_code": "BUSINESS_002",
                        "timestamp": "2025-07-02T12:00:00+09:00"
                    }
                }
            }
        },
        401: {
            "description": "認証エラー",
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "message": "認証が必要です",
                        "error_code": "AUTH_001",
                        "timestamp": "2025-07-02T12:00:00+09:00"
                    }
                }
            }
        }
    },
    tags=["ユーザー管理"]
)
async def update_me(
    *,
    session: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
    user_update: UserUpdate
) -> dict:
    """
    現在のユーザー情報を更新
    
    Args:
        session: データベースセッション
        current_user: 現在のユーザー
        user_update: 更新データ
        
    Returns:
        dict: 更新されたユーザー情報
    """
    logger.info("update_me - start", user_id=current_user.user_id)
    try:
        # TODO: ユーザー更新機能の実装が必要
        # updated_user = await update_user_service(session, current_user, user_update)
        logger.info("update_me - not implemented yet")
        raise BusinessLogicError(
            message="ユーザー更新機能は現在実装中です",
            error_code=ErrorCodes.OPERATION_NOT_ALLOWED
        )
    finally:
        logger.info("update_me - end")


@router.delete(
    "/me",
    response_model=SuccessResponse[None],
    summary="ユーザーアカウント削除",
    description="""現在ログイン中のユーザーアカウントを削除します。
    
    **認証必須:** JWTトークンが必要です。
    
    **削除方式:**
    - 論理削除（ソフトデリート）を採用
    - データは実際には残るが、非アクティブ状態に変更
    - ログイン不可になり、APIアクセスも無効化
    
    **注意事項:**
    - この操作は元に戻せません
    - 削除後は再ログインが必要です
    - 関連データの処理についてはシステム管理者にお問い合わせください
    
    **現在の状態:** 実装中です。
    """,
    responses={
        200: {
            "description": "ユーザーアカウント削除成功",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "ユーザーアカウントが正常に削除されました",
                        "timestamp": "2025-07-02T12:00:00+09:00",
                        "data": None
                    }
                }
            }
        },
        400: {
            "description": "実装中エラー",
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "message": "ユーザー削除機能は現在実装中です",
                        "error_code": "BUSINESS_002",
                        "timestamp": "2025-07-02T12:00:00+09:00"
                    }
                }
            }
        },
        401: {
            "description": "認証エラー",
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "message": "認証が必要です",
                        "error_code": "AUTH_001",
                        "timestamp": "2025-07-02T12:00:00+09:00"
                    }
                }
            }
        }
    },
    tags=["ユーザー管理"]
)
async def delete_me(
    *,
    session: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
) -> dict:
    """
    現在のユーザーアカウントを削除（論理削除）
    
    Args:
        session: データベースセッション
        current_user: 現在のユーザー
        
    Returns:
        dict: 削除成功メッセージ
    """
    logger.info("delete_me - start", user_id=current_user.user_id)
    try:
        # TODO: ユーザー削除機能の実装が必要
        # success = await delete_user_service(session, current_user.user_id)
        logger.info("delete_me - not implemented yet")
        raise BusinessLogicError(
            message="ユーザー削除機能は現在実装中です",
            error_code=ErrorCodes.OPERATION_NOT_ALLOWED
        )
    finally:
        logger.info("delete_me - end")