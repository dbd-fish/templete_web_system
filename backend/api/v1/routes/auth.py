"""
認証API（FastAPI公式テンプレート準拠）
"""

import structlog
from typing import Annotated
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from api.common.database import get_db
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

# ログ設定
logger = structlog.get_logger()

router = APIRouter()


@router.post(
    "/signup",
    response_model=SuccessResponse[dict],
    summary="ユーザー登録（メール認証後）",
    description="""メール認証トークンを使用してユーザーアカウントを正式に登録します。
    
    事前に `/send-verify-email` エンドポイントで仮登録を行い、
    メールで受信した認証トークンを使用してください。
    
    **フロー:**
    1. `/send-verify-email` で仮登録
    2. メールで認証トークンを受信
    3. このエンドポイントで本登録完了
    """,
    responses={
        200: {
            "description": "ユーザー登録成功",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "ユーザー登録が正常に完了しました",
                        "timestamp": "2025-07-02T12:00:00+09:00",
                        "data": {"user_id": "123e4567-e89b-12d3-a456-426614174000"}
                    }
                }
            }
        },
        400: {
            "description": "メールアドレス重複エラー",
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "message": "このメールアドレスは既に登録されています",
                        "error_code": "RESOURCE_002",
                        "timestamp": "2025-07-02T12:00:00+09:00"
                    }
                }
            }
        },
        422: {
            "description": "トークン検証エラー",
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "message": "入力データの検証に失敗しました",
                        "error_code": "VALID_001",
                        "timestamp": "2025-07-02T12:00:00+09:00"
                    }
                }
            }
        }
    },
    tags=["認証"]
)
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
        # メール認証トークンからユーザー情報を取得
        user_info = await verify_email_token(token_data.token)
        logger.info("register_user - user_info", user_info=user_info)
        
        # メール重複チェック
        existing_user = await UserRepository.get_user_by_email(session, user_info.email)
        if existing_user:
            raise BusinessLogicError(
                message="このメールアドレスは既に登録されています",
                error_code=ErrorCodes.RESOURCE_ALREADY_EXISTS
            )
        
        # 新規ユーザーの作成
        new_user = await create_user(user_info.email, user_info.username, user_info.password, session)
        logger.info("register_user - success", user_id=new_user.user_id)
        
        return create_success_response(
            message="ユーザー登録が正常に完了しました",
            data={"user_id": str(new_user.user_id)}
        )
    finally:
        logger.info("register_user - end")


@router.post(
    "/send-verify-email",
    response_model=SuccessResponse[None],
    summary="仮登録用メール送信",
    description="""新規ユーザー登録のための認証メールを送信します。
    
    メールアドレス、ユーザー名、パスワードを受け取り、
    認証トークンを含むメールを送信します。
    
    **注意事項:**
    - メールアドレスは重複チェックされます
    - パスワードは安全に暗号化されます
    - 認証メール受信後、`/signup` で本登録を完了してください
    """,
    responses={
        200: {
            "description": "認証メール送信成功",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "認証用メールを送信しました",
                        "timestamp": "2025-07-02T12:00:00+09:00",
                        "data": None
                    }
                }
            }
        },
        400: {
            "description": "メールアドレス重複エラー",
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "message": "このメールアドレスは既に登録されています",
                        "error_code": "RESOURCE_002",
                        "timestamp": "2025-07-02T12:00:00+09:00"
                    }
                }
            }
        }
    },
    tags=["認証"]
)
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


