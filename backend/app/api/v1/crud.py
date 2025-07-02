"""
CRUD操作集約（FastAPI公式テンプレート準拠）
全エンティティのCRUD操作を関数ベースで統一管理
"""

from typing import Optional
import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlmodel import select as sqlmodel_select

from app.api.v1.models import User, UserCreate, UserUpdate
from app.api.v1.core.security import get_password_hash, verify_password


# User CRUD操作
async def create_user(*, session: AsyncSession, user_create: UserCreate) -> User:
    """
    新しいユーザーを作成
    
    Args:
        session: データベースセッション
        user_create: ユーザー作成データ
        
    Returns:
        User: 作成されたユーザー
    """
    hashed_password = get_password_hash(user_create.password)
    
    # パスワードを除いてUserCreateからUserに変換
    user_data = user_create.model_dump(exclude={"password"})
    db_user = User(**user_data, hashed_password=hashed_password)
    
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)
    return db_user


async def get_user_by_email(*, session: AsyncSession, email: str) -> Optional[User]:
    """
    メールアドレスでユーザーを取得
    
    Args:
        session: データベースセッション
        email: メールアドレス
        
    Returns:
        Optional[User]: ユーザーまたはNone
    """
    statement = select(User).where(
        User.email == email,
        User.user_status == User.STATUS_ACTIVE,
        User.deleted_at.is_(None)
    )
    result = await session.execute(statement)
    return result.scalar_one_or_none()


async def get_user_by_id(*, session: AsyncSession, user_id: uuid.UUID) -> Optional[User]:
    """
    ユーザーIDでユーザーを取得
    
    Args:
        session: データベースセッション
        user_id: ユーザーID
        
    Returns:
        Optional[User]: ユーザーまたはNone
    """
    statement = select(User).where(
        User.user_id == user_id,
        User.user_status == User.STATUS_ACTIVE,
        User.deleted_at.is_(None)
    )
    result = await session.execute(statement)
    return result.scalar_one_or_none()


async def authenticate_user(
    *, session: AsyncSession, email: str, password: str
) -> Optional[User]:
    """
    ユーザー認証
    
    Args:
        session: データベースセッション
        email: メールアドレス
        password: パスワード
        
    Returns:
        Optional[User]: 認証成功時はユーザー、失敗時はNone
    """
    user = await get_user_by_email(session=session, email=email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


async def update_user(
    *, session: AsyncSession, current_user: User, user_update: UserUpdate
) -> User:
    """
    ユーザー情報を更新
    
    Args:
        session: データベースセッション
        current_user: 現在のユーザー
        user_update: 更新データ
        
    Returns:
        User: 更新されたユーザー
    """
    user_data = user_update.model_dump(exclude_unset=True)
    for field, value in user_data.items():
        setattr(current_user, field, value)
    
    session.add(current_user)
    await session.commit()
    await session.refresh(current_user)
    return current_user


async def delete_user(*, session: AsyncSession, user_id: uuid.UUID) -> bool:
    """
    ユーザーを論理削除
    
    Args:
        session: データベースセッション
        user_id: ユーザーID
        
    Returns:
        bool: 削除成功時True、失敗時False
    """
    user = await get_user_by_id(session=session, user_id=user_id)
    if not user:
        return False
    
    from app.api.v1.common.common import datetime_now
    user.deleted_at = datetime_now()
    
    session.add(user)
    await session.commit()
    return True


async def check_email_exists(*, session: AsyncSession, email: str) -> bool:
    """
    メールアドレスの重複チェック
    
    Args:
        session: データベースセッション
        email: メールアドレス
        
    Returns:
        bool: 存在する場合True
    """
    statement = select(User).where(
        User.email == email,
        User.deleted_at.is_(None)
    )
    result = await session.execute(statement)
    return result.scalar_one_or_none() is not None


async def update_user_password(
    *, session: AsyncSession, user: User, new_password: str
) -> User:
    """
    ユーザーのパスワードを更新
    
    Args:
        session: データベースセッション
        user: ユーザー
        new_password: 新しいパスワード
        
    Returns:
        User: 更新されたユーザー
    """
    user.hashed_password = get_password_hash(new_password)
    
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user