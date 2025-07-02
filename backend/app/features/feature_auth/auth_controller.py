import structlog
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.database import get_db
from app.features.feature_auth.auth_service import create_user, decode_password_reset_token, get_current_user, reset_password, reset_password_email, temporary_create_user, verify_email_token
from app.features.feature_auth.schemas.user import PasswordResetData, SendPasswordResetEmailData, TokenData, UserCreate, UserResponse
from app.features.feature_auth.security import authenticate_user, create_access_token
from app.models.user import User

# ログの設定
logger = structlog.get_logger()

router = APIRouter()

@router.post("/me", response_model=UserResponse)
async def get_me(request: Request, db: AsyncSession = Depends(get_db)):
    """現在ログインしているユーザーの情報を取得するエンドポイント。

    Args:
        request (Request): リクエストオブジェクト（クッキーの解析に使用）。
        db (AsyncSession): 非同期データベースセッション。

    Returns:
        UserResponse: ログイン中のユーザー情報。

    """
    logger.info("get_me - start")
    try:
        user = await get_current_user(request, db)
        logger.info("get_me - success", user_id=user.user_id)
        return user
    finally:
        logger.info("get_me - end")

@router.post("/signup", response_model=dict)
async def register_user(tokenData: TokenData, db: AsyncSession = Depends(get_db)):
    """新しいユーザーを登録するエンドポイント。

    Args:
        token (str): メール認証トークン。
        db (AsyncSession): 非同期データベースセッション。

    Returns:
        dict: 登録成功メッセージと新規ユーザーID。

    """
    logger.info("register_user - start",)
    try:
        # tokenからuser情報を取得
        user_info = await verify_email_token(tokenData.token)
        logger.info("register_user - user_info", user_info=user_info)
        # トークンから取得したユーザー情報でユーザー登録
        new_user = await create_user(user_info.email, user_info.username, user_info.password, db)
        logger.info("register_user - success", user_id=new_user.user_id)
        return {"msg": "User created successfully", "user_id": new_user.user_id}
    finally:
        logger.info("register_user - end")

@router.post("/send-verify-email", response_model=dict)
async def send_verify_email(user: UserCreate, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)):
    """新しいユーザーの仮登録用メールを送信するするエンドポイント。

    Args:
        user (UserCreate): 新規ユーザーの情報（メール、ユーザー名、パスワード）。
        db (AsyncSession): 非同期データベースセッション。

    Returns:
        dict: 登録成功メッセージと新規ユーザーID。

    """
    logger.info("temporary_register_user - start", email=user.email, username=user.username)
    try:
        await temporary_create_user(user=user, background_tasks=background_tasks, db=db)
        logger.info("temporary_register_user - success")
        return {"msg": "User created successfully"}
    finally:
        logger.info("temporary_register_user - end")

@router.post("/login", response_model=dict)
async def login(request: Request,response: Response, form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    """ログイン処理を行うエンドポイント。

    Args:
        response (Response): レスポンスオブジェクト。
        form_data (OAuth2PasswordRequestForm): ユーザー名とパスワード。
        db (AsyncSession): 非同期データベースセッション。

    Returns:
        dict: アクセストークンとトークンタイプ。

    """
    logger.info("login - start", username=form_data.username)
    try:
        user = await authenticate_user(form_data.username, form_data.password, db)
        if not user:
            logger.info("login - authentication failed", username=form_data.username)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        # NOTE: クライアントのIPの取得方法はプロキシなどに依存する可能性あり
        # client_host = request.client.host
        client_host = (
            request.headers.get("X-Forwarded-For")
            or (request.client.host if request.client else "unknown")
        )
        access_token = create_access_token(data={"sub": user.email, "client_ip": client_host})  # アクセストークンを生成
        logger.info("login - success", user_id=user.user_id)

        # HttpOnlyクッキーとしてトークンを設定
        response.set_cookie(
            # TODO: リフレッシュトークンを考慮する
            key="authToken",
            value=access_token,
            httponly=True,  # JavaScriptからアクセスできないようにする
            # TODO: 現状はアクセストークンであるAuht_tokeの有効期限を長めに設定する
            max_age=60 * 60 * 3,  # クッキーの有効期限（秒）　3時間
            secure=True,   # HTTPSのみで送信
            samesite="lax"  # クロスサイトリクエストに対する制御
        )
        logger.info("login - success", extra={"user_id": user.user_id})
        return {"message": "Login successful"}
    finally:
        logger.info("login - end")

@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """ログアウト処理を行うエンドポイント。

    Args:
        current_user (User): 現在ログイン中のユーザー。

    Returns:
        dict: ログアウト成功メッセージ。

    """
    logger.info("logout - start", current_user=current_user.email)
    try:
        # クライアント側でトークンを削除するシンプルな処理
        logger.info("logout - success")
        return {"msg": "Logged out successfully"}
    finally:
        logger.info("logout - end")

@router.post("/send-password-reset-email", response_model=dict)
async def send_reset_password_email_endpoint(SendPasswordResetEmailData: SendPasswordResetEmailData, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)):
    """パスワードリセットメール送信処理を行うエンドポイント。

    Args:
        email (str): パスワードリセット対象のメールアドレス
        db (AsyncSession): 非同期データベースセッション。

    Returns:
        dict: パスワードリセット成功メッセージ。

    """
    logger.info("send_reset_password_email_endpoint - start", email=SendPasswordResetEmailData.email)
    try:
        await reset_password_email(email=SendPasswordResetEmailData.email, background_tasks=background_tasks, db=db)
        logger.info("send_reset_password_email_endpoint - success", email=SendPasswordResetEmailData.email)
        return {"msg": "Password reset email send successful"}
    finally:
        logger.info("send_reset_password_email_endpoint - end")




@router.post("/reset-password", response_model=dict)
async def reset_password_endpoint(reset_data: PasswordResetData, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)):
    """新しいユーザーの仮登録用メールを送信するするエンドポイント。

    Args:
        reset_data (PasswordResetData): パスワード変更ユーザの情報（トークン、新しいパスワード）。
        db (AsyncSession): 非同期データベースセッション。

    Returns:
        dict: 登録成功メッセージと新規ユーザーID。

    """
    logger.info("reset_password_endpoint - start", reset_data=reset_data)
    try:
        # tokenからemailを取得
        email = await decode_password_reset_token(reset_data.token)
        await reset_password(email, reset_data.new_password, db)
        logger.info("reset_password_endpoint - success")
        return {"msg": "Password reset successfully"}
    finally:
        logger.info("reset_password_endpoint - end")
