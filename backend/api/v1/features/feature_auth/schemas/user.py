from datetime import date

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from api.common.test_data import TestData
from api.v1.features.feature_auth.models.user import User


class LoginRequest(BaseModel):
    """ログインリクエストデータを表すモデル。"""

    username: str = Field(
        ...,
        description="ユーザー名またはメールアドレス",
        examples=[TestData.DOC_USERNAME_EXAMPLE, TestData.DOC_EMAIL_EXAMPLE],
    )
    password: str = Field(
        ...,
        description="パスワード",
        examples=[TestData.DOC_PASSWORD_EXAMPLE],
    )


class UserCreate(BaseModel):
    """ユーザー作成時に必要なデータを表すモデル。"""

    email: EmailStr = Field(
        ...,
        description="ユーザーのメールアドレス",
        examples=[TestData.DOC_EMAIL_EXAMPLE, TestData.DOC_NEW_USER_EMAIL],
    )
    username: str = Field(
        ...,
        max_length=50,
        min_length=3,
        description="ユーザー名 (3-50文字)",
        examples=[TestData.DOC_USERNAME_EXAMPLE, TestData.DOC_NEW_USERNAME],
    )
    password: str = Field(
        ...,
        min_length=8,
        description="ユーザーのパスワード (8文字以上、英数字記号を含む)",
        examples=[TestData.DOC_NEW_PASSWORD, TestData.DOC_ADMIN_PASSWORD],
    )
    user_role: int = Field(
        User.ROLE_FREE,
        description="ユーザー権限",
        examples=[User.ROLE_FREE],
    )
    user_status: int = Field(
        User.STATUS_ACTIVE,
        description="アカウント状態",
        examples=[User.STATUS_ACTIVE],
    )

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """パスワードの複雑性チェック"""
        if len(v) < 8:
            raise ValueError("パスワードは8文字以上である必要があります")
        if not any(c.islower() for c in v):
            raise ValueError("パスワードに小文字を含めてください")
        if not any(c.isupper() for c in v):
            raise ValueError("パスワードに大文字を含めてください")
        if not any(c.isdigit() for c in v):
            raise ValueError("パスワードに数字を含めてください")
        return v

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        """ユーザー名の妥当性チェック"""
        if not v.strip():
            raise ValueError("ユーザー名は空にできません")
        return v.strip()

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "email": "newuser@example.com",
                    "username": "newuser123",
                    "password": "SecurePassword2024!",
                    "user_role": User.ROLE_FREE,
                    "user_status": User.STATUS_ACTIVE,
                },
                {
                    "email": "admin@company.com",
                    "username": "admin_user",
                    "password": "AdminPass123+-",
                    "user_role": User.ROLE_ADMIN,
                    "user_status": User.STATUS_ACTIVE,
                },
            ],
        },
    )


class TokenData(BaseModel):
    """ユーザー認証・登録時に使用するJWTトークンデータを表すモデル。"""

    token: str = Field(
        ...,
        description="ユーザー情報が格納されているJWTトークン",
        examples=[TestData.DOC_JWT_TOKEN_EXAMPLE],
    )

    @field_validator("token")
    @classmethod
    def validate_token(cls, v: str) -> str:
        """JWTトークンの基本的な形式チェック"""
        if not v.strip():
            raise ValueError("トークンは空にできません")
        parts = v.split(".")
        if len(parts) != 3:
            raise ValueError("無効なJWTトークン形式です")
        return v.strip()


class SendPasswordResetEmailData(BaseModel):
    """パスワードリセットメール送信時のリクエストデータを表すモデル。"""

    email: EmailStr = Field(
        ...,
        description="パスワードリセットメールを送信するユーザーのメールアドレス",
        examples=[TestData.DOC_EMAIL_EXAMPLE, TestData.DOC_ADMIN_EMAIL],
    )


