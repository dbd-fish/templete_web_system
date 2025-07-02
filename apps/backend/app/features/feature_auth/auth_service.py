
from datetime import timedelta

import structlog
from fastapi import BackgroundTasks, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.database import get_db
from app.common.setting import setting
from app.features.feature_auth.auth_repository import UserRepository
from app.features.feature_auth.schemas.user import UserCreate, UserResponse
from app.features.feature_auth.security import create_access_token, decode_access_token, hash_password
from app.features.feature_auth.send_reset_password_email import send_reset_password_email
from app.features.feature_auth.send_verification_email import send_verification_email
from app.models.user import User

logger = structlog.get_logger()


async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """トークンから現在のユーザーを取得します。

    トークンをデコードして、その情報をもとにデータベースからユーザーを取得します。
    トークンが無効、またはユーザーが存在しない場合は例外をスローします。

    Args:
        token (Annotated[str, Depends]): Bearerトークン。
        db (AsyncSession): 非同期データベースセッション。

    Returns:
        UserResponse: 現在のユーザー情報（Pydanticスキーマ形式）。

    Raises:
        HTTPException:
            - 401: トークンが無効または`sub`フィールドが存在しない場合。
            - 404: ユーザーが存在しない場合。

    """
    logger.info("get_current_user - start")
    try:
        # リクエストヘッダーからCookieを取得
        cookie_header = request.headers.get("cookie")
        logger.info("get_me - cookie_header", cookie_header=cookie_header)
        if not cookie_header:
            logger.warning("get_me - no cookie found")
            raise HTTPException(
                status_code=401, detail="Authentication credentials were not provided"
            )

        # Cookieから`authToken`を抽出
        cookies = {cookie.split("=")[0].strip(): cookie.split("=")[1].strip() for cookie in cookie_header.split(";")}
        logger.info("get_me - cookies", cookies=cookies)
        token = cookies.get("authToken")
        logger.info("get_me - token", token=token)

        if not token:
            logger.warning("get_me - authToken not found in cookies")
            raise HTTPException(
                status_code=401, detail="Authentication credentials were not provided"
            )


        # トークンをデコードしてペイロードを取得
        payload = decode_access_token(token)
        email: str = payload.get("sub") or ""
        if email is None:
            logger.warning("get_current_user - token missing 'sub'", token=token)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # TODO: クライアントのIPチェックはプロキシなどの環境に依存するため保留
        client_ip: str = payload.get("client_ip") or ""
        logger.debug("get_current_user - client_ip", client_ip=client_ip)

        # ユーザーをデータベースから取得
        user = await UserRepository.get_user_by_email(db, email)
        if user is None:
            logger.warning("get_current_user - user not found", email=email)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found",
            )

        logger.info("get_current_user - success", user_id=user.user_id)
        return UserResponse(
            user_id=user.user_id,
            email=user.email,
            username=user.username,
            user_role=user.user_role,
            user_status=user.user_status,
        )
    finally:
        logger.info("get_current_user - end")


async def create_user(
    email: str, username: str, password: str, db: AsyncSession,
) -> User:
    """新しいユーザーを作成します。

    ユーザーの情報をもとに新しいユーザーをデータベースに登録します。
    パスワードはハッシュ化されて保存されます。
    エラーが発生した場合はロールバックし、例外をスローします。

    Args:
        email (str): ユーザーのメールアドレス。
        username (str): ユーザー名。
        password (str): プレーンテキストのパスワード。
        db (AsyncSession): 非同期データベースセッション。

    Returns:
        User: 作成されたユーザーオブジェクト。

    Raises:
        HTTPException: ユーザー作成中に発生したエラー。

    """
    logger.info("create_user - start", email=email, username=username, password=password)
    try:
        # パスワードをハッシュ化
        hashed_password = hash_password(password)

        # 新しいユーザーオブジェクトを作成
        new_user = User(
            email=email,
            username=username,
            hashed_password=hashed_password,
            user_role=User.ROLE_FREE,
            user_status=User.STATUS_ACTIVE,
        )

        # 既存ユーザーの確認
        existing_user = await UserRepository.get_user_by_email(db, email)
        if existing_user:
            logger.warning("create_user - user already exists", email=email)
            raise HTTPException(
                status_code=400,
                detail="User already exists",
            )

        # データベースにユーザーを保存
        saved_user = await UserRepository.create_user(db, new_user)
        logger.info("create_user - success", user_id=saved_user.user_id)
        return saved_user
    finally:
        logger.info("create_user - end")

