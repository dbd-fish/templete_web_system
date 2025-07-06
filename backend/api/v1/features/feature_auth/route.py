import structlog
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from api.common.database import get_db
from api.common.response_schemas import MessageResponse, SuccessResponse, create_message_response, create_success_response
from api.v1.features.feature_auth.crud import (
    create_user_service,
    decode_password_reset_token,
    delete_user,
    get_current_user,
    reset_password,
    reset_password_email,
    temporary_create_user,
    update_user_with_schema,
    verify_email_token,
)
from api.v1.features.feature_auth.models.user import User
from api.v1.features.feature_auth.schemas.user import PasswordResetData, SendPasswordResetEmailData, TokenData, UserCreate, UserResponse, UserUpdate
from api.v1.features.feature_auth.security import authenticate_user, create_access_token

# ログの設定
logger = structlog.get_logger()

router = APIRouter()


@router.post(
    "/login",
    response_model=SuccessResponse[MessageResponse],
    summary="ユーザーログイン",
    description="""ユーザー名（またはメールアドレス）とパスワードでログインします。

    **処理の流れ:**
    1. フォームデータ（username/password）を受信
    2. authenticate_user()でユーザー認証を実行
    3. 認証成功時、JWTアクセストークンを生成
    4. HttpOnlyクッキーとしてトークンを設定
    5. セキュアなクッキー設定（3時間の有効期限）

    **テスト用アカウント:**
    - ユーザー名: `testuser`
    - パスワード: `Password123456+-`

    **レスポンス:**
    - 成功時：HttpOnlyクッキーにJWTトークンを設定
    - 失敗時：401エラー（認証失敗）

    **セキュリティ:**
    - HttpOnlyクッキーでXSS攻撃を防止
    - Secure属性でHTTPS通信を強制
    - SameSite=Lax設定でCSRF攻撃を軽減
    """,
    openapi_extra={
        "requestBody": {
            "content": {
                "application/x-www-form-urlencoded": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "username": {"type": "string", "title": "Username", "description": "ユーザー名またはメールアドレス", "default": "testuser", "example": "testuser"},
                            "password": {"type": "string", "title": "Password", "description": "パスワード", "default": "Password123456+-", "example": "Password123456+-"},
                        },
                        "required": ["username", "password"],
                    },
                },
            },
        },
    },
)
async def login(request: Request, response: Response, form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
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
        client_host = request.headers.get("X-Forwarded-For") or (request.client.host if request.client else "unknown")
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
            secure=True,  # HTTPSのみで送信
            samesite="lax",  # クロスサイトリクエストに対する制御
        )
        logger.info("login - success", extra={"user_id": user.user_id})
        return create_message_response(message="ログインに成功しました")
    finally:
        logger.info("login - end")


@router.post(
    "/me",
    response_model=SuccessResponse[UserResponse],
    summary="現在のユーザー情報取得",
    description="""現在ログインしているユーザーの情報を取得します。

    **処理の流れ:**
    1. RequestオブジェクトからauthTokenクッキーを取得
    2. get_current_user()でJWTトークンを検証
    3. トークンからemailを抽出してデータベース検索
    4. ユーザー情報をUserResponseスキーマに変換
    5. 成功レスポンスとして返却

    **認証方式:**
    - HttpOnlyクッキーからJWTトークンを取得
    - トークンの有効性・有効期限を検証
    - データベースでユーザー存在確認

    **パラメータ:**
    - request: リクエストオブジェクト（クッキーの解析に使用）
    - db: 非同期データベースセッション

    **レスポンス:**
    - SuccessResponse[UserResponse]: ログイン中のユーザー情報
    - 401エラー: 認証失敗時（無効なトークン・ユーザー未存在）
    """,
)
async def get_me(request: Request, db: AsyncSession = Depends(get_db)):
    logger.info("get_me - start")
    try:
        user = await get_current_user(request, db)
        logger.info("get_me - success", user_id=user.user_id)
        user_data = UserResponse.model_validate(user)
        return create_success_response(message="ユーザー情報を取得しました", data=user_data.model_dump())
    finally:
        logger.info("get_me - end")


