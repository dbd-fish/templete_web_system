"""
セキュリティ機能（FastAPI公式テンプレート準拠）
"""

from datetime import datetime, timedelta
from typing import Any

import jwt
from passlib.context import CryptContext

from app.core.config import settings

# パスワード暗号化コンテキスト
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = "HS256"


def create_access_token(subject: str | Any, expires_delta: timedelta | None = None) -> str:
    """
    JWTアクセストークンを作成
    
    Args:
        subject: トークンの主体（通常はユーザーID）
        expires_delta: 有効期限（指定なしの場合はデフォルト値）
        
    Returns:
        str: エンコードされたJWTトークン
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    平文パスワードとハッシュ化パスワードを照合
    
    Args:
        plain_password: 平文パスワード
        hashed_password: ハッシュ化パスワード
        
    Returns:
        bool: パスワードが一致するかどうか
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    パスワードをハッシュ化
    
    Args:
        password: 平文パスワード
        
    Returns:
        str: ハッシュ化されたパスワード
    """
    return pwd_context.hash(password)


def decode_token(token: str) -> dict[str, Any]:
    """
    JWTトークンをデコード
    
    Args:
        token: JWTトークン
        
    Returns:
        dict: デコードされたペイロード
        
    Raises:
        jwt.JWTError: トークンが無効な場合
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[ALGORITHM]
        )
        return payload
    except jwt.JWTError:
        raise