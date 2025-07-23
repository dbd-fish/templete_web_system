"""Google OAuth 2.0認証機能モジュール"""

import structlog
from google.auth.transport import requests
from google.oauth2 import id_token
from pydantic import BaseModel

from api.common.setting import setting

logger = structlog.get_logger()


class GoogleUserInfo(BaseModel):
    """GoogleからのユーザーIDトークンをデコードしたユーザー情報"""

    email: str
    name: str
    given_name: str | None = None
    family_name: str | None = None
    picture: str | None = None
    email_verified: bool = False
    locale: str | None = None
    sub: str  # Google unique identifier


async def verify_google_id_token(id_token_str: str) -> GoogleUserInfo:
    """
    Google IDトークンを検証してユーザー情報を取得する

    Args:
        id_token_str: GoogleからのIDトークン

    Returns:
        GoogleUserInfo: 検証済みのユーザー情報

    Raises:
        ValueError: IDトークンの検証に失敗した場合
        Exception: その他のエラー
    """
    logger.info("verify_google_id_token - start")

    try:
        # Google APIでIDトークンを検証
        idinfo = id_token.verify_oauth2_token(id_token_str, requests.Request(), setting.GOOGLE_CLIENT_ID)

        # issuerの確認
        if idinfo["iss"] not in ["accounts.google.com", "https://accounts.google.com"]:
            logger.error("verify_google_id_token - invalid issuer", issuer=idinfo.get("iss"))
            raise ValueError("無効なトークン発行者です")

        # audienceの確認
        if idinfo["aud"] != setting.GOOGLE_CLIENT_ID:
            logger.error("verify_google_id_token - invalid audience", expected=setting.GOOGLE_CLIENT_ID, actual=idinfo.get("aud"))
            raise ValueError("無効なクライアントIDです")

        # 必須フィールドの確認
        if not idinfo.get("email"):
            logger.error("verify_google_id_token - missing email")
            raise ValueError("メールアドレスが取得できませんでした")

        if not idinfo.get("email_verified", False):
            logger.error("verify_google_id_token - email not verified", email=idinfo.get("email"))
            raise ValueError("メールアドレスが認証されていません")

        # GoogleUserInfoオブジェクトを作成
        user_info = GoogleUserInfo(
            email=idinfo["email"],
            name=idinfo.get("name", idinfo["email"]),
            given_name=idinfo.get("given_name"),
            family_name=idinfo.get("family_name"),
            picture=idinfo.get("picture"),
            email_verified=idinfo.get("email_verified", False),
            locale=idinfo.get("locale"),
            sub=idinfo["sub"],
        )

        logger.info("verify_google_id_token - success", email=user_info.email, name=user_info.name, sub=user_info.sub)

        return user_info

    except ValueError as e:
        logger.error("verify_google_id_token - validation error", error=str(e))
        raise
    except Exception as e:
        logger.error("verify_google_id_token - unexpected error", error=str(e), error_type=type(e).__name__)
        raise ValueError(f"IDトークンの検証に失敗しました: {str(e)}") from e
    finally:
        logger.info("verify_google_id_token - end")


def generate_username_from_google_info(google_user_info: GoogleUserInfo) -> str:
    """
    GoogleユーザーIDとメールアドレスからユーザー名を生成する

    Args:
        google_user_info: GoogleからのユーザーIDトークン情報

    Returns:
        str: 生成されたユーザー名
    """
    logger.info("generate_username_from_google_info - start", email=google_user_info.email)

    try:
        # メールアドレスのローカル部分をベースにする
        email_local = google_user_info.email.split("@")[0]

        # 名前情報からユーザー名を生成
        if google_user_info.given_name and google_user_info.family_name:
            base_name = f"{google_user_info.given_name}_{google_user_info.family_name}".replace(" ", "_")
        elif google_user_info.given_name:
            base_name = google_user_info.given_name.replace(" ", "_")
        elif google_user_info.name and google_user_info.name.strip():
            base_name = google_user_info.name.replace(" ", "_")
        else:
            base_name = email_local

        # 英数字以外は除去し、50文字以内に制限
        import re

        username = re.sub(r"[^a-zA-Z0-9]", "", base_name)[:50]

        # 空の場合はGoogleのsubを使用
        if not username:
            username = f"google_user_{google_user_info.sub[:10]}"

        logger.info("generate_username_from_google_info - success", generated_username=username, original_email=google_user_info.email)

        return username

    except Exception as e:
        logger.error("generate_username_from_google_info - error", error=str(e), error_type=type(e).__name__)
        # フォールバック: Googleのsubを使用
        fallback_username = f"google_user_{google_user_info.sub[:10]}"
        logger.info("generate_username_from_google_info - fallback", username=fallback_username)
        return fallback_username
    finally:
        logger.info("generate_username_from_google_info - end")
