from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from api.common.test_data import TestData
from api.v1.features.feature_auth.models.user import User


class LoginRequest(BaseModel):
    """ログインリクエストのスキーマ（OAuth2仕様準拠）"""

    username: str = Field(
        ...,
        description="ユーザー名またはメールアドレス（OAuth2仕様でusernameフィールドを使用）",
        examples=[TestData.TEST_USER_EMAIL_1],
    )
    password: str = Field(
        ...,
        description="パスワード",
        examples=[TestData.TEST_USER_PASSWORD],
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "username": "testuser@example.com",
                "password": "Password123456+-",
            },
        }
    }


class DirectUserCreate(BaseModel):
    """直接ユーザー登録時に必要なデータを表すモデル。"""

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
    password_confirm: str = Field(
        ...,
        min_length=8,
        description="パスワード確認用 (passwordと同じ値)",
        examples=[TestData.DOC_NEW_PASSWORD, TestData.DOC_ADMIN_PASSWORD],
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

    @field_validator("password_confirm")
    @classmethod
    def validate_password_confirm(cls, v: str, info) -> str:
        """パスワード確認の一致チェック"""
        if "password" in info.data and v != info.data["password"]:
            raise ValueError("パスワードが一致しません")
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "email": "newuser@example.com",
                    "username": "newuser123",
                    "password": "SecurePassword2024!",
                    "password_confirm": "SecurePassword2024!",
                },
            ],
        },
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


class GoogleLoginRequest(BaseModel):
    """Googleログインリクエストデータを表すモデル。"""

    id_token: str = Field(
        ...,
        description="GoogleからのIDトークン",
        examples=["eyJhbGciOiJSUzI1NiIsImtpZCI6IjE2NzAy..."],
    )

    @field_validator("id_token")
    @classmethod
    def validate_id_token(cls, v: str) -> str:
        """IDトークンの基本的な形式チェック"""
        if not v.strip():
            raise ValueError("IDトークンは空にできません")
        parts = v.split(".")
        if len(parts) != 3:
            raise ValueError("無効なJWTトークン形式です")
        return v.strip()

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "id_token": (
                        "eyJhbGciOiJSUzI1NiIsImtpZCI6IjE2NzAyNGU2Y2U2ZjVlNTRkYjBhNzVhZjRjYzI1MTkwNzY1NDQwMTciLCJ0eXAiOiJKV1QifQ."
                        "eyJpc3MiOiJhY2NvdW50cy5nb29nbGUuY29tIiwiYXVkIjoieW91ci1jbGllbnQtaWQtaGVyZS5hcHBzLmdvb2dsZXVzZXJjb250ZW50LmNvbSIsInN1YiI6IjEyMzQ1Njc4OTAiLCJlbWFpbCI6InVzZXJAZ21haWwuY29tIiwiZW1haWxfdmVyaWZpZWQiOnRydWUsIm5hbWUiOiJKb2huIERvZSIsInBpY3R1cmUiOiJodHRwczovL2xoMy5nb29nbGV1c2VyY29udGVudC5jb20vYS0vQUdObXl4WnJxWG1oYUl4QnU1eXhPRHBJNldtSzRGa1lBNklzZGlFUWNWNmQ9czk2LWMiLCJnaXZlbl9uYW1lIjoiSm9obiIsImZhbWlseV9uYW1lIjoiRG9lIiwibG9jYWxlIjoiZW4iLCJpYXQiOjE2ODg5MjI2MTAsImV4cCI6MTY4ODkyNjIxMH0."
                        "signature"
                    ),
                },
            ],
        },
    )