async def temporary_create_user(user: UserCreate, background_tasks: BackgroundTasks, db: AsyncSession,):
    """
    仮登録処理用のJWTトークンを生成してメールuserを送信する。

    Args:
        data: ユーザーのサインアップデータ（email, username, password を含む）。
        background_tasks: 非同期タスクのためのFastAPI BackgroundTasksオブジェクト。
        db (AsyncSession): 非同期データベースセッション。
    """
    logger.info("temporary_create_user - start", user=user)
    try:
        # 既存のメールアドレスをチェック
        existing_user = await UserRepository.get_user_by_email(db, user.email)
        if existing_user:
            logger.warning("temporary_create_user - user already exists", email=user.email)
            raise HTTPException(
                status_code=400,
                detail="User already exists",
            )

        # 仮登録用JWTトークンを生成
        token_data = {
            "email": user.email,
            "username": user.username,
            "password": user.password,  # トークンにパスワードは含めない方が安全
        }
        token = create_access_token(data=token_data, expires_delta=timedelta(minutes=60))
        logger.info("temporary_create_user - token", token=token)

        # 認証用メールを送信
        base_url = setting.APP_URL
        verification_url = f"{base_url}/signup-vertify-complete?token={token}"
        background_tasks.add_task(send_verification_email, user.email, verification_url)
        logger.info("temporary_create_user - background_tasks,add", email=user.email, verification_url=verification_url)
    finally:
        logger.info("temporary_create_user - end")


async def reset_password_email(email: str, background_tasks: BackgroundTasks, db: AsyncSession,):
    """l
    パスワード再設定用のJWTトークンを生成してメールを送信する。

    Args:
        email: パスワード再設定対象のメールアドレス。
        background_tasks: 非同期タスクのためのFastAPI BackgroundTasksオブジェクト。
        db (AsyncSession): 非同期データベースセッション。
    """
    logger.info("reset_password_email - start", email=email)
    try:
        # 既存のメールアドレスをチェック
        existing_user = await UserRepository.get_user_by_email(db, email)
        if not existing_user:
            logger.warning("reset_password_email - user does not exist", email=email)
            raise HTTPException(
                status_code=400,
                detail="User does not exist",
            )

        # 仮登録用JWTトークンを生成
        token_data = {
            "email": email,
        }
        token = create_access_token(data=token_data, expires_delta=timedelta(minutes=60))
        logger.info("reset_password_email - token", token=token)

        # 認証用メールを送信
        base_url = setting.APP_URL
        reset_password_url = f"{base_url}/reset-password?token={token}"
        background_tasks.add_task(send_reset_password_email, email, reset_password_url)
        logger.info("reset_password_email - background_tasks,add", email=email, reset_password_url=reset_password_url)
    finally:
        logger.info("reset_password_email - end")



async def reset_password(email: str, new_password: str, db: AsyncSession):
    """パスワードをリセットします。

    Args:
        email (str): ユーザーのメールアドレス。
        new_password (str): 新しいプレーンテキストのパスワード。
        db (AsyncSession): 非同期データベースセッション。

    Returns:
        User: パスワードが更新されたユーザーオブジェクト。

    Raises:
        HTTPException: ユーザーが存在しない場合。

    """
    logger.info("reset_password - start", email=email)
    user = await UserRepository.get_user_by_email(db, email)

    if not user:
        logger.info("reset_password - user not found", email=email)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    hashed_password = hash_password(new_password)

    try:
        # TODO: メールによるユーザ認証後にパスワード変更を完了するべきでは？
        updated_user = await UserRepository.update_user_password(db, user, hashed_password)
        logger.info("reset_password - success", user_id=updated_user.user_id)
        return updated_user
    except Exception as e:
        logger.error("reset_password - error", error=str(e))
        await db.rollback()
        raise e
    finally:
        logger.info("reset_password - end")


async def verify_email_token(token: str) -> UserCreate:
    """トークンを検証し、ユーザー情報を返す。

    Args:
        token (str): メール認証トークン。
        db (AsyncSession): 非同期データベースセッション。

    Returns:
        UserCreate: トークンに対応するユーザー情報。
    """
    logger.info("verify_email_token - start", token=token)

    try:
        # トークンをデコードしてemailを取得
        payload = decode_access_token(token)
        email: str = payload.get("email") or ""
        password: str = payload.get("password") or ""
        username: str = payload.get("username") or ""
        logger.info("verify_email_token - payload", payload=payload)
        if not email or not password or not username:
            logger.warning("verify_email_token - token missing", email=email, password=password, username=username)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user_info = UserCreate(
            email=email,
            username=username,
            password=password,
            user_role=User.ROLE_FREE,
            user_status=User.STATUS_ACTIVE
        )
        return user_info
    finally:
        logger.info("verify_email_token - end")

async def decode_password_reset_token(token: str) -> str:
    """パスワードリセット用トークンからemailを取得

    Args:
        token (str): メール認証トークン。
    Returns:
        str: メールアドレス。
    """
    logger.info("decode_password_reset_token - start", token=token)

    try:
        # トークンをデコードしてemailを取得
        payload = decode_access_token(token)
        email: str = payload.get("email") or ""

        if not email:
            logger.warning("decode_password_reset_token - token missing", email=email)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return email
    finally:
        logger.info("decode_password_reset_token - end")
