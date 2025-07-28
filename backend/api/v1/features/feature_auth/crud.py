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
from api.v1.features.feature_auth.models.user import User
from api.v1.features.feature_auth.schemas.user import AdminUserUpdateRequest, AdvancedUserUpdate, UserCreate, UserUpdate
from api.v1.features.feature_auth.security import create_verification_token, decode_access_token, decode_verification_token, hash_password, verify_password
from api.v1.features.feature_auth.send_reset_password_email import send_reset_password_email
from api.v1.features.feature_auth.send_verification_email import send_verification_email

logger = structlog.get_logger()


async def create_google_user(db: AsyncSession, email: str, username: str, google_sub: str, full_name: str) -> User:
    """Googleアカウント情報を使用して新規ユーザーを作成します。

    Args:
        db (AsyncSession): 非同期データベースセッション。
        email (str): Googleアカウントのメールアドレス。
        username (str): 生成されたユーザー名。
        google_sub (str): GoogleのユニークIDentifier（sub）。
        full_name (str): Googleアカウントのフルネーム。

    Returns:
        User: 作成された新規ユーザー。

    Raises:
        HTTPException: ユーザー作成に失敗した場合。
    """
    logger.info("create_google_user - start", email=email, username=username)

    try:
        # 論理削除済みユーザーが存在するかチェック
        existing_user = await get_user_by_email_including_deleted(db, email)

        if existing_user and existing_user.user_status == User.STATUS_SUSPENDED and existing_user.deleted_at is not None:
            # 論理削除済みユーザーを復活
            logger.info("create_google_user - restoring deleted user", user_id=existing_user.user_id, email=email)

            # ユーザー情報を更新
            existing_user.username = username
            existing_user.user_status = User.STATUS_ACTIVE
            existing_user.deleted_at = None
            existing_user.updated_at = datetime.now(ZoneInfo("Asia/Tokyo"))

            await db.commit()
            await db.refresh(existing_user)

            logger.info("create_google_user - user restored", user_id=existing_user.user_id)
            return existing_user

        elif existing_user and existing_user.user_status == User.STATUS_ACTIVE:
            # アクティブなユーザーが既に存在
            logger.error("create_google_user - active user already exists", email=email)
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="このメールアドレスは既に登録されています",
            )

        # ユーザー名の重複チェック
        username_query = select(User).where(User.username == username, User.user_status == User.STATUS_ACTIVE, User.deleted_at.is_(None))
        username_result = await db.execute(username_query)
        existing_username_user = username_result.scalars().first()

        if existing_username_user:
            # ユーザー名が重複している場合、ランダムな文字列を追加
            import random
            import string

            random_suffix = "".join(random.choices(string.ascii_lowercase + string.digits, k=4))
            username = f"{username}_{random_suffix}"
            logger.info("create_google_user - username collision resolved", original_username=username[:-5], new_username=username)

        # 新規ユーザーを作成
        new_user = User(
            user_id=uuid.uuid4(),
            email=email,
            username=username,
            hashed_password="",  # Googleユーザーはパスワードを設定しない
            user_role=User.ROLE_FREE,
            user_status=User.STATUS_ACTIVE,
            created_at=datetime.now(ZoneInfo("Asia/Tokyo")),
            updated_at=datetime.now(ZoneInfo("Asia/Tokyo")),
            deleted_at=None,
        )

        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

        logger.info("create_google_user - success", user_id=new_user.user_id, email=new_user.email, username=new_user.username)
        return new_user

    finally:
        logger.info("create_google_user - end")


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

    # ZoneInfoで日本時間を取得し、replace()でタイムゾーン情報を削除して保存
    user.updated_at = datetime.now(ZoneInfo("Asia/Tokyo")).replace(tzinfo=None)
    # SQLAlchemyセッションで変更をデータベースにコミット
    await db.commit()
    # データベースから最新の状態を再取得
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
    # ZoneInfoで日本時間を取得し、replace()でタイムゾーン情報を削除して保存
    user.deleted_at = datetime.now(ZoneInfo("Asia/Tokyo")).replace(tzinfo=None)
    # SQLAlchemyセッションで変更をデータベースにコミット
    await db.commit()
    # データベースから最新の状態を再取得
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
    # securityモジュールのhash_password関数でbcryptハッシュ化を実行
    user.hashed_password = hash_password(new_password)
    user.user_status = User.STATUS_ACTIVE
    user.deleted_at = None
    # ZoneInfoで日本時間を取得し、replace()でタイムゾーン情報を削除して保存
    user.updated_at = datetime.now(ZoneInfo("Asia/Tokyo")).replace(tzinfo=None)
    # SQLAlchemyセッションで変更をデータベースにコミット
    await db.commit()
    # データベースから最新の状態を再取得
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

    # FastAPIのRequestオブジェクトのcookiesからauthTokenクッキーを取得
    token = request.cookies.get("authToken")
    if not token:
        raise credentials_exception

    try:
        # securityモジュールのdecode_access_tokenでJWTトークンをデコードしメールを取得
        logger.info("get_current_user - decoding access token", token_length=len(token))
        payload = decode_access_token(token)
        logger.info("get_current_user - JWT payload", payload=payload)
        email: str | None = payload.get("email")
        logger.info("get_current_user - extracted email", email=email)
        if email is None:
            logger.error("get_current_user - email not found in payload")
            raise credentials_exception
    except Exception as e:
        logger.error("get_current_user - token decode error", error=str(e), error_type=type(e).__name__)
        raise credentials_exception from None

    # メールアドレスでデータベースからユーザーを検索
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
    # securityモジュールのhash_passwordでbcryptハッシュ化を実行
    hashed_password = hash_password(password)

    new_user = User(
        # uuid.uuid4()でランダムUUIDを生成し文字列へ変換
        user_id=str(uuid.uuid4()),
        email=email,
        username=username,
        hashed_password=hashed_password,
        user_role=User.ROLE_FREE,  # デフォルトで無料会員として設定
        user_status=User.STATUS_ACTIVE,
        # ZoneInfoで日本時間を取得しreplace()でタイムゾーン情報を削除して保存
        created_at=datetime.now(ZoneInfo("Asia/Tokyo")).replace(tzinfo=None),
        updated_at=datetime.now(ZoneInfo("Asia/Tokyo")).replace(tzinfo=None),
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
    # securityモジュールのcreate_verification_tokenでJWTトークンを作成（timedeltaで24時間の有効期限設定）
    verification_token = create_verification_token(data=token_data, expires_delta=timedelta(hours=24))

    # FastAPIのBackgroundTasksで非同期メール送信タスクを追加
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
        # securityモジュールのdecode_verification_tokenでJWTトークンをデコード
        payload = decode_verification_token(token)
        email: str | None = payload.get("email")
        username: str | None = payload.get("username")
        password: str | None = payload.get("password")

        if email is None or username is None or password is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="無効な認証トークンです")

        return UserCreate(email=email, username=username, password=password, user_role=User.ROLE_FREE, user_status=User.STATUS_ACTIVE)
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="無効な認証トークンです") from None


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
    # securityモジュールのcreate_verification_tokenでJWTトークンを作成（timedeltaで1時間の有効期限設定）
    reset_token = create_verification_token(data={"email": email}, expires_delta=timedelta(hours=1))

    # FastAPIのBackgroundTasksで非同期メール送信タスクを追加
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
        # securityモジュールのdecode_verification_tokenでJWTトークンをデコード
        payload = decode_verification_token(token)
        email: str | None = payload.get("email")

        if email is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="無効なリセットトークンです")

        return email
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="無効なリセットトークンです") from None


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

    # securityモジュールのhash_passwordでbcryptハッシュ化を実行
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
    return await update_user_profile(db=db, user=user, username=user_update.username, email=user_update.email, contact_number=user_update.contact_number, date_of_birth=user_update.date_of_birth)


