"""
ユーザー関連のCRUD操作とサービス層機能
FastAPI標準の関数ベース実装
"""

import uuid
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import structlog
from fastapi import BackgroundTasks, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from api.common.database import get_db
from api.common.setting import setting
from api.v1.features.feature_auth.schemas.user import UserCreate, UserResponse, UserUpdate
from api.v1.features.feature_auth.security import create_access_token, decode_access_token, hash_password
from api.v1.features.feature_auth.send_reset_password_email import send_reset_password_email
from api.v1.features.feature_auth.send_verification_email import send_verification_email
from api.v1.features.feature_auth.models.user import User

logger = structlog.get_logger()


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    """メールアドレスに基づいてユーザーを取得します。

    Args:
        db (AsyncSession): 非同期データベースセッション。
        email (str): 検索対象のメールアドレス。

    Returns:
        User | None: 該当するユーザーが存在すれば返却、それ以外はNone。
    """
    query = select(User).where(User.email == email, User.user_status == User.STATUS_ACTIVE, User.deleted_at.is_(None))
    result = await db.execute(query)
    return result.scalars().first()


async def get_user_by_email_including_deleted(db: AsyncSession, email: str) -> User | None:
    """メールアドレスに基づいてユーザーを取得します（論理削除済みも含む）。

    Args:
        db (AsyncSession): 非同期データベースセッション。
        email (str): 検索対象のメールアドレス。

    Returns:
        User | None: 該当するユーザーが存在すれば返却、それ以外はNone。
    """
    query = select(User).where(User.email == email)
    result = await db.execute(query)
    return result.scalars().first()


async def get_user_by_username(db: AsyncSession, username: str) -> User | None:
    """ユーザー名に基づいてユーザーを取得します。

    Args:
        db (AsyncSession): 非同期データベースセッション。
        username (str): 検索対象のユーザー名。

    Returns:
        User | None: 該当するユーザーが存在すれば返却、それ以外はNone。
    """
    query = select(User).where(User.username == username, User.user_status == User.STATUS_ACTIVE, User.deleted_at.is_(None))
    result = await db.execute(query)
    return result.scalars().first()


async def get_user_by_id(db: AsyncSession, user_id: str) -> User | None:
    """ユーザーIDに基づいてユーザーを取得します。

    Args:
        db (AsyncSession): 非同期データベースセッション。
        user_id (str): 検索対象のユーザーID。

    Returns:
        User | None: 該当するユーザーが存在すれば返却、それ以外はNone。
    """
    query = select(User).where(User.user_id == user_id, User.user_status == User.STATUS_ACTIVE, User.deleted_at.is_(None))
    result = await db.execute(query)
    return result.scalars().first()


async def create_user(db: AsyncSession, user: User) -> User:
    """新しいユーザーをデータベースに登録します。

    Args:
        db (AsyncSession): 非同期データベースセッション。
        user (User): 作成するユーザーオブジェクト。

    Returns:
        User: 作成されたユーザーオブジェクト。
    """
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def update_user_password(db: AsyncSession, user: User, hashed_password: str) -> User:
    """ユーザーのパスワードを更新します。

    Args:
        db (AsyncSession): 非同期データベースセッション。
        user (User): 更新対象のユーザーオブジェクト。
        hashed_password (str): ハッシュ化された新しいパスワード。

    Returns:
        User: 更新されたユーザーオブジェクト。
    """
    user.hashed_password = hashed_password
    await db.commit()
    await db.refresh(user)
    return user


async def update_user_profile(db: AsyncSession, user: User, username: str | None = None, email: str | None = None, contact_number: str | None = None, date_of_birth=None) -> User:
    """ユーザーのプロフィール情報を更新します。

    Args:
        db (AsyncSession): 非同期データベースセッション。
        user (User): 更新対象のユーザーオブジェクト。
        username (str | None): 新しいユーザー名（オプション）。
        email (str | None): 新しいメールアドレス（オプション）。
        contact_number (str | None): 新しい連絡先（オプション）。
        date_of_birth: 新しい生年月日（オプション）。

    Returns:
        User: 更新されたユーザーオブジェクト。
    """
    if username is not None:
        user.username = username
    if email is not None:
        user.email = email
    if contact_number is not None:
        user.contact_number = contact_number
    if date_of_birth is not None:
        user.date_of_birth = date_of_birth
    
    # 日本時間をタイムゾーン情報なしで保存
    user.updated_at = datetime.now(ZoneInfo("Asia/Tokyo")).replace(tzinfo=None)
    await db.commit()
    await db.refresh(user)
    return user


async def delete_user(db: AsyncSession, user: User) -> User:
    """ユーザーを論理削除します。

    Args:
        db (AsyncSession): 非同期データベースセッション。
        user (User): 削除対象のユーザーオブジェクト。

    Returns:
        User: 削除されたユーザーオブジェクト。
    """
    # ユーザーステータスを停止中に変更し、削除日時を設定
    user.user_status = User.STATUS_SUSPENDED
    # 日本時間をタイムゾーン情報なしで保存
    user.deleted_at = datetime.now(ZoneInfo("Asia/Tokyo")).replace(tzinfo=None)
    await db.commit()
    await db.refresh(user)
    return user


