"""
ユーザー関連のCRUD操作（Create, Read, Update, Delete）
FastAPI標準の関数ベース実装
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from api.v1.models.user import User


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    """メールアドレスに基づいてユーザーを取得します。

    Args:
        db (AsyncSession): 非同期データベースセッション。
        email (str): 検索対象のメールアドレス。

    Returns:
        User | None: 該当するユーザーが存在すれば返却、それ以外はNone。
    """
    query = select(User).where(User.email == email, User.user_status == User.STATUS_ACTIVE, User.deleted_at.is_(None))
    result = await db.execute(query)
    return result.scalars().first()


async def get_user_by_username(db: AsyncSession, username: str) -> User | None:
    """ユーザー名に基づいてユーザーを取得します。

    Args:
        db (AsyncSession): 非同期データベースセッション。
        username (str): 検索対象のユーザー名。

    Returns:
        User | None: 該当するユーザーが存在すれば返却、それ以外はNone。
    """
    query = select(User).where(User.username == username, User.user_status == User.STATUS_ACTIVE, User.deleted_at.is_(None))
    result = await db.execute(query)
    return result.scalars().first()


async def get_user_by_id(db: AsyncSession, user_id: str) -> User | None:
    """ユーザーIDに基づいてユーザーを取得します。

    Args:
        db (AsyncSession): 非同期データベースセッション。
        user_id (str): 検索対象のユーザーID。

    Returns:
        User | None: 該当するユーザーが存在すれば返却、それ以外はNone。
    """
    query = select(User).where(User.user_id == user_id, User.user_status == User.STATUS_ACTIVE, User.deleted_at.is_(None))
    result = await db.execute(query)
    return result.scalars().first()


async def create_user(db: AsyncSession, user: User) -> User:
    """新しいユーザーをデータベースに登録します。

    Args:
        db (AsyncSession): 非同期データベースセッション。
        user (User): 作成するユーザーオブジェクト。

    Returns:
        User: 作成されたユーザーオブジェクト。
    """
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def update_user_password(db: AsyncSession, user: User, hashed_password: str) -> User:
    """ユーザーのパスワードを更新します。

    Args:
        db (AsyncSession): 非同期データベースセッション。
        user (User): 更新対象のユーザーオブジェクト。
        hashed_password (str): ハッシュ化された新しいパスワード。

    Returns:
        User: 更新されたユーザーオブジェクト。
    """
    user.hashed_password = hashed_password
    await db.commit()
    await db.refresh(user)
    return user


async def update_user_profile(db: AsyncSession, user: User, username: str | None = None, email: str | None = None) -> User:
    """ユーザーのプロフィール情報を更新します。

    Args:
        db (AsyncSession): 非同期データベースセッション。
        user (User): 更新対象のユーザーオブジェクト。
        username (str | None): 新しいユーザー名（オプション）。
        email (str | None): 新しいメールアドレス（オプション）。

    Returns:
        User: 更新されたユーザーオブジェクト。
    """
    if username is not None:
        user.username = username
    if email is not None:
        user.email = email
    
    await db.commit()
    await db.refresh(user)
    return user


async def delete_user(db: AsyncSession, user: User) -> User:
    """ユーザーを論理削除します。

    Args:
        db (AsyncSession): 非同期データベースセッション。
        user (User): 削除対象のユーザーオブジェクト。

    Returns:
        User: 削除されたユーザーオブジェクト。
    """
    from datetime import datetime
    from zoneinfo import ZoneInfo
    
    user.user_status = User.STATUS_DELETED
    user.deleted_at = datetime.now(ZoneInfo("Asia/Tokyo"))
    await db.commit()
    await db.refresh(user)
    return user


