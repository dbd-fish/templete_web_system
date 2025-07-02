"""
ユーザー管理API（FastAPI公式テンプレート準拠）
"""

import structlog
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import SessionDep, get_current_user
from app.api.v1.models import User, UserResponse, UserUpdate
from app.api.v1 import crud

# ログの設定
logger = structlog.get_logger()

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: Annotated[User, Depends(get_current_user)]
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
    session: SessionDep,
    current_user: Annotated[User, Depends(get_current_user)],
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
        updated_user = await crud.update_user(
            session=session,
            current_user=current_user,
            user_update=user_update
        )
        logger.info("update_me - success", user_id=updated_user.user_id)
        return UserResponse.model_validate(updated_user)
    finally:
        logger.info("update_me - end")


@router.delete("/me")
async def delete_me(
    *,
    session: SessionDep,
    current_user: Annotated[User, Depends(get_current_user)]
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
        success = await crud.delete_user(
            session=session,
            user_id=current_user.user_id
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete user"
            )
        
        logger.info("delete_me - success", user_id=current_user.user_id)
        return {"message": "User deleted successfully"}
    finally:
        logger.info("delete_me - end")