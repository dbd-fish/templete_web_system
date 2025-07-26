from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import structlog
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import or_
from sqlalchemy.future import select

from api.common.database import AsyncSession
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


def create_access_token(user_email: str, expires_delta: timedelta | None = None) -> str:
    """JWTアクセストークンを作成する

    Args:
        user_email (str): ユーザーのメールアドレス。
        expires_delta (timedelta, optional): トークンの有効期限。

    Returns:
        str: 作成されたJWTアクセストークン。

    """
    logger.info("create_access_token - start", user_email=user_email)
    try:
        expire = datetime.now(ZoneInfo("Asia/Tokyo")) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
        to_encode = {
            "email": user_email,  # ユーザーメール
            "exp": int(expire.timestamp()),  # 有効期限（30分）
        }

        logger.debug("create_access_token - JWT payload prepared", user_email=user_email)
        # python-joseライブラリでJWTアクセストークンを生成
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        logger.info("create_access_token - simplified JWT created", user_email=user_email, expire=expire)
        return encoded_jwt
    finally:
        logger.info("create_access_token - end")


def create_refresh_token(user_email: str, expires_delta: timedelta | None = None) -> str:
    """JWTリフレッシュトークンを作成する

    Args:
        user_email (str): ユーザーのメールアドレス。
        expires_delta (timedelta, optional): トークンの有効期限。

    Returns:
        str: 作成されたJWTリフレッシュトークン。

    """
    logger.info("create_refresh_token - start", user_email=user_email)
    try:
        expire = datetime.now(ZoneInfo("Asia/Tokyo")) + (expires_delta or timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))
        to_encode = {
            "email": user_email,  # ユーザーメール
            "exp": int(expire.timestamp()),  # 有効期限（5日）
        }

        logger.debug("create_refresh_token - JWT payload prepared", user_email=user_email)

        # python-joseでJWTリフレッシュトークンを生成
        refresh_token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

        logger.info("create_refresh_token - simplified JWT created", user_email=user_email, expire=expire)
        return refresh_token
    finally:
        logger.info("create_refresh_token - end")


def create_token_pair(user_email: str) -> tuple[str, str]:
    """JWTアクセストークンとリフレッシュトークンのペアを作成する。

    Args:
        user_email (str): ユーザーのメールアドレス。

    Returns:
        Tuple[str, str]: (access_token, refresh_token)のタプル。

    """
    logger.info("create_token_pair - start", user_email=user_email)
    try:
        access_token = create_access_token(user_email)
        refresh_token = create_refresh_token(user_email)
        logger.info("create_token_pair - simplified JWT pair created", user_email=user_email)
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
        # python-jose用にUTCタイムスタンプに変換
        to_encode.update({"exp": int(expire.timestamp())})
        logger.debug("create_verification_token - to_encode prepared")
        # python-joseでメール認証用の署名付きトークンを生成
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        logger.info("create_verification_token - success")
        logger.info("create_verification_token - expire", expire=expire)
        return encoded_jwt
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
        # python-joseライブラリでJWTトークンを秘密鍵と指定アルゴリズムで検証・デコード
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        logger.info("decode_access_token - success")
        return payload
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
        # python-joseでメール認証用トークンを検証・デコード
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
    finally:
        logger.info("decode_verification_token - end")


def decode_refresh_token(token: str) -> dict:
    """JWTリフレッシュトークンをデコードしてペイロードを取得する（一般的JWT+リフレッシュトークンシステム標準実装）。

    Args:
        token (str): デコード対象のJWTリフレッシュトークン。

    Returns:
        dict: デコードされたペイロード情報。

    Raises:
        HTTPException: トークンが無効または不正な場合。

    """
    logger.info("decode_refresh_token - start")
    try:
        # python-joseライブラリでJWTリフレッシュトークンを検証・デコード
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # 必須フィールドの確認
        if not payload.get("email"):
            logger.error("Missing email in refresh token")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="リフレッシュトークンにemailが含まれていません",
            )

        logger.info("decode_refresh_token - success", email=payload.get("email"))
        return payload
    finally:
        logger.info("decode_refresh_token - end")


def validate_refresh_token(refresh_token: str) -> str:
    """JWTリフレッシュトークンを検証してユーザーメールを取得する（一般的JWT+リフレッシュトークンシステム標準実装）。

    Args:
        refresh_token (str): 検証対象のJWTリフレッシュトークン。

    Returns:
        str: ユーザーのメールアドレス。

    Raises:
        HTTPException: リフレッシュトークンが無効な場合。

    """
    logger.info("validate_refresh_token - start")
    logger.info("validate_refresh_token - JWT validation", token_length=len(refresh_token))
    try:
        # JWTリフレッシュトークンをデコードして検証
        payload = decode_refresh_token(refresh_token)

        # emailを取得
        user_email = payload.get("email")
        if not user_email:
            logger.error("validate_refresh_token - email not found in JWT payload")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="リフレッシュトークンにemailが含まれていません",
            )

        logger.info("validate_refresh_token - JWT validation successful", user_email=user_email)
        return user_email
    finally:
        logger.info("validate_refresh_token - end")



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