async def change_user_password(db: AsyncSession, user: User, current_password: str, new_password: str) -> None:
    """ユーザーのパスワードを変更します。

    Args:
        db (AsyncSession): 非同期データベースセッション。
        user (User): パスワード変更対象のユーザー。
        current_password (str): 現在のパスワード。
        new_password (str): 新しいパスワード。

    Raises:
        HTTPException: 現在のパスワードが間違っている場合、またはGoogleユーザーの場合。
    """
    logger.info("change_user_password - start", user_id=user.user_id, email=user.email)

    try:
        # Googleユーザー（パスワードが空）の場合はエラー
        if not user.hashed_password:
            logger.warning("change_user_password - google_user_cannot_change_password", user_id=user.user_id)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Googleアカウントでログインしたユーザーはパスワード変更できません",
            )

        # securityモジュールのverify_passwordで現在のパスワードを検証
        if not verify_password(current_password, user.hashed_password):
            logger.warning("change_user_password - invalid_current_password", user_id=user.user_id)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="現在のパスワードが正しくありません",
            )

        # securityモジュールのhash_passwordで新しいパスワードをbcryptハッシュ化
        new_hashed_password = hash_password(new_password)

        # パスワードを更新
        await update_user_password(db, user, new_hashed_password)

        logger.info("change_user_password - success", user_id=user.user_id)

    finally:
        logger.info("change_user_password - end")


