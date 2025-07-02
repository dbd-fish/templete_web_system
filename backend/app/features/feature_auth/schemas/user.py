from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.user import User


class UserCreate(BaseModel):
    """ユーザー作成時に必要なデータを表すモデル。
    """

    email: EmailStr = Field(..., description="ユーザーのメールアドレス")
    username: str = Field(..., max_length=50, description="ユーザー名 (50文字以内)")
    password: str = Field(..., min_length=8, description="ユーザーのパスワード (8文字以上)")

    user_role: int = Field(User.ROLE_FREE, description="ユーザー権限 (1: guest, 2: free, 3: regular, 4: admin, 5: owner)")
    user_status: int = Field(User.STATUS_ACTIVE, description="アカウント状態 (1: active, 2: suspended)")

class TokenData(BaseModel):
    """ユーザー作成時に使用するリクエストデータを表すモデル。
    """
    token: str = Field(..., description="ユーザー情報が格納されるているJWT")


class SendPasswordResetEmailData(BaseModel):
    """パスワードリセットメール送信時のモデル。
    """
    email: EmailStr = Field(..., description="ユーザーのメールアドレス")



class PasswordResetData(BaseModel):
    """パスワードリセット時のリクエストデータを表すモデル。
    """
    token: str = Field(..., description="ユーザー情報が格納されるているJWT")
    new_password: str = Field(..., min_length=8, description="新しいパスワード (8文字以上)")


class UserResponse(BaseModel):
    """ユーザー情報のレスポンスデータを表すモデル。
    """

    user_id: UUID = Field(..., description="ユーザーの一意な識別子")
    email: EmailStr = Field(..., description="ユーザーのメールアドレス")
    username: str = Field(..., description="ユーザー名")
    user_role: int = Field(..., description="ユーザー権限 (1: guest, 2: free, 3: regular, 4: admin, 5: owner)")
    user_status: int = Field(..., description="アカウント状態 (1: active, 2: suspended)")

    model_config = ConfigDict(from_attributes = True)
