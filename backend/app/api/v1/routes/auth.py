"""
認証API（FastAPI公式テンプレート準拠）
"""

import structlog
from typing import Annotated
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import SessionDep
from app.api.v1.models import UserCreate, UserResponse, Token, TokenData, SendPasswordResetEmailData, PasswordResetData
from app.api.v1.core.security import create_access_token
from app.api.v1 import crud

# 既存の機能を段階的移行期間中は継続使用
from app.api.v1.features.feature_auth.auth_service import (
    decode_password_reset_token,
    reset_password_email,
    temporary_create_user,
    verify_email_token
)

# ログの設定
logger = structlog.get_logger()

router = APIRouter()


@router.post("/signup", response_model=dict)
async def register_user(
    token_data: TokenData,
    session: SessionDep
) -> dict:
    """
    新しいユーザーを登録（メール認証後）
    
    Args:
        token_data: メール認証トークン
        session: データベースセッション
        
    Returns:
        dict: 登録成功メッセージ
    """
    logger.info("register_user - start")
    try:
        # トークンからユーザー情報を取得
        user_info = await verify_email_token(token_data.token)
        logger.info("register_user - user_info", user_info=user_info)
        
        # メール重複チェック
        if await crud.check_email_exists(session=session, email=user_info.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # ユーザー作成データ準備
        user_create = UserCreate(
            email=user_info.email,
            username=user_info.username,
            password=user_info.password
        )
        
        # ユーザー作成
        new_user = await crud.create_user(session=session, user_create=user_create)
        logger.info("register_user - success", user_id=new_user.user_id)
        
        return {"msg": "User created successfully", "user_id": str(new_user.user_id)}
    finally:
        logger.info("register_user - end")


@router.post("/send-verify-email", response_model=dict)
async def send_verify_email(
    user: UserCreate,
    background_tasks: BackgroundTasks,
    session: SessionDep
) -> dict:
    """
    仮登録用メールを送信
    
    Args:
        user: ユーザー登録情報
        background_tasks: バックグラウンドタスク
        session: データベースセッション
        
    Returns:
        dict: 送信成功メッセージ
    """
    logger.info("send_verify_email - start", email=user.email, username=user.username)
    try:
        # メール重複チェック
        if await crud.check_email_exists(session=session, email=user.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # 段階的移行: 既存の仮登録機能を使用
        await temporary_create_user(user=user, background_tasks=background_tasks, db=session)
        logger.info("send_verify_email - success")
        
        return {"msg": "Verification email sent successfully"}
    finally:
        logger.info("send_verify_email - end")


@router.post("/login", response_model=dict)
async def login(
    request: Request,
    response: Response,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: SessionDep
) -> dict:
    """
    ログイン処理
    
    Args:
        request: リクエストオブジェクト
        response: レスポンスオブジェクト
        form_data: ログインフォームデータ
        session: データベースセッション
        
    Returns:
        dict: ログイン成功メッセージ
    """
    logger.info("login - start", username=form_data.username)
    try:
        # ユーザー認証
        user = await crud.authenticate_user(
            session=session,
            email=form_data.username,
            password=form_data.password
        )
        
        if not user:
            logger.info("login - authentication failed", username=form_data.username)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # クライアントIP取得
        client_host = (
            request.headers.get("X-Forwarded-For")
            or (request.client.host if request.client else "unknown")
        )
        
        # アクセストークン生成
        access_token = create_access_token(subject=str(user.user_id))
        logger.info("login - success", user_id=user.user_id)
        
        # HttpOnlyクッキーとしてトークンを設定
        response.set_cookie(
            key="authToken",
            value=access_token,
            httponly=True,
            max_age=60 * 60 * 3,  # 3時間
            secure=True,
            samesite="lax"
        )
        
        return {"message": "Login successful"}
    finally:
        logger.info("login - end")


@router.post("/logout")
async def logout() -> dict:
    """
    ログアウト処理
    
    Returns:
        dict: ログアウト成功メッセージ
    """
    logger.info("logout - start")
    try:
        # クライアント側でトークンを削除するシンプルな処理
        logger.info("logout - success")
        return {"msg": "Logged out successfully"}
    finally:
        logger.info("logout - end")


@router.post("/send-password-reset-email", response_model=dict)
async def send_reset_password_email(
    data: SendPasswordResetEmailData,
    background_tasks: BackgroundTasks,
    session: SessionDep
) -> dict:
    """
    パスワードリセットメール送信
    
    Args:
        data: メール送信データ
        background_tasks: バックグラウンドタスク
        session: データベースセッション
        
    Returns:
        dict: 送信成功メッセージ
    """
    logger.info("send_reset_password_email - start", email=data.email)
    try:
        # 段階的移行: 既存のリセット機能を使用
        await reset_password_email(
            email=data.email,
            background_tasks=background_tasks,
            db=session
        )
        logger.info("send_reset_password_email - success", email=data.email)
        
        return {"msg": "Password reset email sent successfully"}
    finally:
        logger.info("send_reset_password_email - end")


@router.post("/reset-password", response_model=dict)
async def reset_password(
    reset_data: PasswordResetData,
    session: SessionDep
) -> dict:
    """
    パスワードリセット処理
    
    Args:
        reset_data: パスワードリセットデータ
        session: データベースセッション
        
    Returns:
        dict: リセット成功メッセージ
    """
    logger.info("reset_password - start")
    try:
        # トークンからメールアドレスを取得
        email = await decode_password_reset_token(reset_data.token)
        
        # ユーザー取得
        user = await crud.get_user_by_email(session=session, email=email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # パスワード更新
        await crud.update_user_password(
            session=session,
            user=user,
            new_password=reset_data.new_password
        )
        
        logger.info("reset_password - success")
        return {"msg": "Password reset successfully"}
    finally:
        logger.info("reset_password - end")