async def get_profile_info(user: User) -> dict:
    """ユーザーのプロフィール情報を取得します。

    Args:
        user (User): プロフィール情報を取得するユーザー。

    Returns:
        dict: プロフィール情報辞書。
    """
    logger.info("get_profile_info - start", user_id=user.user_id)

    try:
        # Googleユーザーかどうかを判定（hashed_passwordが空の場合）
        is_google_user = not bool(user.hashed_password)

        profile_data = {
            "email": user.email,
            "username": user.username,
            "contact_number": user.contact_number,
            "date_of_birth": user.date_of_birth,
            "user_role": user.user_role,
            "user_status": user.user_status,
            "profile_image_url": None,  # 将来的にプロフィール画像機能で使用
            "is_google_user": is_google_user,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
        }

        logger.info("get_profile_info - success", user_id=user.user_id, is_google_user=is_google_user)
        return profile_data

    finally:
        logger.info("get_profile_info - end")


async def link_google_account_to_email_user(db: AsyncSession, email_user: User, google_sub: str, google_full_name: str) -> User:
    """メールユーザーにGoogleアカウントを連携します。

    Args:
        db (AsyncSession): 非同期データベースセッション。
        email_user (User): 連携対象のメールユーザー。
        google_sub (str): GoogleのユニークID。
        google_full_name (str): Googleアカウントのフルネーム。

    Returns:
        User: 連携完了したユーザー。

    Raises:
        HTTPException: 連携に失敗した場合。
    """
    logger.info("link_google_account_to_email_user - start", user_id=email_user.user_id, google_sub=google_sub)

    try:
        # 既にパスワードが設定されているメールユーザーであることを確認
        if not email_user.hashed_password:
            logger.error("link_google_account_to_email_user - not_email_user", user_id=email_user.user_id)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="このアカウントはメールユーザーではありません",
            )

        # 将来のアカウント連携テーブルでの管理を想定
        # 現時点ではユーザーテーブルに連携情報を保存する可能性を示す
        # google_subフィールドやlinked_accountsフィールドの追加が必要

        # 今回は基本的なユーザー情報更新のみ実装
        email_user.updated_at = datetime.now(ZoneInfo("Asia/Tokyo"))

        await db.commit()
        await db.refresh(email_user)

        logger.info("link_google_account_to_email_user - success", user_id=email_user.user_id)
        return email_user

    finally:
        logger.info("link_google_account_to_email_user - end")


async def link_email_account_to_google_user(db: AsyncSession, google_user: User, password: str) -> User:
    """メールアカウント機能をGoogleユーザーに連携（パスワード追加）します。

    Args:
        db (AsyncSession): 非同期データベースセッション。
        google_user (User): 連携対象のGoogleユーザー。
        password (str): 設定するパスワード。

    Returns:
        User: 連携完了したユーザー。

    Raises:
        HTTPException: 連携に失敗した場合。
    """
    logger.info("link_email_account_to_google_user - start", user_id=google_user.user_id)

    try:
        # 既にGoogleユーザー（パスワードが空）であることを確認
        if google_user.hashed_password:
            logger.error("link_email_account_to_google_user - not_google_user", user_id=google_user.user_id)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="このアカウントは既にメール認証に対応しています",
            )

        # パスワードをハッシュ化して設定
        google_user.hashed_password = hash_password(password)
        google_user.updated_at = datetime.now(ZoneInfo("Asia/Tokyo"))

        await db.commit()
        await db.refresh(google_user)

        logger.info("link_email_account_to_google_user - success", user_id=google_user.user_id)
        return google_user

    finally:
        logger.info("link_email_account_to_google_user - end")