class RefreshTokenRequest(BaseModel):
    """リフレッシュトークンによるアクセストークン更新リクエストデータを表すモデル。"""

    refresh_token: str = Field(
        ...,
        description="リフレッシュトークン（UUIDベース）",
        examples=["b8f7c2a1-5e3d-4b9e-8f7a-2c5e9d6b3a8f"],
    )

    @field_validator("refresh_token")
    @classmethod
    def validate_refresh_token(cls, v: str) -> str:
        """リフレッシュトークンの基本的な形式チェック"""
        if not v.strip():
            raise ValueError("リフレッシュトークンは空にできません")
        # UUID形式の基本チェック
        import re

        uuid_pattern = r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
        if not re.match(uuid_pattern, v.strip().lower()):
            raise ValueError("無効なリフレッシュトークン形式です")
        return v.strip()


class TokenPairResponse(BaseModel):
    """アクセストークンとリフレッシュトークンのペアレスポンスデータを表すモデル。"""

    access_token: str = Field(
        ...,
        description="JWTアクセストークン（15分有効）",
        examples=[TestData.DOC_JWT_TOKEN_EXAMPLE],
    )
    refresh_token: str = Field(
        ...,
        description="リフレッシュトークン（30日有効）",
        examples=["b8f7c2a1-5e3d-4b9e-8f7a-2c5e9d6b3a8f"],
    )
    token_type: str = Field(
        "bearer",
        description="トークンタイプ",
        examples=["bearer"],
    )
    expires_in: int = Field(
        ...,
        description="アクセストークンの有効期限（秒）",
        examples=[900],  # 15分
    )


class PasswordChangeRequest(BaseModel):
    """パスワード変更リクエストデータを表すモデル。"""

    current_password: str = Field(
        ...,
        description="現在のパスワード",
        examples=[TestData.DOC_PASSWORD_EXAMPLE],
    )
    new_password: str = Field(
        ...,
        min_length=8,
        description="新しいパスワード (8文字以上、英数字記号を含む)",
        examples=[TestData.DOC_NEW_PASSWORD],
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

    @field_validator("current_password")
    @classmethod
    def validate_current_password(cls, v: str) -> str:
        """現在のパスワードの基本チェック"""
        if not v.strip():
            raise ValueError("現在のパスワードは空にできません")
        return v.strip()

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "current_password": "Password123456+-",
                    "new_password": "NewPassword789!@#",
                },
            ],
        },
    )


class ProfileResponse(BaseModel):
    """プロフィール情報のレスポンスデータを表すモデル。"""

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
    profile_image_url: str | None = Field(
        None,
        description="プロフィール画像URL",
        examples=["https://example.com/profile/user123.jpg"],
    )
    is_google_user: bool = Field(
        ...,
        description="Googleアカウントでログインしたユーザーかどうか",
        examples=[False, True],
    )
    created_at: datetime = Field(
        ...,
        description="アカウント作成日時",
        examples=["2025-01-01T00:00:00+09:00"],
    )
    updated_at: datetime = Field(
        ...,
        description="最終更新日時",
        examples=["2025-07-22T12:00:00+09:00"],
    )

    model_config = ConfigDict(from_attributes=True)


