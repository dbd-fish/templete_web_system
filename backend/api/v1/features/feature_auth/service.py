"""
認証関連のサービス層
ビジネスロジック、認証、メール送信など
"""

import uuid
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import structlog
from fastapi import BackgroundTasks, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.common.database import get_db
from api.common.setting import setting
from api.v1.features.feature_auth import crud
from api.v1.features.feature_auth.schemas.user import UserCreate, UserResponse
from api.v1.features.feature_auth.security import create_access_token, decode_access_token, hash_password
from api.v1.features.feature_auth.send_reset_password_email import send_reset_password_email
from api.v1.features.feature_auth.send_verification_email import send_verification_email
from api.v1.models.user import User

logger = structlog.get_logger()


async def get_current_user(request: Request, db: AsyncSession = Depends(get_db)) -> User:
    """現在ログイン中のユーザーを取得します。

    Args:
        request (Request): リクエストオブジェクト（クッキーからトークンを取得）。
        db (AsyncSession): 非同期データベースセッション。

    Returns:
        User: 現在ログイン中のユーザー。

    Raises:
        HTTPException: 認証に失敗した場合。
    """
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="認証情報が無効です", headers={"WWW-Authenticate": "Bearer"})

    # クッキーからトークンを取得
    token = request.cookies.get("authToken")
    if not token:
        raise credentials_exception

    try:
        # トークンからユーザーIDを取得
        payload = decode_access_token(token)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except Exception:
        raise credentials_exception

    # データベースからユーザーを取得
    user = await crud.get_user_by_id(db, user_id=user_id)
    if user is None:
        raise credentials_exception

    return user


async def create_user(email: str, username: str, password: str, db: AsyncSession) -> User:
    """新しいユーザーを作成します。

    Args:
        email (str): メールアドレス。
        username (str): ユーザー名。
        password (str): パスワード。
        db (AsyncSession): 非同期データベースセッション。

    Returns:
        User: 作成されたユーザー。
    """
    hashed_password = hash_password(password)
    
    new_user = User(
        user_id=str(uuid.uuid4()),
        email=email,
        username=username,
        hashed_password=hashed_password,
        user_status=User.STATUS_ACTIVE,
        created_at=datetime.now(ZoneInfo("Asia/Tokyo")),
        updated_at=datetime.now(ZoneInfo("Asia/Tokyo"))
    )
    
    return await crud.create_user(db, new_user)


async def temporary_create_user(user: UserCreate, background_tasks: BackgroundTasks, db: AsyncSession) -> None:
    """仮登録用のメール認証トークンを送信します。

    Args:
        user (UserCreate): ユーザー登録情報。
        background_tasks (BackgroundTasks): バックグラウンドタスク。
        db (AsyncSession): 非同期データベースセッション。
    """
    # メール認証トークンを生成
    token_data = {"email": user.email, "username": user.username, "password": user.password}
    verification_token = create_access_token(data=token_data, expires_delta=timedelta(hours=24))
    
    # バックグラウンドでメール送信
    background_tasks.add_task(send_verification_email, user.email, verification_token)


async def verify_email_token(token: str) -> UserCreate:
    """メール認証トークンを検証してユーザー情報を取得します。

    Args:
        token (str): メール認証トークン。

    Returns:
        UserCreate: トークンから取得したユーザー情報。

    Raises:
        HTTPException: トークンが無効な場合。
    """
    try:
        payload = decode_access_token(token)
        email: str = payload.get("email")
        username: str = payload.get("username")
        password: str = payload.get("password")
        
        if email is None or username is None or password is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="無効な認証トークンです")
            
        return UserCreate(email=email, username=username, password=password)
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="無効な認証トークンです")


async def reset_password_email(email: str, background_tasks: BackgroundTasks, db: AsyncSession) -> None:
    """パスワードリセット用のメールを送信します。

    Args:
        email (str): メールアドレス。
        background_tasks (BackgroundTasks): バックグラウンドタスク。
        db (AsyncSession): 非同期データベースセッション。
    """
    # ユーザーの存在確認
    user = await crud.get_user_by_email(db, email)
    if user:
        # パスワードリセットトークンを生成
        reset_token = create_access_token(data={"email": email}, expires_delta=timedelta(hours=1))
        
        # バックグラウンドでメール送信
        background_tasks.add_task(send_reset_password_email, email, reset_token)


async def decode_password_reset_token(token: str) -> str:
    """パスワードリセットトークンを検証してメールアドレスを取得します。

    Args:
        token (str): パスワードリセットトークン。

    Returns:
        str: トークンから取得したメールアドレス。

    Raises:
        HTTPException: トークンが無効な場合。
    """
    try:
        payload = decode_access_token(token)
        email: str = payload.get("email")
        
        if email is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="無効なリセットトークンです")
            
        return email
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="無効なリセットトークンです")


async def reset_password(email: str, new_password: str, db: AsyncSession) -> None:
    """パスワードをリセットします。

    Args:
        email (str): メールアドレス。
        new_password (str): 新しいパスワード。
        db (AsyncSession): 非同期データベースセッション。

    Raises:
        HTTPException: ユーザーが見つからない場合。
    """
    user = await crud.get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ユーザーが見つかりません")
    
    hashed_password = hash_password(new_password)
    await crud.update_user_password(db, user, hashed_password)