async def get_account_linking_status(user: User) -> dict:
    """ユーザーのアカウント連携状態を取得します。

    Args:
        user (User): アカウント連携状態を確認するユーザー。

    Returns:
        dict: アカウント連携情報。
    """
    logger.info("get_account_linking_status - start", user_id=user.user_id)

    try:
        # Googleユーザーかどうかを判定
        is_google_user = not bool(user.hashed_password)

        # 連携済みアカウントタイプを算出
        linked_accounts = []
        if user.hashed_password:  # メール認証が利用可能
            linked_accounts.append("email")
        # 将来的にはgoogle_subフィールドや連携テーブルで判定
        # 現時点では簡単な推定でGoogle連携を判定
        if is_google_user or not user.hashed_password:
            linked_accounts.append("google")

        # プライマリアカウントを決定
        if is_google_user:
            primary_account = "google"
        else:
            primary_account = "email"

        linking_info = {
            "user_email": user.email,
            "linked_accounts": linked_accounts,
            "primary_account": primary_account,
            "is_google_user": is_google_user,
            "has_password": bool(user.hashed_password),
            "can_use_email_login": bool(user.hashed_password),
            "can_use_google_login": True,  # 将来的にはgoogle_subや連携テーブルで判定
        }

        logger.info("get_account_linking_status - success", user_id=user.user_id, primary_account=primary_account)
        return linking_info

    finally:
        logger.info("get_account_linking_status - end")


async def update_advanced_user_profile(db: AsyncSession, user: User, user_update: AdvancedUserUpdate) -> User:
    """AdvancedUserUpdateスキーマを使って高度なユーザー情報を更新します。

    Args:
        db (AsyncSession): 非同期データベースセッション。
        user (User): 更新対象のユーザーオブジェクト。
        user_update (AdvancedUserUpdate): 高度な更新データ。

    Returns:
        User: 更新されたユーザーオブジェクト。

    Raises:
        HTTPException: メールアドレスが既に使用されている場合等。
    """
    logger.info("update_advanced_user_profile - start", user_id=user.user_id)

    try:
        # メールアドレスの重複チェック
        if user_update.email and user_update.email != user.email:
            existing_user = await get_user_by_email(db, user_update.email)
            if existing_user:
                logger.warning("update_advanced_user_profile - email_already_exists", email=user_update.email)
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="このメールアドレスは既に使用されています",
                )

        # ユーザー名の重複チェック
        if user_update.username and user_update.username != user.username:
            username_query = select(User).where(User.username == user_update.username, User.user_status == User.STATUS_ACTIVE, User.deleted_at.is_(None))
            username_result = await db.execute(username_query)
            existing_username_user = username_result.scalars().first()

            if existing_username_user:
                logger.warning("update_advanced_user_profile - username_already_exists", username=user_update.username)
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="このユーザー名は既に使用されています",
                )

        # フィールドの更新
        if user_update.email is not None:
            user.email = user_update.email
        if user_update.username is not None:
            user.username = user_update.username
        if user_update.contact_number is not None:
            user.contact_number = user_update.contact_number
        if user_update.date_of_birth is not None:
            user.date_of_birth = user_update.date_of_birth  # type: ignore[assignment]
        # profile_image_urlは将来的にUserモデルに追加予定

        # 更新日時を設定
        user.updated_at = datetime.now(ZoneInfo("Asia/Tokyo")).replace(tzinfo=None)

        await db.commit()
        await db.refresh(user)

        logger.info("update_advanced_user_profile - success", user_id=user.user_id)
        return user

    finally:
        logger.info("update_advanced_user_profile - end")


# ============================================================================
# 管理者用機能
# ============================================================================


async def get_all_users_for_admin(db: AsyncSession, page: int = 1, page_size: int = 20, include_deleted: bool = False) -> tuple[list[User], int]:
    """管理者用: 全ユーザー一覧を取得します（ページネーション対応）。

    Args:
        db (AsyncSession): 非同期データベースセッション。
        page (int): ページ番号（1から開始）。
        page_size (int): 1ページあたりの件数。
        include_deleted (bool): 削除済みユーザーを含むかどうか。

    Returns:
        tuple[list[User], int]: (ユーザーリスト, 全件数)のタプル。

    Raises:
        HTTPException: データ取得に失敗した場合。
    """
    logger.info("get_all_users_for_admin - start", page=page, page_size=page_size, include_deleted=include_deleted)

    try:
        # 基本クエリ
        base_query = select(User)

        if not include_deleted:
            base_query = base_query.where(User.deleted_at.is_(None))

        # 全件数を取得するためのクエリ
        from sqlalchemy import func

        # SQLAlchemyのfunc.count()関数でレコード数をカウント
        count_query = select(func.count(User.user_id))
        if not include_deleted:
            count_query = count_query.where(User.deleted_at.is_(None))

        # 非同期データベースセッションでカウントクエリを実行
        count_result = await db.execute(count_query)
        # scalar()で単一のスカラー値を取得
        total_count = count_result.scalar()

        # ページネーション用クエリ
        offset = (page - 1) * page_size
        # SQLAlchemyのorder_by()で作成日時順の降順ソート、offset()でオフセット、limit()で件数制限
        paginated_query = base_query.order_by(User.created_at.desc()).offset(offset).limit(page_size)

        # 非同期データベースセッションでページネーションクエリを実行
        result = await db.execute(paginated_query)
        # scalars().all()で全てのスカラー値をリストで取得
        users = result.scalars().all()

        logger.info("get_all_users_for_admin - success", user_count=len(users), total_count=total_count)
        return list(users), total_count

    finally:
        logger.info("get_all_users_for_admin - end")