class AdvancedUserUpdate(BaseModel):
    """高度なユーザー情報更新リクエストデータを表すモデル。"""

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
    profile_image_url: str | None = Field(
        None,
        max_length=500,
        description="プロフィール画像URL（任意・500文字以内）",
        examples=["https://example.com/profile/user123.jpg"],
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

    @field_validator("profile_image_url")
    @classmethod
    def validate_profile_image_url(cls, v: str | None) -> str | None:
        """プロフィール画像URLの基本チェック"""
        if v is not None:
            import re

            # URLの基本形式チェック
            url_pattern = r"^https?://[^\s/$.?#].[^\s]*$"
            if not re.match(url_pattern, v.strip()):
                raise ValueError("無効なURL形式です")
            return v.strip()
        return None

    model_config = ConfigDict(from_attributes=True)


class SessionInfoResponse(BaseModel):
    """セッション情報のレスポンスデータを表すモデル。"""

    refresh_token: str = Field(
        ...,
        description="リフレッシュトークン（UUIDベース）",
        examples=["b8f7c2a1-5e3d-4b9e-8f7a-2c5e9d6b3a8f"],
    )
    created_at: str = Field(
        ...,
        description="セッション作成日時（ISO形式）",
        examples=["2025-07-22T10:30:00+09:00"],
    )
    last_used: str = Field(
        ...,
        description="最終使用日時（ISO形式）",
        examples=["2025-07-22T12:15:00+09:00"],
    )
    device_info: dict[str, str] = Field(
        ...,
        description="デバイス情報",
        examples=[{"device_id": "device-uuid-12345", "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36", "ip_address": "192.168.1.100", "platform": "windows"}],
    )


class UserSessionsResponse(BaseModel):
    """ユーザーセッション一覧のレスポンスデータを表すモデル。"""

    user_email: str = Field(
        ...,
        description="ユーザーメールアドレス",
        examples=["user@example.com"],
    )
    session_count: int = Field(
        ...,
        description="アクティブセッション数",
        examples=[3],
    )
    sessions: list[SessionInfoResponse] = Field(
        ...,
        description="セッション情報のリスト",
    )


class RevokeSessionRequest(BaseModel):
    """セッション無効化リクエストデータを表すモデル。"""

    device_id: str = Field(
        ...,
        description="無効化対象のデバイスID",
        examples=["device-uuid-12345"],
    )

    @field_validator("device_id")
    @classmethod
    def validate_device_id(cls, v: str) -> str:
        """デバイスIDの基本チェック"""
        if not v.strip():
            raise ValueError("デバイスIDは空にできません")
        return v.strip()


class ProfileImageUploadRequest(BaseModel):
    """プロフィール画像アップロードリクエストデータを表すモデル。"""

    image_data: str = Field(
        ...,
        description="Base64エンコードされた画像データ",
        examples=["data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEAAA..."],
    )
    filename: str = Field(
        ...,
        max_length=255,
        description="アップロードファイル名",
        examples=["profile_image.jpg", "avatar.png"],
    )

    @field_validator("image_data")
    @classmethod
    def validate_image_data(cls, v: str) -> str:
        """Base64画像データの基本検証"""
        if not v.strip():
            raise ValueError("画像データは空にできません")

        # Base64データURLの基本形式チェック
        if not v.startswith("data:image/"):
            raise ValueError("無効な画像データ形式です")

        # サポートされる画像形式のチェック
        supported_formats = ["data:image/jpeg", "data:image/jpg", "data:image/png", "data:image/webp"]
        if not any(v.startswith(fmt) for fmt in supported_formats):
            raise ValueError("サポートされていない画像形式です（JPEG, PNG, WebPのみ対応）")

        # Base64データ部分の存在確認
        if ";base64," not in v:
            raise ValueError("Base64エンコードされた画像データが必要です")

        return v.strip()

    @field_validator("filename")
    @classmethod
    def validate_filename(cls, v: str) -> str:
        """ファイル名の基本検証"""
        if not v.strip():
            raise ValueError("ファイル名は空にできません")

        # 拡張子チェック
        import re

        valid_extensions = r"\.(jpg|jpeg|png|webp)$"
        if not re.search(valid_extensions, v.lower()):
            raise ValueError("サポートされていないファイル拡張子です（.jpg, .jpeg, .png, .webpのみ対応）")

        # 危険な文字のチェック
        dangerous_chars = r"[<>:\"/\\|?*]"
        if re.search(dangerous_chars, v):
            raise ValueError("ファイル名に無効な文字が含まれています")

        return v.strip()

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "image_data": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEAAA...",
                    "filename": "profile_image.jpg",
                },
                {
                    "image_data": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...",
                    "filename": "avatar.png",
                },
            ],
        },
    )


