"""SQLite対応のテスト用モデル定義"""
import uuid
from datetime import datetime

from sqlalchemy import TIMESTAMP, Date, SmallInteger, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from api.common.common import datetime_now
from api.common.database import Base


class User(Base):
    """SQLite対応のUserモデル: ユーザー管理テーブル"""

    __tablename__ = "user"

    # ユーザー権限を定数として定義
    ROLE_GUEST = 1      # ゲスト
    ROLE_FREE = 2       # 無料会員
    ROLE_PREMIUM = 3    # 有料会員
    ROLE_ADMIN = 9      # 管理者

    # ユーザーステータスを定数として定義
    STATUS_INACTIVE = 0 # 無効
    STATUS_ACTIVE = 1   # 有効
    STATUS_SUSPENDED = 2 # 停止

    # SQLite対応：UUIDを文字列として保存
    user_id: Mapped[str] = mapped_column(
        String(36), 
        primary_key=True, 
        default=lambda: str(uuid.uuid4()), 
        comment="ユーザーID（UUID文字列）"
    )
    
    username: Mapped[str] = mapped_column(
        String(50), 
        unique=True, 
        index=True, 
        comment="ユーザー名（一意・50文字以内）"
    )
    
    email: Mapped[str] = mapped_column(
        String(100), 
        unique=True, 
        index=True, 
        comment="メールアドレス（一意・100文字以内）"
    )
    
    hashed_password: Mapped[str] = mapped_column(
        String(255), 
        comment="ハッシュ化されたパスワード"
    )
    
    contact_number: Mapped[str | None] = mapped_column(
        String(20), 
        comment="連絡先電話番号（任意・20文字以内）"
    )
    
    date_of_birth: Mapped[datetime | None] = mapped_column(
        Date, 
        comment="生年月日（任意）"
    )
    
    user_role: Mapped[int | None] = mapped_column(
        SmallInteger, 
        default=ROLE_FREE, 
        comment="ユーザー権限（デフォルト：無料会員）"
    )
    
    user_status: Mapped[int] = mapped_column(
        SmallInteger, 
        default=STATUS_ACTIVE, 
        comment="ユーザーステータス（デフォルト：有効）"
    )
    
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, 
        default=datetime_now, 
        comment="作成日時"
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, 
        default=datetime_now, 
        onupdate=datetime_now, 
        comment="更新日時"
    )
    
    deleted_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP, 
        comment="論理削除日時（NULL=有効）"
    )

    def __repr__(self) -> str:
        return f"<User(user_id={self.user_id}, username={self.username}, email={self.email})>"