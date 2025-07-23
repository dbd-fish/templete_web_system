import uuid
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import jwt
import structlog
from fastapi import HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlalchemy import or_
from sqlalchemy.future import select

from api.common.database import AsyncSession
from api.common.redis_client import get_device_info_from_request, session_store
from api.common.setting import setting
from api.v1.features.feature_auth.models.user import User

# ログの設定
logger = structlog.get_logger()

# 環境変数に適切に置き換える
SECRET_KEY = setting.SECRET_KEY  # JWTの署名に使用する秘密鍵
ALGORITHM = setting.ALGORITHM  # JWTの暗号化アルゴリズム
ACCESS_TOKEN_EXPIRE_MINUTES = setting.ACCESS_TOKEN_EXPIRE_MINUTES  # アクセストークンの有効期限（分単位）
REFRESH_TOKEN_EXPIRE_DAYS = setting.REFRESH_TOKEN_EXPIRE_DAYS  # リフレッシュトークンの有効期限（日単位）

# パスワード暗号化設定
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# トークンのエンドポイント（FastAPIのOAuth2PasswordBearerを使用）
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")


def hash_password(password: str) -> str:
    """パスワードをハッシュ化する。

    Args:
        password (str): プレーンパスワード。

    Returns:
        str: ハッシュ化されたパスワード。

    """
    logger.info("hash_password - start")
    try:
        # passlibのCryptContextクラスを使用してbcryptアルゴリズムでパスワードをハッシュ化
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
    logger.info("verify_password - start")
    try:
        # passlibのCryptContextを使用してプレーンパスワードとハッシュ値を比較検証
        result = pwd_context.verify(plain_password, hashed_password)
        logger.info("verify_password - end", result=result)
        return result
    finally:
        logger.info("verify_password - end")


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """アクセストークンを作成する。

    Args:
        data (dict): トークンに含めるデータ。
        expires_delta (timedelta, optional): トークンの有効期限。

    Returns:
        str: 作成されたJWTアクセストークン。

    """
    logger.info("create_access_token - start")
    try:
        to_encode = data.copy()
        to_encode.update({"token_type": "access"})  # トークンタイプを明示
        # ZoneInfoクラスで日本時間を設定し、有効期限を計算
        expire = datetime.now(ZoneInfo("Asia/Tokyo")) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
        to_encode.update({"exp": expire})
        logger.debug("create_access_token - to_encode prepared")
        # PyJWTライブラリでペイロードを秘密鍵と指定アルゴリズムで署名してJWTを生成
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        logger.info("create_access_token - success")
        logger.info("create_access_token - expire", expire=expire)
        # PyJWT 2.x系では文字列を返すが、型チェックのために明示的にstrにキャスト
        return str(encoded_jwt)
    finally:
        logger.info("create_access_token - end")


async def create_refresh_token(user_email: str, request: Request | None = None) -> str:
    """リフレッシュトークンを作成する。

    Args:
        user_email (str): ユーザーのメールアドレス。
        request (Request, optional): リクエストオブジェクト（デバイス情報取得用）

    Returns:
        str: 作成されたリフレッシュトークン。

    """
    logger.info("create_refresh_token - start", user_email=user_email)
    try:
        # UUIDライブラリでランダムなUUID4形式のリフレッシュトークンを生成
        refresh_token = str(uuid.uuid4())

        # デバイス情報を取得（User-Agent、IP等のリクエスト情報を解析）
        device_info = await get_device_info_from_request(request) if request else {}

        # Redisセッションストアにリフレッシュトークンとデバイス情報を保存
        await session_store.store_refresh_token(refresh_token, user_email, device_info)

        # セッション作成のメトリクス情報をRedisに記録
        await session_store.record_session_metrics("token_created", user_email, device_info)

        logger.info("create_refresh_token - success", user_email=user_email)
        return refresh_token
    finally:
        logger.info("create_refresh_token - end")


async def create_token_pair(user_email: str, client_ip: str, request: Request | None = None) -> tuple[str, str]:
    """アクセストークンとリフレッシュトークンのペアを作成する。

    Args:
        user_email (str): ユーザーのメールアドレス。
        client_ip (str): クライアントのIPアドレス。
        request (Request, optional): リクエストオブジェクト（デバイス情報取得用）

    Returns:
        Tuple[str, str]: (access_token, refresh_token)のタプル。

    """
    logger.info("create_token_pair - start", user_email=user_email)
    try:
        access_token = create_access_token(data={"sub": user_email, "client_ip": client_ip})
        refresh_token = await create_refresh_token(user_email, request)
        logger.info("create_token_pair - success", user_email=user_email)
        return access_token, refresh_token
    finally:
        logger.info("create_token_pair - end")