class ProfileImageUploadResponse(BaseModel):
    """プロフィール画像アップロードレスポンスデータを表すモデル。"""

    image_url: str = Field(
        ...,
        description="アップロードされた画像のURL",
        examples=["https://example.com/profile/12345/profile_image.jpg"],
    )
    file_size: int = Field(
        ...,
        description="アップロードされた画像のファイルサイズ（バイト）",
        examples=[1024000],
    )
    image_dimensions: dict[str, int] = Field(
        ...,
        description="画像の寸法情報",
        examples=[{"width": 512, "height": 512}],
    )
    upload_timestamp: str = Field(
        ...,
        description="アップロード完了日時（ISO形式）",
        examples=["2025-07-22T12:30:00+09:00"],
    )

    model_config = ConfigDict(from_attributes=True)


class AccountLinkingRequest(BaseModel):
    """アカウント連携リクエストデータを表すモデル。"""

    link_type: str = Field(
        ...,
        description="連携タイプ（google_to_email または email_to_google）",
        examples=["google_to_email", "email_to_google"],
    )
    password: str | None = Field(
        None,
        min_length=8,
        description="メールアカウント用パスワード（email_to_googleの場合は必須）",
        examples=["SecurePassword123!"],
    )
    google_id_token: str | None = Field(
        None,
        description="GoogleのIDトークン（google_to_emailの場合は必須）",
        examples=["eyJhbGciOiJSUzI1NiIsImtpZCI6IjE2NzAy..."],
    )

    @field_validator("link_type")
    @classmethod
    def validate_link_type(cls, v: str) -> str:
        """連携タイプの検証"""
        valid_types = ["google_to_email", "email_to_google"]
        if v not in valid_types:
            raise ValueError(f"無効な連携タイプです。{valid_types}のいずれかを指定してください")
        return v

    @field_validator("password")
    @classmethod
    def validate_password_for_linking(cls, v: str | None, info) -> str | None:
        """連携タイプに応じたパスワード検証"""
        if info.data.get("link_type") == "email_to_google":
            if not v:
                raise ValueError("email_to_google連携にはパスワードが必要です")
            # パスワード複雑性チェック
            if len(v) < 8:
                raise ValueError("パスワードは8文字以上である必要があります")
            if not any(c.islower() for c in v):
                raise ValueError("パスワードに小文字を含めてください")
            if not any(c.isupper() for c in v):
                raise ValueError("パスワードに大文字を含めてください")
            if not any(c.isdigit() for c in v):
                raise ValueError("パスワードに数字を含めてください")
        return v

    @field_validator("google_id_token")
    @classmethod
    def validate_google_id_token_for_linking(cls, v: str | None, info) -> str | None:
        """連携タイプに応じたGoogleトークン検証"""
        if info.data.get("link_type") == "google_to_email":
            if not v:
                raise ValueError("google_to_email連携にはGoogleトークンが必要です")
            # JWTトークンの基本形式チェック
            parts = v.split(".")
            if len(parts) != 3:
                raise ValueError("無効なJWTトークン形式です")
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "link_type": "google_to_email",
                    "google_id_token": "eyJhbGciOiJSUzI1NiIsImtpZCI6IjE2NzAy...",
                },
                {
                    "link_type": "email_to_google",
                    "password": "SecurePassword123!",
                },
            ],
        },
    )


class AccountLinkingResponse(BaseModel):
    """アカウント連携レスポンスデータを表すモデル。"""

    link_status: str = Field(
        ...,
        description="連携ステータス（linked, pending, failed）",
        examples=["linked", "pending", "failed"],
    )
    linked_accounts: list[str] = Field(
        ...,
        description="連携済みアカウントタイプ一覧",
        examples=[["email", "google"], ["email"]],
    )
    primary_account: str = Field(
        ...,
        description="プライマリアカウントタイプ",
        examples=["email", "google"],
    )
    message: str = Field(
        ...,
        description="連携結果メッセージ",
        examples=["アカウント連携が完了しました", "連携処理中です", "連携に失敗しました"],
    )
    next_steps: list[str] | None = Field(
        None,
        description="次に行うべき手順（必要に応じて）",
        examples=[["メール認証を完了してください"], ["Googleアカウントで再ログインしてください"]],
    )

    model_config = ConfigDict(from_attributes=True)