@router.post(
    "/signup",
    response_model=SuccessResponse[UserResponse],
    summary="ユーザー本登録",
    description="""新しいユーザーを登録するエンドポイントです。

    **処理の流れ:**
    1. 認証メール内のURLから取得したJWTトークンを受信
    2. verify_email_token()でトークンの有効性を検証
    3. トークンからユーザー情報（email, username, password）を抽出
    4. create_user_service()でユーザー登録処理を実行：
       - 論理削除済みユーザーが存在する場合：復活処理を実行
       - アクティブユーザーが存在する場合：409エラーを返す
       - 新規の場合：新しいユーザーを作成
    5. パスワードはbcryptでハッシュ化して保存
    6. 作成または復活されたユーザー情報をUserResponseスキーマで返却

    **前提条件:**
    - 事前に/send-verify-emailで認証メールを送信済み
    - 認証メール内のURLからトークンを取得
    - トークンの有効期限は24時間

    **パラメータ:**
    - tokenData: メールで送信されたURLから取得できるJWTトークン
    - db: 非同期データベースセッション

    **レスポンス:**
    - SuccessResponse[UserResponse]: 登録成功メッセージと新規ユーザー情報
    - 400エラー: 無効なトークン、期限切れトークン
    - 409エラー: アクティブなユーザーが既に存在する場合
    """,
)
async def register_user(tokenData: TokenData, db: AsyncSession = Depends(get_db)):
    logger.info(
        "register_user - start",
    )
    try:
        # tokenからuser情報を取得
        user_info = await verify_email_token(tokenData.token)
        logger.info("register_user - user_info", user_info=user_info)
        # トークンから取得したユーザー情報でユーザー登録
        new_user = await create_user_service(user_info.email, user_info.username, user_info.password, db)
        logger.info("register_user - success", user_id=new_user.user_id)
        user_data = UserResponse.model_validate(new_user)
        return create_success_response(message="ユーザー登録が完了しました", data=user_data.model_dump())
    finally:
        logger.info("register_user - end")


@router.post(
    "/send-verify-email",
    response_model=SuccessResponse[MessageResponse],
    summary="仮登録・認証メール送信",
    description="""新しいユーザーの仮登録用メールを送信するエンドポイントです。

    **処理の流れ:**
    1. UserCreateスキーマでユーザー情報を受信
    2. temporary_create_user()でメール認証処理を開始
    3. ユーザー情報をJWTトークンに埋め込み（24時間有効）
    4. send_verification_email()をバックグラウンドタスクで実行
    5. メール送信は非同期で実行され、レスポンスを即座に返却

    **メール送信内容:**
    - 件名: アカウント本登録のお知らせ
    - 本文: 認証リンクURL（JWTトークン付き）
    - 有効期限: 24時間

    **セキュリティ:**
    - パスワードはトークンに含まれるが、JWTで暗号化
    - SMTP認証情報が未設定の場合はモックモードで動作

    **パラメータ:**
    - user: 新規ユーザーの情報（メール、ユーザー名、パスワード）
    - background_tasks: バックグラウンドタスク
    - db: 非同期データベースセッション

    **レスポンス:**
    - SuccessResponse[MessageResponse]: 認証メール送信成功メッセージ
    """,
)
async def send_verify_email(user: UserCreate, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)):
    logger.info("temporary_register_user - start", email=user.email, username=user.username)
    try:
        await temporary_create_user(user=user, background_tasks=background_tasks, db=db)
        logger.info("temporary_register_user - success")
        return create_message_response(message="認証メールを送信しました。メールをご確認ください")
    finally:
        logger.info("temporary_register_user - end")


@router.post(
    "/logout",
    response_model=SuccessResponse[MessageResponse],
    summary="ユーザーログアウト",
    description="""ログアウト処理を行うエンドポイントです。

    **処理の流れ:**
    1. get_current_user()でログイン中のユーザーを確認
    2. 認証クッキー（authToken）をセキュアな設定で削除
    3. ログアウト成功メッセージを返却

    **クッキー削除設定:**
    - HttpOnly: JavaScriptからアクセス不可
    - Secure: HTTPS通信でのみ有効
    - SameSite=Lax: CSRF攻撃防止

    **パラメータ:**
    - current_user: 現在ログイン中のユーザー（依存性注入で自動取得）

    **レスポンス:**
    - SuccessResponse[MessageResponse]: ログアウト成功メッセージ
    - 401エラー: 未認証状態でのアクセス時
    """,
)
async def logout(response: Response, current_user: User = Depends(get_current_user)):
    logger.info("logout - start", current_user=current_user.email)
    try:
        # 認証クッキーを削除してログアウト処理
        response.delete_cookie(key="authToken", httponly=True, secure=True, samesite="lax")
        logger.info("logout - success", user_email=current_user.email)
        return create_message_response(message="ログアウトしました")
    finally:
        logger.info("logout - end")