def create_verification_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """メール認証用トークンを作成する。

    Args:
        data (dict): トークンに含めるデータ。
        expires_delta (timedelta, optional): トークンの有効期限。

    Returns:
        str: 作成されたJWT認証トークン。

    """
    logger.info("create_verification_token - start")
    try:
        to_encode = data.copy()
        to_encode.update({"token_type": "verification"})  # トークンタイプを明示
        # ZoneInfoで日本時間を取得し、デフォルト24時間の有効期限を設定
        expire = datetime.now(ZoneInfo("Asia/Tokyo")) + (expires_delta or timedelta(hours=24))
        to_encode.update({"exp": expire})
        logger.debug("create_verification_token - to_encode prepared")
        # PyJWTでメール認証用の署名付きトークンを生成
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        logger.info("create_verification_token - success")
        logger.info("create_verification_token - expire", expire=expire)
        return str(encoded_jwt)
    finally:
        logger.info("create_verification_token - end")


def decode_access_token(token: str) -> dict:
    """アクセストークンをデコードしてペイロードを取得する。

    Args:
        token (str): デコード対象のJWTアクセストークン。

    Returns:
        dict: デコードされたペイロード情報。

    Raises:
        HTTPException: トークンが無効または不正な場合。

    """
    logger.info("decode_access_token - start")
    try:
        # PyJWTライブラリでJWTトークンを秘密鍵と指定アルゴリズムで検証・デコード
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # トークンタイプの検証（access以外は拒否）
        if payload.get("token_type") != "access":
            logger.error("Invalid token type")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="無効なトークンタイプです",
                headers={"WWW-Authenticate": "Bearer"},
            )

        logger.info("decode_access_token - success")
        return payload
    except jwt.ExpiredSignatureError:
        logger.error("Token has expired")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="トークンが期限切れです",
            headers={"WWW-Authenticate": "Bearer"},
        ) from None
    except jwt.InvalidTokenError:
        logger.error("Invalid token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="無効なトークンです",
            headers={"WWW-Authenticate": "Bearer"},
        ) from None
    finally:
        logger.info("decode_access_token - end")


def decode_verification_token(token: str) -> dict:
    """認証用トークンをデコードしてペイロードを取得する。

    Args:
        token (str): デコード対象のJWT認証トークン。

    Returns:
        dict: デコードされたペイロード情報。

    Raises:
        HTTPException: トークンが無効または不正な場合。

    """
    logger.info("decode_verification_token - start")
    try:
        # PyJWTでメール認証用トークンを検証・デコード
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # トークンタイプの検証（verification以外は拒否）
        if payload.get("token_type") != "verification":
            logger.error("Invalid token type")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="無効なトークンタイプです",
            )

        logger.info("decode_verification_token - success")
        return payload
    except jwt.ExpiredSignatureError:
        logger.error("Verification token has expired")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="認証トークンが期限切れです",
        ) from None
    except jwt.InvalidTokenError:
        logger.error("Invalid verification token")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="無効な認証トークンです",
        ) from None
    finally:
        logger.info("decode_verification_token - end")


async def validate_refresh_token(refresh_token: str) -> str:
    """リフレッシュトークンを検証してユーザーメールを取得する。

    Args:
        refresh_token (str): 検証対象のリフレッシュトークン。

    Returns:
        str: ユーザーのメールアドレス。

    Raises:
        HTTPException: リフレッシュトークンが無効な場合。

    """
    logger.info("validate_refresh_token - start")
    try:
        # Redisセッションストアでリフレッシュトークンの有効性を検証しユーザーメールを取得
        user_email = await session_store.validate_refresh_token(refresh_token)
        if not user_email:
            logger.error("Invalid refresh token")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="無効なリフレッシュトークンです",
            )

        # トークン検証のメトリクス情報をRedisに記録
        await session_store.record_session_metrics("token_validated", user_email)

        logger.info("validate_refresh_token - success", user_email=user_email)
        return user_email
    finally:
        logger.info("validate_refresh_token - end")


async def revoke_refresh_token(refresh_token: str) -> None:
    """リフレッシュトークンを無効化する。

    Args:
        refresh_token (str): 無効化対象のリフレッシュトークン。

    """
    logger.info("revoke_refresh_token - start")
    try:
        # Redisセッションストアから指定されたリフレッシュトークンを無効化
        await session_store.revoke_refresh_token(refresh_token)

        # トークン無効化のメトリクス情報をRedisに記録
        await session_store.record_session_metrics("token_revoked")

        logger.info("revoke_refresh_token - success")
    finally:
        logger.info("revoke_refresh_token - end")