async def get_user_by_id_for_admin(db: AsyncSession, user_id: str) -> User:
    """管理者用: ユーザーIDでユーザーを取得します（削除済みユーザーも含む）。

    Args:
        db (AsyncSession): 非同期データベースセッション。
        user_id (str): 取得するユーザーのID。

    Returns:
        User: 取得されたユーザーオブジェクト。

    Raises:
        HTTPException: ユーザーが見つからない場合。
    """
    logger.info("get_user_by_id_for_admin - start", user_id=user_id)

    try:
        # UUIDの形式チェック
        try:
            # uuid.UUID()コンストラクタで文字列をUUIDオブジェクトに変換して形式検証
            uuid_obj = uuid.UUID(user_id)
        except ValueError:
            logger.warning("get_user_by_id_for_admin - invalid_uuid", user_id=user_id)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="無効なユーザーIDです",
            ) from None

        # SQLAlchemyのselectでユーザーID検索クエリを構築（削除済みも含めて検索）
        query = select(User).where(User.user_id == uuid_obj)
        # 非同期データベースセッションでクエリを実行
        result = await db.execute(query)
        # scalars().first()でスカラー値の最初のレコードを取得
        user = result.scalars().first()

        if not user:
            logger.warning("get_user_by_id_for_admin - user_not_found", user_id=user_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="ユーザーが見つかりません",
            )

        logger.info("get_user_by_id_for_admin - success", user_id=user.user_id)
        return user

    finally:
        logger.info("get_user_by_id_for_admin - end")


async def update_user_by_admin(db: AsyncSession, user_id: str, user_update: AdminUserUpdateRequest) -> User:
    """管理者用: ユーザー情報を更新します。

    Args:
        db (AsyncSession): 非同期データベースセッション。
        user_id (str): 更新するユーザーのID。
        user_update (AdminUserUpdateRequest): 更新データ。

    Returns:
        User: 更新されたユーザーオブジェクト。

    Raises:
        HTTPException: ユーザーが見つからない場合やメールアドレスが重複している場合。
    """
    logger.info("update_user_by_admin - start", user_id=user_id)

    try:
        # 対象ユーザーを取得
        user = await get_user_by_id_for_admin(db, user_id)

        # メールアドレスの重複チェック
        if user_update.email and user_update.email != user.email:
            existing_user = await get_user_by_email(db, user_update.email)
            if existing_user:
                logger.warning("update_user_by_admin - email_already_exists", email=user_update.email)
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="このメールアドレスは既に使用されています",
                )

        # ユーザー名の重複チェック
        if user_update.username and user_update.username != user.username:
            # SQLAlchemyのselectでユーザー名重複確認クエリを構築（自分以外のユーザーで同じユーザー名を検索）
            username_query = select(User).where(
                User.username == user_update.username,
                User.user_status == User.STATUS_ACTIVE,
                User.deleted_at.is_(None),
                User.user_id != user.user_id,  # 自分自身は除外
            )
            # 非同期データベースセッションでクエリを実行
            username_result = await db.execute(username_query)
            # scalars().first()でスカラー値の最初のレコードを取得
            existing_username_user = username_result.scalars().first()

            if existing_username_user:
                logger.warning("update_user_by_admin - username_already_exists", username=user_update.username)
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="このユーザー名は既に使用されています",
                )

        # フィールドの更新
        if user_update.email is not None:
            user.email = user_update.email
        if user_update.username is not None:
            user.username = user_update.username
        if user_update.user_role is not None:
            user.user_role = user_update.user_role
        if user_update.user_status is not None:
            user.user_status = user_update.user_status
        if user_update.contact_number is not None:
            user.contact_number = user_update.contact_number
        if user_update.date_of_birth is not None:
            user.date_of_birth = user_update.date_of_birth  # type: ignore[assignment]

        # ZoneInfoで日本時間を取得して更新日時を設定
        user.updated_at = datetime.now(ZoneInfo("Asia/Tokyo"))

        # SQLAlchemyセッションで変更をデータベースにコミット
        await db.commit()
        # データベースから最新の状態を再取得
        await db.refresh(user)

        logger.info("update_user_by_admin - success", user_id=user.user_id)
        return user

    finally:
        logger.info("update_user_by_admin - end")


