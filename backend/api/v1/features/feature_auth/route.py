import structlog
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from api.common.database import get_db
from api.v1.features.feature_auth.crud import create_user_service, decode_password_reset_token, get_current_user, reset_password, reset_password_email, temporary_create_user, verify_email_token, update_user_with_schema, delete_user
from api.v1.features.feature_auth.schemas.user import PasswordResetData, SendPasswordResetEmailData, TokenData, UserCreate, UserResponse, UserUpdate
from api.v1.features.feature_auth.security import authenticate_user, create_access_token
from api.v1.features.feature_auth.models.user import User
from api.common.response_schemas import SuccessResponse, MessageResponse, EmptyData, create_success_response, create_message_response, ErrorCodes
from api.common.exception_handlers import BusinessLogicError

# ログの設定
logger = structlog.get_logger()

router = APIRouter()

@router.post("/me", response_model=SuccessResponse[UserResponse])
async def get_me(request: Request, db: AsyncSession = Depends(get_db)):
    """現在ログインしているユーザーの情報を取得するエンドポイント。

    Args:
        request (Request): リクエストオブジェクト（クッキーの解析に使用）。
        db (AsyncSession): 非同期データベースセッション。

    Returns:
        SuccessResponse[UserResponse]: ログイン中のユーザー情報。

    """
    logger.info("get_me - start")
    try:
        user = await get_current_user(request, db)
        logger.info("get_me - success", user_id=user.user_id)
        user_data = UserResponse.model_validate(user)
        return create_success_response(
            message="ユーザー情報を取得しました",
            data=user_data.model_dump()
        )
    finally:
        logger.info("get_me - end")

@router.post("/signup", response_model=SuccessResponse[UserResponse])
async def register_user(tokenData: TokenData, db: AsyncSession = Depends(get_db)):
    """新しいユーザーを登録するエンドポイント。

    Args:
        tokenData (TokenData): メール認証トークン。
        db (AsyncSession): 非同期データベースセッション。

    Returns:
        SuccessResponse[UserResponse]: 登録成功メッセージと新規ユーザー情報。

    """
    logger.info("register_user - start",)
    try:
        # tokenからuser情報を取得
        user_info = await verify_email_token(tokenData.token)
        logger.info("register_user - user_info", user_info=user_info)
        # トークンから取得したユーザー情報でユーザー登録
        new_user = await create_user_service(user_info.email, user_info.username, user_info.password, db)
        logger.info("register_user - success", user_id=new_user.user_id)
        user_data = UserResponse.model_validate(new_user)
        return create_success_response(
            message="ユーザー登録が完了しました",
            data=user_data.model_dump()
        )
    finally:
        logger.info("register_user - end")

@router.post("/send-verify-email", response_model=SuccessResponse[MessageResponse])
async def send_verify_email(user: UserCreate, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)):
    """新しいユーザーの仮登録用メールを送信するするエンドポイント。

    Args:
        user (UserCreate): 新規ユーザーの情報（メール、ユーザー名、パスワード）。
        db (AsyncSession): 非同期データベースセッション。

    Returns:
        SuccessResponse[MessageResponse]: 認証メール送信成功メッセージ。

    """
    logger.info("temporary_register_user - start", email=user.email, username=user.username)
    try:
        await temporary_create_user(user=user, background_tasks=background_tasks, db=db)
        logger.info("temporary_register_user - success")
        return create_message_response(
            message="認証メールを送信しました。メールをご確認ください"
        )
    finally:
        logger.info("temporary_register_user - end")