@router.post(
    "/login",
    response_model=SuccessResponse[None],
    summary="ログイン",
    description="""ユーザー認証を行いJWTトークンを発行します。
    
    メールアドレスとパスワードで認証を行い、
    認証成功時にHttpOnlyクッキーとしてJWTトークンを設定します。
    
    **認証情報:**
    - username: メールアドレス
    - password: ユーザーパスワード
    
    **セキュリティ:**
    - JWT トークンは HttpOnly クッキーに格納
    - 有効期限: 3時間
    - Secure フラグ有効（HTTPS必須）
    """,
    responses={
        200: {
            "description": "ログイン成功",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "ログインが正常に完了しました",
                        "timestamp": "2025-07-02T12:00:00+09:00",
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
                        "success": False,
                        "message": "ユーザー名またはパスワードが正しくありません",
                        "error_code": "AUTH_001",
                        "timestamp": "2025-07-02T12:00:00+09:00"
                    }
                }
            }
        }
    },
    tags=["認証"]
)
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
        # ユーザー認証の実行
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
        
        # クライアントIPアドレスの取得
        client_host = (
            request.headers.get("X-Forwarded-For")
            or (request.client.host if request.client else "unknown")
        )
        
        # JWTアクセストークンの生成
        access_token = create_access_token(subject=str(user.user_id))
        logger.info("login - success", user_id=user.user_id)
        
        # セキュアなHttpOnlyクッキーとしてトークンを設定
        response.set_cookie(
            key="authToken",
            value=access_token,
            httponly=True,
            max_age=60 * 60 * 3,  # クッキーの有効期限: 3時間
            secure=True,
            samesite="lax"
        )
        
        return create_success_response(
            message="ログインが正常に完了しました"
        )
    finally:
        logger.info("login - end")


@router.post(
    "/logout",
    response_model=SuccessResponse[None],
    summary="ログアウト",
    description="""ユーザーログアウト処理を行います。
    
    現在はクライアント側でのトークン削除を想定した
    シンプルな実装となっています。
    
    **注意事項:**
    - HttpOnlyクッキーのトークンはクライアント側で削除してください
    - サーバー側でのトークン無効化は現在未実装
    """,
    responses={
        200: {
            "description": "ログアウト成功",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "ログアウトが正常に完了しました",
                        "timestamp": "2025-07-02T12:00:00+09:00",
                        "data": None
                    }
                }
            }
        }
    },
    tags=["認証"]
)
async def logout() -> dict:
    """
    ログアウト処理
    
    Returns:
        dict: ログアウト成功メッセージ
    """
    logger.info("logout - start")
    try:
        # クライアント側でのトークン削除を想定したシンプルな処理
        logger.info("logout - success")
        return create_success_response(
            message="ログアウトが正常に完了しました"
        )
    finally:
        logger.info("logout - end")


@router.post(
    "/send-password-reset-email",
    response_model=SuccessResponse[None],
    summary="パスワードリセットメール送信",
    description="""パスワードリセット用の認証メールを送信します。
    
    登録済みのメールアドレスに対してパスワードリセット用の
    トークンを含むメールを送信します。
    
    **フロー:**
    1. このエンドポイントでリセットメール送信
    2. メールでリセットトークンを受信
    3. `/reset-password` で新しいパスワードを設定
    
    **セキュリティ:**
    - リセットトークンには有効期限があります
    - メールアドレスが存在しない場合でも同じレスポンス
    """,
    responses={
        200: {
            "description": "リセットメール送信成功",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "パスワードリセット用メールを送信しました",
                        "timestamp": "2025-07-02T12:00:00+09:00",
                        "data": None
                    }
                }
            }
        }
    },
    tags=["認証"]
)
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
        # 段階的移行: 既存のパスワードリセット機能を使用
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


@router.post(
    "/reset-password",
    response_model=SuccessResponse[None],
    summary="パスワードリセット",
    description="""リセットトークンを使用してパスワードを変更します。
    
    `/send-password-reset-email` で送信されたメールから
    リセットトークンを取得し、新しいパスワードを設定します。
    
    **セキュリティ:**
    - リセットトークンは一度のみ使用可能
    - トークンには有効期限があります
    - 新しいパスワードは安全に暗号化されます
    
    **注意事項:**
    - パスワード変更後は再ログインが必要です
    """,
    responses={
        200: {
            "description": "パスワードリセット成功",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "パスワードのリセットが正常に完了しました",
                        "timestamp": "2025-07-02T12:00:00+09:00",
                        "data": None
                    }
                }
            }
        },
        400: {
            "description": "無効なトークン",
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "message": "無効なリセットトークンです",
                        "error_code": "AUTH_004",
                        "timestamp": "2025-07-02T12:00:00+09:00"
                    }
                }
            }
        }
    },
    tags=["認証"]
)
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
        # リセットトークンからメールアドレスを取得
        email = await decode_password_reset_token(reset_data.token)
        
        # 新しいパスワードでのリセット実行
        await reset_password(email, reset_data.new_password, session)
        
        logger.info("reset_password - success")
        return create_success_response(
            message="パスワードのリセットが正常に完了しました"
        )
    finally:
        logger.info("reset_password - end")