@router.post(
    "/send-password-reset-email",
    response_model=SuccessResponse[MessageResponse],
    summary="パスワードリセットメール送信",
    description="""パスワードリセットメール送信処理を行うエンドポイントです。

    **処理の流れ:**
    1. SendPasswordResetEmailDataでメールアドレスを受信
    2. reset_password_email()でパスワードリセット処理を開始
    3. データベースでユーザー存在確認
    4. 存在しない場合：404エラーを返す
    5. 存在する場合：JWTトークンを生成（1時間有効）
    6. send_reset_password_email()をバックグラウンドタスクで実行

    **メール送信内容:**
    - 件名: パスワードリセットのお知らせ
    - 本文: パスワードリセットリンクURL（JWTトークン付き）
    - 有効期限: 1時間

    **セキュリティ機能:**
    - トークンは1時間の短期間で有効期限切れ

    **パラメータ:**
    - SendPasswordResetEmailData: パスワードリセット対象のメールアドレス
    - background_tasks: バックグラウンドタスク
    - db: 非同期データベースセッション

    **レスポンス:**
    - SuccessResponse[MessageResponse]: パスワードリセットメール送信成功メッセージ
    - 404エラー: 指定されたメールアドレスのユーザーが見つからない場合
    """,
)
async def send_reset_password_email_endpoint(SendPasswordResetEmailData: SendPasswordResetEmailData, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)):
    logger.info("send_reset_password_email_endpoint - start", email=SendPasswordResetEmailData.email)
    try:
        await reset_password_email(email=SendPasswordResetEmailData.email, background_tasks=background_tasks, db=db)
        logger.info("send_reset_password_email_endpoint - success", email=SendPasswordResetEmailData.email)
        return create_message_response(message="パスワードリセットメールを送信しました")
    finally:
        logger.info("send_reset_password_email_endpoint - end")


@router.post(
    "/reset-password",
    response_model=SuccessResponse[MessageResponse],
    summary="パスワードリセット実行",
    description="""パスワードリセット処理を行うエンドポイントです。

    **処理の流れ:**
    1. PasswordResetDataでトークンと新しいパスワードを受信
    2. decode_password_reset_token()でJWTトークンを検証
    3. トークンからメールアドレスを抽出
    4. reset_password()でパスワード更新処理を実行
    5. 新しいパスワードをbcryptでハッシュ化
    6. データベースでユーザーのパスワードを更新

    **前提条件:**
    - 事前に/send-password-reset-emailでリセットメールを送信済み
    - リセットメール内のURLからトークンを取得
    - トークンの有効期限は1時間

    **セキュリティ:**
    - JWTトークンの有効性・有効期限を厳密に検証
    - パスワードはbcryptで安全にハッシュ化
    - トークンは一回限りの使用（時間ベースで自動失効）

    **パラメータ:**
    - reset_data: パスワード変更ユーザの情報（トークン、新しいパスワード）
    - background_tasks: バックグラウンドタスク
    - db: 非同期データベースセッション

    **レスポンス:**
    - SuccessResponse[MessageResponse]: パスワードリセット成功メッセージ
    - 400エラー: 無効なトークン、期限切れトークン
    - 404エラー: ユーザーが見つからない場合
    """,
)
async def reset_password_endpoint(reset_data: PasswordResetData, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)):
    logger.info("reset_password_endpoint - start", reset_data=reset_data)
    try:
        # tokenからemailを取得
        email = await decode_password_reset_token(reset_data.token)
        await reset_password(email, reset_data.new_password, db)
        logger.info("reset_password_endpoint - success")
        return create_message_response(message="パスワードが正常にリセットされました")
    finally:
        logger.info("reset_password_endpoint - end")