class PasswordResetData(BaseModel):
    """パスワードリセット実行時のリクエストデータを表すモデル。"""

    token: str = Field(
        ...,
        description="パスワードリセット用JWTトークン（メールで送信される）",
        examples=[TestData.DOC_RESET_TOKEN_EXAMPLE],
    )
    new_password: str = Field(
        ...,
        min_length=8,
        description="新しいパスワード (8文字以上、英数字記号を含む)",
        examples=[TestData.DOC_RESET_PASSWORD],
    )

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        """新しいパスワードの複雑性チェック"""
        if len(v) < 8:
            raise ValueError("パスワードは8文字以上である必要があります")
        if not any(c.islower() for c in v):
            raise ValueError("パスワードに小文字を含めてください")
        if not any(c.isupper() for c in v):
            raise ValueError("パスワードに大文字を含めてください")
        if not any(c.isdigit() for c in v):
            raise ValueError("パスワードに数字を含めてください")
        return v

    @field_validator("token")
    @classmethod
    def validate_reset_token(cls, v: str) -> str:
        """パスワードリセットトークンの形式チェック"""
        if not v.strip():
            raise ValueError("リセットトークンは空にできません")
        parts = v.split(".")
        if len(parts) != 3:
            raise ValueError("無効なJWTトークン形式です")
        return v.strip()


class UserUpdate(BaseModel):
    """ユーザー情報更新時のリクエストデータを表すモデル。"""

    email: EmailStr | None = Field(
        None,
        description="新しいメールアドレス（任意）",
        examples=[TestData.DOC_NEW_USER_EMAIL, TestData.DOC_ADMIN_EMAIL],
    )
    username: str | None = Field(
        None,
        max_length=50,
        min_length=3,
        description="新しいユーザー名（任意・3-50文字）",
        examples=[TestData.DOC_NEW_USERNAME, TestData.DOC_ADMIN_USERNAME],
    )
    contact_number: str | None = Field(
        None,
        max_length=20,
        description="連絡先電話番号（任意・20文字以内）",
        examples=[TestData.DOC_CONTACT_NUMBER],
    )
    date_of_birth: date | None = Field(
        None,
        description="生年月日（任意・YYYY-MM-DD形式）",
        examples=[TestData.DOC_DATE_OF_BIRTH],
    )

    @field_validator("username")
    @classmethod
    def validate_username_update(cls, v: str | None) -> str | None:
        """ユーザー名更新時の妥当性チェック"""
        if v is not None and not v.strip():
            raise ValueError("ユーザー名は空にできません")
        return v.strip() if v else None

    @field_validator("contact_number")
    @classmethod
    def validate_contact_number(cls, v: str | None) -> str | None:
        """電話番号の基本的な形式チェック"""
        if v is not None:
            # 基本的な電話番号形式のチェック（数字、ハイフン、プラス記号のみ許可）
            import re

            if not re.match(r"^[0-9+\-\s\(\)]+$", v.strip()):
                raise ValueError("電話番号に無効な文字が含まれています")
            return v.strip()
        return None

    model_config = ConfigDict(from_attributes=True)


class UserResponse(BaseModel):
    """ユーザー情報のレスポンスデータを表すモデル。"""

    email: EmailStr = Field(
        ...,
        description="ユーザーのメールアドレス",
        examples=[TestData.DOC_EMAIL_EXAMPLE],
    )
    username: str = Field(
        ...,
        description="ユーザー名",
        examples=[TestData.DOC_USERNAME_EXAMPLE, TestData.DOC_ADMIN_USERNAME],
    )
    contact_number: str | None = Field(
        None,
        description="連絡先電話番号",
        examples=[TestData.DOC_CONTACT_NUMBER],
    )
    date_of_birth: date | None = Field(
        None,
        description="生年月日",
        examples=[TestData.DOC_DATE_OF_BIRTH],
    )
    user_role: int = Field(
        ...,
        description="ユーザー権限",
        examples=[User.ROLE_FREE, User.ROLE_ADMIN],
    )
    user_status: int = Field(
        ...,
        description="アカウント状態",
        examples=[User.STATUS_ACTIVE, User.STATUS_SUSPENDED],
    )

    model_config = ConfigDict(from_attributes=True)
