"""
API共通の依存性注入（段階的移行版）
"""

from typing import AsyncGenerator, Annotated
from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession

# 段階的移行: 既存のデータベース設定を継続使用
from app.api.v1.common.database import get_db as legacy_get_db
from app.api.v1.features.feature_auth.security import verify_token
from app.api.v1.features.feature_auth.auth_repository import AuthRepository

# 将来的にこれらに移行予定
# from app.api.v1.core.db import get_db as get_db_session
# from app.api.v1.models import User  # SQLModel統合後

# 既存スキーマ使用（段階的移行）
from app.api.v1.features.feature_auth.schemas.user import UserResponse


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """データベースセッションの依存性注入（段階的移行版）"""
    async for session in legacy_get_db():
        yield session


# 型安全な依存性注入のエイリアス（FastAPI公式パターン準拠）
SessionDep = Annotated[AsyncSession, Depends(get_db)]


async def get_current_user(
    request: Request, 
    session: SessionDep
) -> "User":
    """現在のユーザー情報を取得（JWT認証）"""
    from app.api.v1.models import User
    from app.api.v1 import crud
    
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
    import uuid
    user = await crud.get_user_by_id(session=session, user_id=uuid.UUID(user_id))
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="ユーザーが見つかりません",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user