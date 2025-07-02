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

# ログの設定
logger = structlog.get_logger()

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: UserResponse = Depends(get_current_user)
) -> UserResponse:
    """
    現在ログインしているユーザーの情報を取得
    
    Returns:
        UserResponse: ユーザー情報
    """
    logger.info("get_me - start", user_id=current_user.user_id)
    try:
        return UserResponse.model_validate(current_user)
    finally:
        logger.info("get_me - end")


@router.patch("/me", response_model=UserResponse)
async def update_me(
    *,
    session: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
    user_update: UserUpdate
) -> UserResponse:
    """
    現在のユーザー情報を更新
    
    Args:
        session: データベースセッション
        current_user: 現在のユーザー
        user_update: 更新データ
        
    Returns:
        UserResponse: 更新されたユーザー情報
    """
    logger.info("update_me - start", user_id=current_user.user_id)
    try:
        # TODO: update_user機能の実装が必要
        # updated_user = await update_user_service(session, current_user, user_update)
        logger.info("update_me - not implemented yet")
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="User update functionality not implemented yet"
        )
    finally:
        logger.info("update_me - end")


@router.delete("/me")
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
        # TODO: delete_user機能の実装が必要
        # success = await delete_user_service(session, current_user.user_id)
        logger.info("delete_me - not implemented yet")
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="User deletion functionality not implemented yet"
        )
    finally:
        logger.info("delete_me - end")