from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.user import User


class UserRepository:
    """ユーザー関連のデータベース操作を担当するリポジトリクラス。"""

    @staticmethod
    async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
        """メールアドレスに基づいてユーザーを取得します。

        Args:
            db (AsyncSession): 非同期データベースセッション。
            email (str): 検索対象のメールアドレス。

        Returns:
            User | None: 該当するユーザーが存在すれば返却、それ以外はNone。

        """
        query = select(User).where(
            User.email == email,
            User.user_status == User.STATUS_ACTIVE,
            User.deleted_at.is_(None),
        )
        result = await db.execute(query)
        return result.scalars().first()

    @staticmethod
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

    @staticmethod
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


