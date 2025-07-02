import uuid
from datetime import datetime

from sqlalchemy import TIMESTAMP, Date, SmallInteger, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.common.common import datetime_now
from app.common.database import Base


class User(Base):
    """Userモデル: ユーザー管理テーブル
    """

    __tablename__ = "user"

    # ユーザー権限を定数として定義
    ROLE_GUEST = 1      # ゲスト
    ROLE_FREE = 2       # 無料会員
    ROLE_REGULAR = 3    # 一般会員
    ROLE_ADMIN = 4      # 管理者
    ROLE_OWNER = 5      # オーナー

    # ユーザー状態を定数として定義
    STATUS_ACTIVE = 1   # アクティブ
    STATUS_SUSPENDED = 2 # 停止中

    # ユーザーID (UUID) - プライマリキー
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, comment="ユーザーID (UUID)")

    # ユーザー名 - 50文字以内
    username: Mapped[str] = mapped_column(String(50), nullable=False, comment="ユーザー名")

    # メールアドレス - 一意でなければならない
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, comment="メールアドレス")

    # パスワードハッシュ
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False, comment="パスワード（ハッシュ）")

    # 連絡先電話番号
    contact_number: Mapped[str | None] = mapped_column(String(15), comment="連絡先電話番号")

    # 生年月日
    date_of_birth: Mapped[Date | None] = mapped_column(Date, comment="生年月日")

    # ユーザー権限
    user_role: Mapped[int] = mapped_column(SmallInteger, nullable=False, comment="ユーザー権限 (1: guest, 2: free, 3: regular, 4: admin, 5: owner)")

    # アカウント状態
    user_status: Mapped[int] = mapped_column(SmallInteger, nullable=False, comment="アカウント状態 (1: active, 2: suspended)")

    # 作成日時
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime_now(), comment="作成日時")

    # 更新日時 - 更新時に自動で変更
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime_now(), onupdate=datetime_now(), comment="更新日時")

    # 削除日時
    deleted_at: Mapped[datetime | None] = mapped_column(TIMESTAMP, nullable=True, comment="削除日時")