async def revoke_all_refresh_tokens_for_user(user_email: str) -> int:
    """特定ユーザーのすべてのリフレッシュトークンを無効化する。

    Args:
        user_email (str): 対象ユーザーのメールアドレス。

    Returns:
        int: 無効化されたトークン数

    """
    logger.info("revoke_all_refresh_tokens_for_user - start", user_email=user_email)
    try:
        # Redisセッションストアで指定ユーザーの全リフレッシュトークンを無効化
        revoked_count = await session_store.revoke_all_refresh_tokens_for_user(user_email)

        # 全トークン無効化のメトリクス情報をRedisに記録
        await session_store.record_session_metrics("all_tokens_revoked", user_email)

        logger.info("revoke_all_refresh_tokens_for_user - success", user_email=user_email, revoked_count=revoked_count)
        return revoked_count
    finally:
        logger.info("revoke_all_refresh_tokens_for_user - end")


async def authenticate_user(username_or_email: str, password: str, db: AsyncSession) -> User:
    """ユーザー名またはメールアドレスとパスワードを使用してユーザー認証を行う。

    Args:
        username_or_email (str): ユーザー名またはメールアドレス。
        password (str): プレーンパスワード。
        db (AsyncSession): データベースセッション。

    Returns:
        User: 認証に成功したユーザーオブジェクト。

    Raises:
        HTTPException: 認証に失敗した場合。

    """
    logger.info("authenticate_user - start", username_or_email=username_or_email)
    # SQLAlchemyのselectとor_関数でユーザー名またはメール、アクティブ状態、削除なしの条件でクエリ構築
    query = select(User).where(
        or_(User.email == username_or_email, User.username == username_or_email),
        User.user_status == User.STATUS_ACTIVE,
        User.deleted_at.is_(None),
    )
    # 非同期データベースセッションでクエリを実行
    result = await db.execute(query)
    # SQLAlchemyのscalars()でスカラー値を取得し、first()で最初のレコードを取得
    user = result.scalars().first()
    if not user:
        logger.info("authenticate_user - user not found", username_or_email=username_or_email)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="メールアドレスまたはパスワードが無効です",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not verify_password(password, user.hashed_password):
        logger.info("authenticate_user - incorrect password", username_or_email=username_or_email)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="メールアドレスまたはパスワードが無効です",
            headers={"WWW-Authenticate": "Bearer"},
        )
    logger.info("authenticate_user - success", user_id=user.user_id)
    logger.info("authenticate_user - end")
    return user


def require_admin_role(user: User) -> None:
    """管理者権限が必要な機能にアクセスする際の権限チェックを行う。

    Args:
        user (User): 権限を確認するユーザーオブジェクト。

    Raises:
        HTTPException: ユーザーが管理者権限を持たない場合。

    """
    logger.info("require_admin_role - start", user_id=user.user_id, user_role=user.user_role)
    
    if user.user_role < User.ROLE_ADMIN:
        logger.warning("require_admin_role - access denied", user_id=user.user_id, user_role=user.user_role)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="管理者権限が必要です",
        )
    
    logger.info("require_admin_role - access granted", user_id=user.user_id)


def require_owner_role(user: User) -> None:
    """オーナー権限が必要な機能にアクセスする際の権限チェックを行う。

    Args:
        user (User): 権限を確認するユーザーオブジェクト。

    Raises:
        HTTPException: ユーザーがオーナー権限を持たない場合。

    """
    logger.info("require_owner_role - start", user_id=user.user_id, user_role=user.user_role)
    
    if user.user_role < User.ROLE_OWNER:
        logger.warning("require_owner_role - access denied", user_id=user.user_id, user_role=user.user_role)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="オーナー権限が必要です",
        )
    
    logger.info("require_owner_role - access granted", user_id=user.user_id)


def is_admin_user(user: User) -> bool:
    """ユーザーが管理者権限を持つかどうかを判定する。

    Args:
        user (User): 判定するユーザーオブジェクト。

    Returns:
        bool: 管理者権限を持つ場合True、そうでなければFalse。

    """
    return user.user_role >= User.ROLE_ADMIN


def is_owner_user(user: User) -> bool:
    """ユーザーがオーナー権限を持つかどうかを判定する。

    Args:
        user (User): 判定するユーザーオブジェクト。

    Returns:
        bool: オーナー権限を持つ場合True、そうでなければFalse。

    """
    return user.user_role >= User.ROLE_OWNER
