from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import structlog
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from passlib.context import CryptContext
from sqlalchemy.future import select

from app.common.database import AsyncSession
from app.common.setting import setting
from app.models.user import User

# ログの設定
logger = structlog.get_logger()

# 環境変数に適切に置き換える
SECRET_KEY = setting.SECRET_KEY  # JWTの署名に使用する秘密鍵
ALGORITHM = setting.ALGORITHM  # JWTの暗号化アルゴリズム
ACCESS_TOKEN_EXPIRE_MINUTES = setting.ACCESS_TOKEN_EXPIRE_MINUTES  # アクセストークンの有効期限（分単位）

# パスワード暗号化設定
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# トークンのエンドポイント（FastAPIのOAuth2PasswordBearerを使用）
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

def hash_password(password: str) -> str:
    """パスワードをハッシュ化する。

    Args:
        password (str): プレーンパスワード。

    Returns:
        str: ハッシュ化されたパスワード。

    """
    logger.info("hash_password - start")
    try:
        hashed_password = pwd_context.hash(password)
        logger.info("hash_password - end")
        return hashed_password
    finally:
        logger.info("hash_password - end")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """プレーンパスワードとハッシュ化されたパスワードを比較して検証する。

    Args:
        plain_password (str): プレーンパスワード。
        hashed_password (str): ハッシュ化されたパスワード。

    Returns:
        bool: 検証結果（True: 一致, False: 不一致）。

    """
    logger.info("verify_password - start", plain_password=plain_password, hashed_password=hashed_password)
    try:
        result = pwd_context.verify(plain_password, hashed_password)
        logger.info("verify_password - end", result=result)
        return result
    finally:
        logger.info("verify_password - end")

# TODO: 関数名を汎用的なものに変更する
def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """アクセストークンを作成する。また仮登録時のトークンも作成する。

    Args:
        data (dict): トークンに含めるデータ。
        expires_delta (timedelta, optional): トークンの有効期限。

    Returns:
        str: 作成されたJWTアクセストークン。

    """
    logger.info("create_access_token - start", data=data, expires_delta=expires_delta)
    try:
        to_encode = data.copy()
        expire = datetime.now(ZoneInfo("Asia/Tokyo")) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
        to_encode.update({"exp": expire})
        logger.debug("create_access_token - to_encode", to_encode=to_encode)
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        logger.info("create_access_token - success", encoded_jwt=encoded_jwt)
        logger.info("create_access_token - expire", expire=expire)
        return encoded_jwt
    finally:
        logger.info("create_access_token - end")

# TODO: 関数名を汎用的なものに変更する
def decode_access_token(token: str) -> dict:
    """アクセストークンをデコードしてペイロードを取得する。また仮登録時のトークンもデコードする。

    Args:
        token (str): デコード対象のJWTアクセストークン。

    Returns:
        dict: デコードされたペイロード情報。

    Raises:
        HTTPException: トークンが無効または不正な場合。

    """
    logger.info("decode_access_token - start", token=token)
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])  # トークンをデコード
        logger.info("decode_access_token - success", payload=payload)
        return payload
    finally:
        logger.info("decode_access_token - end")

async def authenticate_user(email: str, password: str, db: AsyncSession) -> User:
    """メールアドレスとパスワードを使用してユーザー認証を行う。

    Args:
        email (str): ユーザーのメールアドレス。
        password (str): プレーンパスワード。
        db (AsyncSession): データベースセッション。

    Returns:
        User: 認証に成功したユーザーオブジェクト。

    Raises:
        HTTPException: 認証に失敗した場合。

    """
    logger.info("authenticate_user - start", email=email)
    query = select(User).where(
        User.email == email,
        User.user_status == User.STATUS_ACTIVE,
        User.deleted_at.is_(None),
    )
    result = await db.execute(query)
    user = result.scalars().first()  # 検索結果を取得
    if not user:
        logger.info("authenticate_user - user not found", email=email)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not verify_password(password, user.hashed_password):
        logger.info("authenticate_user - incorrect password", email=email)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    logger.info("authenticate_user - success", user_id=user.user_id)
    logger.info("authenticate_user - end")
    return user
