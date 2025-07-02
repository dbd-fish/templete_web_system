"""
API共通の依存性注入
"""

from typing import AsyncGenerator
from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.database import AsyncSessionLocal, engine
from app.features.feature_auth.security import verify_token
from app.features.feature_auth.auth_repository import AuthRepository
from app.schemas.user import UserResponse


async def get_db() -> AsyncGenerator:
    """データベースセッションの依存性注入"""
    async with AsyncSessionLocal(bind=engine) as session:
        yield session


async def get_current_user(
    request: Request, 
    db: AsyncSession = Depends(get_db)
) -> UserResponse:
    """現在のユーザー情報を取得（JWT認証）"""
    token = request.headers.get("Authorization")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="認証トークンが見つかりません",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # "Bearer "プレフィックスを削除
    if token.startswith("Bearer "):
        token = token[7:]
    
    # JWTトークンの検証
    payload = verify_token(token)
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="無効なトークンです",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # ユーザー情報をデータベースから取得
    auth_repo = AuthRepository(db)
    user = await auth_repo.get_user_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="ユーザーが見つかりません",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return UserResponse.model_validate(user)