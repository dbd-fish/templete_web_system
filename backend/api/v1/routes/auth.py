"""
認証API（FastAPI公式テンプレート準拠）
"""

import structlog
from typing import Annotated
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from api.v1.common.database import get_db
from api.v1.features.feature_auth.schemas.user import UserCreate, UserResponse, Token, TokenData, SendPasswordResetEmailData, PasswordResetData
from api.v1.features.feature_auth.security import create_access_token

from api.v1.features.feature_auth.auth_service import (
    create_user,
    decode_password_reset_token,
    reset_password,
    reset_password_email,
    temporary_create_user,
    verify_email_token
)
from api.v1.features.feature_auth.security import authenticate_user
from api.v1.features.feature_auth.auth_repository import UserRepository
from ..common.response_schemas import (
    create_success_response,
    SuccessResponse,
    ErrorCodes
)
from ..common.exception_handlers import BusinessLogicError

# ログの設定
logger = structlog.get_logger()

router = APIRouter()


@router.post("/signup", response_model=SuccessResponse[dict])
async def register_user(
    token_data: TokenData,
    session: AsyncSession = Depends(get_db)
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
        existing_user = await UserRepository.get_user_by_email(session, user_info.email)
        if existing_user:
            raise BusinessLogicError(
                message="このメールアドレスは既に登録されています",
                error_code=ErrorCodes.RESOURCE_ALREADY_EXISTS
            )
        
        # ユーザー作成
        new_user = await create_user(user_info.email, user_info.username, user_info.password, session)
        logger.info("register_user - success", user_id=new_user.user_id)
        
        return create_success_response(
            message="ユーザー登録が正常に完了しました",
            data={"user_id": str(new_user.user_id)}
        )
    finally:
        logger.info("register_user - end")


@router.post("/send-verify-email", response_model=SuccessResponse[None])
async def send_verify_email(
    user: UserCreate,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_db)
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
        existing_user = await UserRepository.get_user_by_email(session, user.email)
        if existing_user:
            raise BusinessLogicError(
                message="このメールアドレスは既に登録されています",
                error_code=ErrorCodes.RESOURCE_ALREADY_EXISTS
            )
        
        # 段階的移行: 既存の仮登録機能を使用
        await temporary_create_user(user=user, background_tasks=background_tasks, db=session)
        logger.info("send_verify_email - success")
        
        return create_success_response(
            message="認証用メールを送信しました"
        )
    finally:
        logger.info("send_verify_email - end")


@router.post("/login", response_model=SuccessResponse[None])
async def login(
    request: Request,
    response: Response,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: AsyncSession = Depends(get_db)
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
        user = await authenticate_user(
            email=form_data.username,
            password=form_data.password,
            db=session
        )
        
        if not user:
            logger.info("login - authentication failed", username=form_data.username)
            raise BusinessLogicError(
                message="ユーザー名またはパスワードが正しくありません",
                error_code=ErrorCodes.AUTHENTICATION_FAILED
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
        
        return create_success_response(
            message="ログインが正常に完了しました"
        )
    finally:
        logger.info("login - end")


@router.post("/logout", response_model=SuccessResponse[None])
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
        return create_success_response(
            message="ログアウトが正常に完了しました"
        )
    finally:
        logger.info("logout - end")


@router.post("/send-password-reset-email", response_model=SuccessResponse[None])
async def send_reset_password_email(
    data: SendPasswordResetEmailData,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_db)
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
        
        return create_success_response(
            message="パスワードリセット用メールを送信しました"
        )
    finally:
        logger.info("send_reset_password_email - end")


@router.post("/reset-password", response_model=SuccessResponse[None])
async def reset_password(
    reset_data: PasswordResetData,
    session: AsyncSession = Depends(get_db)
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
        
        # パスワードリセット実行
        await reset_password(email, reset_data.new_password, session)
        
        logger.info("reset_password - success")
        return create_success_response(
            message="パスワードのリセットが正常に完了しました"
        )
    finally:
        logger.info("reset_password - end")