async def restore_user(db: AsyncSession, user: User, new_username: str, new_password: str) -> User:
    """論理削除されたユーザーを復活させます。

    Args:
        db (AsyncSession): 非同期データベースセッション。
        user (User): 復活対象のユーザーオブジェクト。
        new_username (str): 新しいユーザー名。
        new_password (str): 新しいパスワード。

    Returns:
        User: 復活されたユーザーオブジェクト。
    """
    # ユーザー情報を更新して復活
    user.username = new_username
    user.hashed_password = hash_password(new_password)
    user.user_status = User.STATUS_ACTIVE
    user.deleted_at = None
    # 日本時間をタイムゾーン情報なしで保存
    user.updated_at = datetime.now(ZoneInfo("Asia/Tokyo")).replace(tzinfo=None)
    await db.commit()
    await db.refresh(user)
    return user


# =============================================================================
# サービス層関数（ビジネスロジック、認証、メール送信など）
# =============================================================================

async def get_current_user(request: Request, db: AsyncSession = Depends(get_db)) -> User:
    """現在ログイン中のユーザーを取得します。

    Args:
        request (Request): リクエストオブジェクト（クッキーからトークンを取得）。
        db (AsyncSession): 非同期データベースセッション。

    Returns:
        User: 現在ログイン中のユーザー。

    Raises:
        HTTPException: 認証に失敗した場合。
    
    Note:
        JWTトークンのsubフィールドからメールアドレスを取得してユーザーを検索します。
    """
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="認証情報が無効です", headers={"WWW-Authenticate": "Bearer"})

    # クッキーからトークンを取得
    token = request.cookies.get("authToken")
    if not token:
        raise credentials_exception

    try:
        # トークンからメールアドレスを取得
        payload = decode_access_token(token)
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except Exception:
        raise credentials_exception

    # データベースからユーザーを取得（メールアドレスで検索）
    user = await get_user_by_email(db, email=email)
    if user is None:
        raise credentials_exception

    return user


async def create_user_service(email: str, username: str, password: str, db: AsyncSession) -> User:
    """新しいユーザーを作成します（パスワードハッシュ化込み）。
    
    論理削除済みユーザーが存在する場合は復活させます。

    Args:
        email (str): メールアドレス。
        username (str): ユーザー名。
        password (str): パスワード。
        db (AsyncSession): 非同期データベースセッション。

    Returns:
        User: 作成または復活されたユーザー。
    """
    logger.info("create_user_service - start", email=email, username=username)
    
    # 論理削除済みも含めてユーザーが既に存在するかチェック
    existing_user = await get_user_by_email_including_deleted(db, email)
    
    if existing_user:
        if existing_user.deleted_at is not None:
            # 論理削除済みユーザーを復活
            logger.info("create_user_service - restoring deleted user", email=email, user_id=existing_user.user_id)
            restored_user = await restore_user(db, existing_user, username, password)
            logger.info("create_user_service - user restored", email=email, user_id=restored_user.user_id)
            return restored_user
        else:
            # アクティブなユーザーが既に存在
            logger.error("create_user_service - active user already exists", email=email)
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="このメールアドレスは既に使用されています")
    
    # 新規ユーザー作成
    logger.info("create_user_service - creating new user", email=email)
    hashed_password = hash_password(password)
    
    new_user = User(
        user_id=str(uuid.uuid4()),
        email=email,
        username=username,
        hashed_password=hashed_password,
        user_role=User.ROLE_FREE,  # デフォルトで無料会員として設定
        user_status=User.STATUS_ACTIVE,
        # 日本時間をタイムゾーン情報なしで保存
        created_at=datetime.now(ZoneInfo("Asia/Tokyo")).replace(tzinfo=None),
        updated_at=datetime.now(ZoneInfo("Asia/Tokyo")).replace(tzinfo=None)
    )
    
    created_user = await create_user(db, new_user)
    logger.info("create_user_service - new user created", email=email, user_id=created_user.user_id)
    return created_user


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
        
    Raises:
        HTTPException: ユーザーが見つからない場合。
    """
    # ユーザーの存在確認
    user = await get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="指定されたメールアドレスのユーザーが見つかりません")
    
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
    user = await get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ユーザーが見つかりません")
    
    hashed_password = hash_password(new_password)
    await update_user_password(db, user, hashed_password)


async def update_user_with_schema(db: AsyncSession, user: User, user_update: UserUpdate) -> User:
    """UserUpdateスキーマを使ってユーザーを更新します。

    Args:
        db (AsyncSession): 非同期データベースセッション。
        user (User): 更新対象のユーザーオブジェクト。
        user_update (UserUpdate): 更新データ。

    Returns:
        User: 更新されたユーザーオブジェクト。
    """
    return await update_user_profile(
        db=db,
        user=user,
        username=user_update.username,
        email=user_update.email,
        contact_number=user_update.contact_number,
        date_of_birth=user_update.date_of_birth
    )