@router.post(
    "/login", 
    response_model=SuccessResponse[MessageResponse],
    summary="ユーザーログイン",
    description="""ユーザー名（またはメールアドレス）とパスワードでログインします。
    
    **テスト用アカウント:**
    - ユーザー名: `testuser`
    - パスワード: `Password123456+-`
    
    **レスポンス:**
    - 成功時：HttpOnlyクッキーにJWTトークンを設定
    - 失敗時：401エラー（認証失敗）
    """,
    responses={
        200: {
            "description": "ログイン成功",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "ログインに成功しました",
                        "timestamp": "2025-07-03T12:00:00+09:00",
                        "data": None
                    }
                }
            }
        },
        401: {
            "description": "認証失敗",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Incorrect username or password"
                    }
                }
            }
        }
    },
    openapi_extra={
        "requestBody": {
            "content": {
                "application/x-www-form-urlencoded": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "username": {
                                "type": "string",
                                "title": "Username",
                                "description": "ユーザー名またはメールアドレス",
                                "default": "testuser",
                                "example": "testuser"
                            },
                            "password": {
                                "type": "string",
                                "title": "Password",
                                "description": "パスワード",
                                "default": "Password123456+-",
                                "example": "Password123456+-"
                            }
                        },
                        "required": ["username", "password"]
                    }
                }
            }
        }
    },
    tags=["認証"]
)
async def login(request: Request, response: Response, form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    """ログイン処理を行うエンドポイント。

    Args:
        response (Response): レスポンスオブジェクト。
        form_data (OAuth2PasswordRequestForm): ユーザー名とパスワード。
        db (AsyncSession): 非同期データベースセッション。

    Returns:
        SuccessResponse[MessageResponse]: ログイン成功メッセージ。

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
        return create_message_response(
            message="ログインに成功しました"
        )
    finally:
        logger.info("login - end")

@router.post("/logout", response_model=SuccessResponse[MessageResponse])
async def logout(current_user: User = Depends(get_current_user)):
    """ログアウト処理を行うエンドポイント。

    Args:
        current_user (User): 現在ログイン中のユーザー。

    Returns:
        SuccessResponse[MessageResponse]: ログアウト成功メッセージ。

    """
    logger.info("logout - start", current_user=current_user.email)
    try:
        # クライアント側でトークンを削除するシンプルな処理
        logger.info("logout - success")
        return create_message_response(
            message="ログアウトしました"
        )
    finally:
        logger.info("logout - end")

@router.post("/send-password-reset-email", response_model=SuccessResponse[MessageResponse])
async def send_reset_password_email_endpoint(SendPasswordResetEmailData: SendPasswordResetEmailData, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)):
    """パスワードリセットメール送信処理を行うエンドポイント。

    Args:
        email (str): パスワードリセット対象のメールアドレス
        db (AsyncSession): 非同期データベースセッション。

    Returns:
        SuccessResponse[MessageResponse]: パスワードリセットメール送信成功メッセージ。

    """
    logger.info("send_reset_password_email_endpoint - start", email=SendPasswordResetEmailData.email)
    try:
        await reset_password_email(email=SendPasswordResetEmailData.email, background_tasks=background_tasks, db=db)
        logger.info("send_reset_password_email_endpoint - success", email=SendPasswordResetEmailData.email)
        return create_message_response(
            message="パスワードリセットメールを送信しました"
        )
    finally:
        logger.info("send_reset_password_email_endpoint - end")




@router.post("/reset-password", response_model=SuccessResponse[MessageResponse])
async def reset_password_endpoint(reset_data: PasswordResetData, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)):
    """パスワードリセット処理を行うエンドポイント。

    Args:
        reset_data (PasswordResetData): パスワード変更ユーザの情報（トークン、新しいパスワード）。
        db (AsyncSession): 非同期データベースセッション。

    Returns:
        SuccessResponse[MessageResponse]: パスワードリセット成功メッセージ。

    """
    logger.info("reset_password_endpoint - start", reset_data=reset_data)
    try:
        # tokenからemailを取得
        email = await decode_password_reset_token(reset_data.token)
        await reset_password(email, reset_data.new_password, db)
        logger.info("reset_password_endpoint - success")
        return create_message_response(
            message="パスワードが正常にリセットされました"
        )
    finally:
        logger.info("reset_password_endpoint - end")


@router.patch(
    "/me", 
    response_model=SuccessResponse[UserResponse],
    summary="ユーザー情報更新",
    description="""現在ログイン中のユーザーの情報を部分的に更新します。
    
    **認証必須:** JWTトークンが必要です。
    
    **更新可能なフィールド:**
    - username: ユーザー名
    - email: メールアドレス  
    - contact_number: 連絡先電話番号
    - date_of_birth: 生年月日
    
    **注意事項:**
    - メールアドレス変更時は再認証が必要になる場合があります
    - パスワード変更は別エンドポイントで行ってください
    """,
    responses={
        200: {
            "description": "ユーザー情報更新成功",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "ユーザー情報が正常に更新されました",
                        "timestamp": "2025-07-03T12:00:00+09:00",
                        "data": {
                            "user_id": "123e4567-e89b-12d3-a456-426614174000",
                            "username": "updated_user",
                            "email": "updated@example.com"
                        }
                    }
                }
            }
        },
        400: {
            "description": "バリデーションエラー",
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "message": "入力データの検証に失敗しました",
                        "error_code": "VALID_001",
                        "timestamp": "2025-07-03T12:00:00+09:00"
                    }
                }
            }
        },
        401: {
            "description": "認証エラー",
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "message": "認証が必要です",
                        "error_code": "AUTH_001",
                        "timestamp": "2025-07-03T12:00:00+09:00"
                    }
                }
            }
        }
    },
    tags=["認証"]
)
async def update_user_profile(user_update: UserUpdate, request: Request, db: AsyncSession = Depends(get_db)):
    """現在のユーザー情報を更新するエンドポイント。

    Args:
        user_update (UserUpdate): 更新するユーザー情報。
        request (Request): リクエストオブジェクト（認証用）。
        db (AsyncSession): 非同期データベースセッション。

    Returns:
        SuccessResponse[UserResponse]: 更新されたユーザー情報。
    """
    logger.info("update_user_profile - start")
    try:
        # 現在のユーザーを取得
        current_user = await get_current_user(request, db)
        
        # ユーザー情報を更新
        updated_user = await update_user_with_schema(db, current_user, user_update)
        logger.info("update_user_profile - success", user_id=updated_user.user_id)
        
        user_data = UserResponse.model_validate(updated_user)
        return create_success_response(
            message="ユーザー情報が正常に更新されました",
            data=user_data.model_dump()
        )
    finally:
        logger.info("update_user_profile - end")


@router.delete(
    "/me",
    response_model=SuccessResponse[MessageResponse],
    summary="ユーザーアカウント削除",
    description="""現在ログイン中のユーザーアカウントを削除します。
    
    **認証必須:** JWTトークンが必要です。
    
    **削除方式:**
    - 論理削除（ソフトデリート）を採用
    - データは実際には残るが、非アクティブ状態に変更
    - ログイン不可になり、APIアクセスも無効化
    
    **注意事項:**
    - この操作は元に戻せません
    - 削除後は再ログインが必要です
    - 関連データの処理についてはシステム管理者にお問い合わせください
    """,
    responses={
        200: {
            "description": "ユーザーアカウント削除成功",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "ユーザーアカウントが正常に削除されました",
                        "timestamp": "2025-07-03T12:00:00+09:00",
                        "data": {"message": "ユーザーアカウントが正常に削除されました"}
                    }
                }
            }
        },
        401: {
            "description": "認証エラー",
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "message": "認証が必要です",
                        "error_code": "AUTH_001",
                        "timestamp": "2025-07-03T12:00:00+09:00"
                    }
                }
            }
        }
    },
    tags=["認証"]
)
async def delete_user_account(request: Request, db: AsyncSession = Depends(get_db)):
    """現在のユーザーアカウントを削除するエンドポイント。

    Args:
        request (Request): リクエストオブジェクト（認証用）。
        db (AsyncSession): 非同期データベースセッション。

    Returns:
        SuccessResponse[MessageResponse]: 削除成功メッセージ。
    """
    logger.info("delete_user_account - start")
    try:
        # 現在のユーザーを取得
        current_user = await get_current_user(request, db)
        
        # ユーザーを論理削除
        await delete_user(db, current_user)
        logger.info("delete_user_account - success", user_id=current_user.user_id)
        
        return create_success_response(
            message="ユーザーアカウントが正常に削除されました",
            data={"message": "ユーザーアカウントが正常に削除されました"}
        )
    finally:
        logger.info("delete_user_account - end")