class AdminUserResponse(BaseModel):
    """管理者用ユーザー情報レスポンスデータを表すモデル。"""

    user_id: str = Field(
        ...,
        description="ユーザーID（UUID）",
        examples=["12345678-1234-1234-1234-123456789012"],
    )
    email: EmailStr = Field(
        ...,
        description="ユーザーのメールアドレス",
        examples=[TestData.DOC_EMAIL_EXAMPLE],
    )
    username: str = Field(
        ...,
        description="ユーザー名",
        examples=[TestData.DOC_USERNAME_EXAMPLE],
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
    created_at: datetime = Field(
        ...,
        description="アカウント作成日時",
        examples=["2025-01-01T00:00:00+09:00"],
    )
    updated_at: datetime = Field(
        ...,
        description="最終更新日時",
        examples=["2025-07-22T12:00:00+09:00"],
    )
    deleted_at: datetime | None = Field(
        None,
        description="削除日時（論理削除時のみ）",
        examples=["2025-12-31T23:59:59+09:00"],
    )

    model_config = ConfigDict(from_attributes=True)


class AdminUserListResponse(BaseModel):
    """管理者用ユーザー一覧レスポンスデータを表すモデル。"""

    total_count: int = Field(
        ...,
        description="全ユーザー数",
        examples=[150],
    )
    page: int = Field(
        ...,
        description="現在のページ番号",
        examples=[1],
    )
    page_size: int = Field(
        ...,
        description="1ページあたりの件数",
        examples=[20],
    )
    users: list[AdminUserResponse] = Field(
        ...,
        description="ユーザー情報のリスト",
    )

    model_config = ConfigDict(from_attributes=True)


class AdminUserUpdateRequest(BaseModel):
    """管理者用ユーザー情報更新リクエストデータを表すモデル。"""

    email: EmailStr | None = Field(
        None,
        description="新しいメールアドレス（任意）",
        examples=[TestData.DOC_NEW_USER_EMAIL],
    )
    username: str | None = Field(
        None,
        max_length=50,
        min_length=3,
        description="新しいユーザー名（任意・3-50文字）",
        examples=[TestData.DOC_NEW_USERNAME],
    )
    user_role: int | None = Field(
        None,
        description="ユーザー権限（任意）",
        examples=[User.ROLE_FREE, User.ROLE_ADMIN],
    )
    user_status: int | None = Field(
        None,
        description="アカウント状態（任意）",
        examples=[User.STATUS_ACTIVE, User.STATUS_SUSPENDED],
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

    @field_validator("user_role")
    @classmethod
    def validate_user_role(cls, v: int | None) -> int | None:
        """ユーザー権限の妥当性チェック"""
        if v is not None:
            valid_roles = [User.ROLE_GUEST, User.ROLE_FREE, User.ROLE_REGULAR, User.ROLE_ADMIN, User.ROLE_OWNER]
            if v not in valid_roles:
                raise ValueError(f"無効なユーザー権限です。{valid_roles}のいずれかを指定してください")
        return v

    @field_validator("user_status")
    @classmethod
    def validate_user_status(cls, v: int | None) -> int | None:
        """ユーザー状態の妥当性チェック"""
        if v is not None:
            valid_statuses = [User.STATUS_ACTIVE, User.STATUS_SUSPENDED]
            if v not in valid_statuses:
                raise ValueError(f"無効なユーザー状態です。{valid_statuses}のいずれかを指定してください")
        return v

    @field_validator("contact_number")
    @classmethod
    def validate_contact_number(cls, v: str | None) -> str | None:
        """電話番号の基本的な形式チェック"""
        if v is not None:
            import re

            if not re.match(r"^[0-9+\-\s\(\)]+$", v.strip()):
                raise ValueError("電話番号に無効な文字が含まれています")
            return v.strip()
        return None

    model_config = ConfigDict(from_attributes=True)