@router.patch(
    "/me",
    response_model=SuccessResponse[UserResponse],
    summary="ユーザー情報更新",
    description="""現在ログイン中のユーザーの情報を部分的に更新します。

    **処理の流れ:**
    1. get_current_user()で現在のユーザーを取得・認証
    2. UserUpdateスキーマで更新データを受信
    3. update_user_with_schema()でユーザー情報を更新
    4. 更新されたユーザー情報で新しいJWTトークンを生成
    5. 新しいトークンをHttpOnlyクッキーに設定
    6. 更新されたユーザー情報をレスポンスで返却

    **自動トークン更新:**
    - ユーザー情報更新後、新しいJWTトークンを自動生成
    - 古いトークンは自動的に無効化
    - セッションの継続性を保証

    **認証必須:** JWTトークンが必要です。

    **更新可能なフィールド:**
    - username: ユーザー名
    - email: メールアドレス
    - contact_number: 連絡先電話番号
    - date_of_birth: 生年月日

    **注意事項:**
    - メールアドレス変更時は新しいトークンが発行されます
    - パスワード変更は別エンドポイントで行ってください
    - 更新時刻は自動的に日本時間で記録されます
    """,
)
async def update_user_profile(user_update: UserUpdate, request: Request, response: Response, db: AsyncSession = Depends(get_db)):
    logger.info("update_user_profile - start")
    try:
        # 現在のユーザーを取得
        current_user = await get_current_user(request, db)

        # ユーザー情報を更新
        updated_user = await update_user_with_schema(db, current_user, user_update)
        logger.info("update_user_profile - user_updated", user_id=updated_user.user_id)

        # 新しい認証トークンを生成（更新されたユーザー情報で）
        client_host = request.headers.get("X-Forwarded-For") or (request.client.host if request.client else "unknown")
        access_token = create_access_token(data={"sub": updated_user.email, "client_ip": client_host})
        logger.info("update_user_profile - token_created")

        # HttpOnlyクッキーとして新しいトークンを設定
        response.set_cookie(
            key="authToken",
            value=access_token,
            httponly=True,  # JavaScriptからアクセスできないようにする
            max_age=60 * 60 * 3,  # クッキーの有効期限（秒）　3時間
            secure=True,  # HTTPSのみで送信
            samesite="lax",  # クロスサイトリクエストに対する制御
        )
        logger.info("update_user_profile - success", user_id=updated_user.user_id)

        user_data = UserResponse.model_validate(updated_user)
        return create_success_response(message="ユーザー情報が正常に更新され、新しい認証トークンが発行されました", data=user_data.model_dump())
    finally:
        logger.info("update_user_profile - end")


@router.delete(
    "/me",
    response_model=SuccessResponse[MessageResponse],
    summary="ユーザーアカウント削除",
    description="""現在ログイン中のユーザーアカウントを削除します。

    **処理の流れ:**
    1. get_current_user()で現在のユーザーを取得・認証
    2. delete_user()で論理削除を実行
    3. ユーザーステータスを「停止中」に変更
    4. deleted_at フィールドに削除日時を記録
    5. 認証クッキーを削除してログアウト処理
    6. 削除完了メッセージを返却

    **論理削除の詳細:**
    - 物理削除は行わず、データベースレコードは保持
    - user_status を STATUS_SUSPENDED に変更
    - deleted_at に削除日時を記録（日本時間）
    - 削除されたユーザーは検索対象から除外

    **認証必須:** JWTトークンが必要です。

    **削除方式:**
    - 論理削除（ソフトデリート）を採用
    - データは実際には残るが、非アクティブ状態に変更
    - アカウントは完全に無効化され、今後ログインできなくなります

    **注意事項:**
    - この操作は元に戻せません
    - 削除実行後は自動的にログアウトされます
    - 同じメールアドレスでの再登録が必要な場合は、新規登録を行ってください
    """,
)
async def delete_user_account(request: Request, response: Response, db: AsyncSession = Depends(get_db)):
    logger.info("delete_user_account - start")
    try:
        # 現在のユーザーを取得
        current_user = await get_current_user(request, db)

        # ユーザーを論理削除
        await delete_user(db, current_user)
        logger.info("delete_user_account - user_deleted", user_id=current_user.user_id)

        # 認証クッキーを削除（ログアウト処理）
        response.delete_cookie(key="authToken", httponly=True, secure=True, samesite="lax")
        logger.info("delete_user_account - success", user_id=current_user.user_id)

        return create_success_response(message="ユーザーアカウントが正常に削除され、ログアウトしました", data={"message": "ユーザーアカウントが正常に削除されました"})
    finally:
        logger.info("delete_user_account - end")
