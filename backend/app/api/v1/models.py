"""
統合モデル定義（SQLModel使用）
FastAPI公式テンプレート準拠のモデル定義
"""

from datetime import datetime, date
from typing import Optional
import uuid

from sqlmodel import SQLModel, Field, Column
from sqlalchemy import String, SmallInteger, TIMESTAMP, Date
from sqlalchemy.dialects.postgresql import UUID
from pydantic import EmailStr

from app.api.v1.common.common import datetime_now


# ユーザーモデル関連
class UserBase(SQLModel):
    """ユーザーの基本属性を定義する基底クラス"""
    username: str = Field(max_length=50, description="ユーザー名")
    email: EmailStr = Field(sa_column=Column(String(100), unique=True, nullable=False))
    contact_number: Optional[str] = Field(default=None, max_length=15, description="連絡先電話番号")
    date_of_birth: Optional[date] = Field(default=None, description="生年月日")
    user_role: int = Field(default=2, description="ユーザー権限レベル")
    user_status: int = Field(default=1, description="アカウント状態")


class User(UserBase, table=True):
    """SQLModelユーザーモデル（テーブル定義）"""
    __tablename__ = "user"
    
    # 権限レベル定数
    ROLE_GUEST = 1      # ゲストユーザー
    ROLE_FREE = 2       # 無料ユーザー
    ROLE_REGULAR = 3    # 一般ユーザー
    ROLE_ADMIN = 4      # 管理者
    ROLE_OWNER = 5      # オーナー
    
    # アカウント状態定数
    STATUS_ACTIVE = 1      # アクティブ
    STATUS_SUSPENDED = 2   # 停止
    
    user_id: uuid.UUID = Field(
        sa_column=Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        description="ユーザーID"
    )
    hashed_password: str = Field(
        sa_column=Column(String(255), nullable=False),
        description="ハッシュ化されたパスワード"
    )
    created_at: datetime = Field(
        sa_column=Column(TIMESTAMP, default=datetime_now, nullable=False),
        description="作成日時"
    )
    updated_at: datetime = Field(
        sa_column=Column(TIMESTAMP, default=datetime_now, onupdate=datetime_now, nullable=False),
        description="更新日時"
    )
    deleted_at: Optional[datetime] = Field(
        sa_column=Column(TIMESTAMP, nullable=True),
        default=None,
        description="削除日時（論理削除）"
    )


class UserCreate(UserBase):
    """ユーザー作成用スキーマ"""
    password: str = Field(min_length=8, description="パスワード（8文字以上）")


class UserResponse(UserBase):
    """API応答用スキーマ"""
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


class UserUpdate(SQLModel):
    """ユーザー更新用スキーマ（部分更新対応）"""
    username: Optional[str] = Field(default=None, max_length=50)
    email: Optional[EmailStr] = None
    contact_number: Optional[str] = Field(default=None, max_length=15)
    date_of_birth: Optional[date] = None
    user_role: Optional[int] = None
    user_status: Optional[int] = None


# 認証関連スキーマ
class Token(SQLModel):
    """JWT トークンレスポンス"""
    access_token: str
    token_type: str = "bearer"


class TokenData(SQLModel):
    """トークンデータスキーマ"""
    token: str


class SendPasswordResetEmailData(SQLModel):
    """パスワードリセットメール送信用スキーマ"""
    email: EmailStr


class PasswordResetData(SQLModel):
    """パスワードリセット用スキーマ"""
    token: str
    new_password: str = Field(min_length=8, description="新しいパスワード（8文字以上）")