async def delete_user_by_admin(db: AsyncSession, user_id: str, permanent: bool = False) -> User:
    """管理者用: ユーザーを削除します（論理削除または物理削除）。

    Args:
        db (AsyncSession): 非同期データベースセッション。
        user_id (str): 削除するユーザーのID。
        permanent (bool): 物理削除を行うかどうか（デフォルト: False）。

    Returns:
        User: 削除されたユーザーオブジェクト（論理削除の場合のみ）。

    Raises:
        HTTPException: ユーザーが見つからない場合。
    """
    logger.info("delete_user_by_admin - start", user_id=user_id, permanent=permanent)

    try:
        # 対象ユーザーを取得
        user = await get_user_by_id_for_admin(db, user_id)

        if permanent:
            # SQLAlchemyセッションでUserオブジェクトを物理削除
            await db.delete(user)
            logger.info("delete_user_by_admin - permanent_delete", user_id=user.user_id)
        else:
            # 論理削除（ステータスをSUSPENDEDに変更し削除日時を記録）
            user.user_status = User.STATUS_SUSPENDED
            # ZoneInfoで日本時間を取得して削除・更新日時を設定
            user.deleted_at = datetime.now(ZoneInfo("Asia/Tokyo"))
            user.updated_at = datetime.now(ZoneInfo("Asia/Tokyo"))
            logger.info("delete_user_by_admin - logical_delete", user_id=user.user_id)

        # SQLAlchemyセッションで変更をデータベースにコミット
        await db.commit()

        if not permanent:
            # 論理削除の場合のみデータベースから最新の状態を再取得
            await db.refresh(user)

        logger.info("delete_user_by_admin - success", user_id=user_id, permanent=permanent)
        return user

    finally:
        logger.info("delete_user_by_admin - end")


async def restore_deleted_user_by_admin(db: AsyncSession, user_id: str) -> User:
    """管理者用: 論理削除されたユーザーを復活させます。

    Args:
        db (AsyncSession): 非同期データベースセッション。
        user_id (str): 復活させるユーザーのID。

    Returns:
        User: 復活されたユーザーオブジェクト。

    Raises:
        HTTPException: ユーザーが見つからない場合や既にアクティブな場合。
    """
    logger.info("restore_deleted_user_by_admin - start", user_id=user_id)

    try:
        # 対象ユーザーを取得
        user = await get_user_by_id_for_admin(db, user_id)

        # 削除済みユーザーかどうかチェック
        if user.deleted_at is None or user.user_status != User.STATUS_SUSPENDED:
            logger.warning("restore_deleted_user_by_admin - user_not_deleted", user_id=user.user_id)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="このユーザーは削除されていません",
            )

        # メールアドレスの重複チェック（復活時）
        existing_user = await get_user_by_email(db, user.email)
        if existing_user and existing_user.user_id != user.user_id:
            logger.warning("restore_deleted_user_by_admin - email_conflict", email=user.email)
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="このメールアドレスは既に使用されています",
            )

        # ユーザーを復活（ステータスをACTIVEに変更し削除日時をクリア）
        user.user_status = User.STATUS_ACTIVE
        user.deleted_at = None
        # ZoneInfoで日本時間を取得して更新日時を設定
        user.updated_at = datetime.now(ZoneInfo("Asia/Tokyo"))

        # SQLAlchemyセッションで変更をデータベースにコミット
        await db.commit()
        # データベースから最新の状態を再取得
        await db.refresh(user)

        logger.info("restore_deleted_user_by_admin - success", user_id=user.user_id)
        return user

    finally:
        logger.info("restore_deleted_user_by_admin - end")
