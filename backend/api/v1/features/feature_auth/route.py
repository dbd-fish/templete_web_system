
import urllib.parse

import structlog
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.common.database import get_db
from api.common.response_schemas import MessageResponse, SuccessResponse, create_message_response, create_success_response
from api.common.setting import setting
from api.v1.features.feature_auth.crud import (
    change_user_password,
    create_user_service,
    decode_password_reset_token,
    delete_user,
    delete_user_by_admin,
    get_all_users_for_admin,
    get_current_user,
    get_profile_info,
    get_user_by_id_for_admin,
    reset_password,
    reset_password_email,
    restore_deleted_user_by_admin,
    temporary_create_user,
    update_advanced_user_profile,
    update_user_by_admin,
    update_user_with_schema,
    verify_email_token,
)
from api.v1.features.feature_auth.google_oauth import generate_username_from_google_info, verify_google_id_token
from api.v1.features.feature_auth.models.user import User

from api.v1.features.feature_auth.schemas.user import (
    AdminUserListResponse,
    AdminUserResponse,
    AdminUserUpdateRequest,
    AdvancedUserUpdate,
    DirectUserCreate,
    GoogleLoginRequest,
    PasswordChangeRequest,
    PasswordResetData,
    ProfileResponse,
    SendPasswordResetEmailData,
    TokenData,
    TokenPairResponse,
    UserCreate,
    UserResponse,
    UserUpdate,
)
from api.v1.features.feature_auth.security import authenticate_user, create_access_token, create_token_pair, require_admin_role, validate_refresh_token

# ログの設定
logger = structlog.get_logger()

router = APIRouter()



@router.post(
    "/login",
    response_model=SuccessResponse[MessageResponse],
    summary="ユーザーログイン",
    description="""ユーザー名（またはメールアドレス）とパスワードでログインします。

    **処理の流れ:**
    1. JSONまたはフォームデータ（username/password）を受信
    2. authenticate_user()でユーザー認証を実行
    3. 認証成功時、JWTアクセストークンを生成
    4. HttpOnlyクッキーとしてトークンを設定
    5. セキュアなクッキー設定（3時間の有効期限）

    **テスト用アカウント:**
    - メールアドレス: `testuser@example.com`
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
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "username": {"type": "string", "title": "Username", "description": "ユーザー名またはメールアドレス", "default": "testuser@example.com", "example": "testuser@example.com"},
                            "password": {"type": "string", "title": "Password", "description": "パスワード", "default": "Password123456+-", "example": "Password123456+-"},
                        },
                        "required": ["username", "password"],
                    },
                },
                "application/x-www-form-urlencoded": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "username": {"type": "string", "title": "Username", "description": "ユーザー名またはメールアドレス", "default": "testuser@example.com", "example": "testuser@example.com"},
                            "password": {"type": "string", "title": "Password", "description": "パスワード", "default": "Password123456+-", "example": "Password123456+-"},
                        },
                        "required": ["username", "password"],
                    },
                },
            },
        },
    },
)
async def login(request: Request, response: Response, db: AsyncSession = Depends(get_db)):
    # Content-Typeに基づいてリクエストボディを解析
    content_type = request.headers.get("content-type", "")
    body = await request.body()
    body_str = body.decode('utf-8')

    username = ""
    password = ""

    if "application/json" in content_type:
        # JSONリクエストの場合
        import json
        try:
            json_data = json.loads(body_str)
            username = json_data.get("email", "")
            password = json_data.get("password", "")
        except json.JSONDecodeError as e:
            logger.error("login - invalid JSON format")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="無効なJSON形式です",
            ) from e
    else:
        # フォームデータの場合（デフォルト）
        def parse_form_data(data: str) -> dict[str, str]:
            params = {}
            for pair in data.split('&'):
                if '=' in pair:
                    key, value = pair.split('=', 1)
                    # URL デコード（ただし + を空白に変換しない）
                    key = urllib.parse.unquote(key)
                    value = urllib.parse.unquote(value)
                    params[key] = value
            return params

        form_params = parse_form_data(body_str)
        username = form_params.get("username", "")
        password = form_params.get("password", "")

    logger.info("login - start", username=username)
    logger.info("login - form_data received", username=username, password_length=len(password))
    try:
        user = await authenticate_user(username, password, db)
        if not user:
            logger.info("login - authentication failed", username=username)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token, refresh_token = create_token_pair(user.email)  # JWTトークンペアを生成
        logger.info("login - success", user_id=user.user_id)

        # HttpOnlyクッキーとしてアクセストークンを設定
        response.set_cookie(
            key="authToken",
            value=access_token,
            httponly=True,  # JavaScriptからアクセスできないようにする
            max_age=setting.ACCESS_TOKEN_COOKIE_MAX_AGE,  # JWTより若干長い期限で整合性確保
            secure=not setting.DEV_MODE,  # 開発環境ではHTTPを許可、本番環境ではHTTPSのみ
            samesite="lax",  # クロスサイトリクエストに対する制御
        )

        # HttpOnlyクッキーとしてリフレッシュトークンを設定
        response.set_cookie(
            key="refreshToken",
            value=refresh_token,
            httponly=True,  # JavaScriptからアクセスできないようにする
            max_age=setting.REFRESH_TOKEN_COOKIE_MAX_AGE,  # リフレッシュトークンCookie期限
            secure=not setting.DEV_MODE,  # 開発環境ではHTTPを許可、本番環境ではHTTPSのみ
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
    summary="ユーザー直接登録",
    description="""新しいユーザーを直接登録するエンドポイントです。

    **処理の流れ:**
    1. DirectUserCreateスキーマでユーザー情報を受信
    2. パスワードとパスワード確認の一致をチェック
    3. create_user_service()でユーザー登録処理を実行：
       - 論理削除済みユーザーが存在する場合：復活処理を実行
       - アクティブユーザーが存在する場合：409エラーを返す
       - 新規の場合：新しいユーザーを作成
    4. パスワードはbcryptでハッシュ化して保存
    5. 作成または復活されたユーザー情報をUserResponseスキーマで返却

    **パラメータ:**
    - user_data: 新規ユーザーの情報（email, username, password, password_confirm）
    - db: 非同期データベースセッション

    **レスポンス:**
    - SuccessResponse[UserResponse]: 登録成功メッセージと新規ユーザー情報
    - 400エラー: バリデーションエラー（パスワード不一致等）
    - 409エラー: アクティブなユーザーが既に存在する場合
    """,
)
async def register_user_direct(user_data: DirectUserCreate, db: AsyncSession = Depends(get_db)):
    logger.info("register_user_direct - start", email=user_data.email, username=user_data.username)
    try:
        # 直接ユーザー登録処理
        new_user = await create_user_service(user_data.email, user_data.username, user_data.password, db)
        logger.info("register_user_direct - success", user_id=new_user.user_id)
        user_response = UserResponse.model_validate(new_user)
        return create_success_response(message="ユーザー登録が完了しました", data=user_response.model_dump())
    finally:
        logger.info("register_user_direct - end")


@router.post(
    "/signup-with-email",
    response_model=SuccessResponse[UserResponse],
    summary="ユーザー本登録（メール認証）",
    description="""メール認証を経た新しいユーザーを登録するエンドポイントです。

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
async def register_user_with_email(tokenData: TokenData, db: AsyncSession = Depends(get_db)):
    logger.info("register_user_with_email - start")
    try:
        # tokenからuser情報を取得
        user_info = await verify_email_token(tokenData.token)
        logger.info("register_user_with_email - user_info", user_info=user_info)
        # トークンから取得したユーザー情報でユーザー登録
        new_user = await create_user_service(user_info.email, user_info.username, user_info.password, db)
        logger.info("register_user_with_email - success", user_id=new_user.user_id)
        user_data = UserResponse.model_validate(new_user)
        return create_success_response(message="ユーザー登録が完了しました", data=user_data.model_dump())
    finally:
        logger.info("register_user_with_email - end")


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
    1. リフレッシュトークンを無効化（存在する場合）
    2. 認証クッキー（authToken/refreshToken）をセキュアな設定で削除
    3. ログアウト成功メッセージを返却

    **認証不要設計:**
    - 無効なトークンやクッキーなしでもログアウト処理を実行
    - フロントエンド側の状態リセットを確実に支援

    **クッキー削除設定:**
    - HttpOnly: JavaScriptからアクセス不可
    - Secure: HTTPS通信でのみ有効（本番環境）
    - SameSite=Lax: CSRF攻撃防止

    **パラメータ:**
    - request: リクエストオブジェクト（クッキー取得用）
    - response: レスポンスオブジェクト（クッキー削除用）

    **レスポンス:**
    - SuccessResponse[MessageResponse]: ログアウト成功メッセージ
    """,
)
async def logout(request: Request, response: Response):
    logger.info("logout - start")
    try:
        # 認証クッキーを削除してログアウト処理
        response.delete_cookie(key="authToken", httponly=True, secure=not setting.DEV_MODE, samesite="lax")
        response.delete_cookie(key="refreshToken", httponly=True, secure=not setting.DEV_MODE, samesite="lax")
        logger.info("logout - success")
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


        # 新しい認証トークンペアを生成（更新されたユーザー情報で）
        access_token, refresh_token = create_token_pair(updated_user.email)  # client_ipパラメータ削除
        logger.info("update_user_profile - token_created")

        # HttpOnlyクッキーとして新しいアクセストークンを設定
        response.set_cookie(
            key="authToken",
            value=access_token,
            httponly=True,  # JavaScriptからアクセスできないようにする
            max_age=setting.ACCESS_TOKEN_COOKIE_MAX_AGE,  # JWTより若干長い期限で整合性確保
            secure=not setting.DEV_MODE,  # 開発環境ではHTTPを許可、本番環境ではHTTPSのみ
            samesite="lax",  # クロスサイトリクエストに対する制御
        )

        # HttpOnlyクッキーとして新しいリフレッシュトークンを設定
        response.set_cookie(
            key="refreshToken",
            value=refresh_token,
            httponly=True,  # JavaScriptからアクセスできないようにする
            max_age=setting.REFRESH_TOKEN_COOKIE_MAX_AGE,  # リフレッシュトークンCookie期限
            secure=not setting.DEV_MODE,  # 開発環境ではHTTPを許可、本番環境ではHTTPSのみ
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
        response.delete_cookie(key="authToken", httponly=True, secure=not setting.DEV_MODE, samesite="lax")
        response.delete_cookie(key="refreshToken", httponly=True, secure=not setting.DEV_MODE, samesite="lax")
        logger.info("delete_user_account - success", user_id=current_user.user_id)

        return create_success_response(message="ユーザーアカウントが正常に削除され、ログアウトしました", data={"message": "ユーザーアカウントが正常に削除されました"})
    finally:
        logger.info("delete_user_account - end")


@router.delete(
    "/account",
    response_model=SuccessResponse[MessageResponse],
    summary="アカウント削除",
    description="""現在ログイン中のユーザーアカウントを削除します。

    **処理の流れ:**
    1. get_current_user()で現在のユーザーを取得・認証
    2. delete_user()で論理削除を実行
    3. ユーザーステータスを「停止中」に変更
    4. deleted_at フィールドに削除日時を記録
    5. 全てのリフレッシュトークンを無効化
    6. 認証クッキーを削除してログアウト処理
    7. 削除完了メッセージを返却

    **論理削除の詳細:**
    - 物理削除は行わず、データベースレコードは保持
    - user_status を STATUS_SUSPENDED に変更
    - deleted_at に削除日時を記録（日本時間）
    - 削除されたユーザーは検索対象から除外

    **認証必須:** JWTトークンが必要です。

    **セキュリティ機能:**
    - 本人認証確認（ログイン中のユーザーのみ削除可能）
    - 全セッション無効化（リフレッシュトークン削除）
    - 即座ログアウト処理

    **削除方式:**
    - 論理削除（ソフトデリート）を採用
    - データは実際には残るが、非アクティブ状態に変更
    - アカウントは完全に無効化され、今後ログインできなくなります

    **注意事項:**
    - この操作は元に戻せません
    - 削除実行後は自動的にログアウトされます
    - 同じメールアドレスでの再登録が必要な場合は、新規登録を行ってください

    **パラメータ:**
    - request: リクエストオブジェクト（認証トークン取得用）
    - response: レスポンスオブジェクト（クッキー削除用）
    - db: 非同期データベースセッション

    **レスポンス:**
    - SuccessResponse[MessageResponse]: 削除完了メッセージ
    - 401エラー: 未認証状態でのアクセス時
    """,
)
async def delete_account(request: Request, response: Response, db: AsyncSession = Depends(get_db)):
    logger.info("delete_account - start")
    try:
        # 現在のユーザーを取得
        current_user = await get_current_user(request, db)

        # ユーザーを論理削除
        await delete_user(db, current_user)
        logger.info("delete_account - user_deleted", user_id=current_user.user_id)


        # 認証クッキーを削除（ログアウト処理）
        response.delete_cookie(key="authToken", httponly=True, secure=not setting.DEV_MODE, samesite="lax")
        response.delete_cookie(key="refreshToken", httponly=True, secure=not setting.DEV_MODE, samesite="lax")
        logger.info("delete_account - success", user_id=current_user.user_id)

        return create_success_response(message="アカウントが正常に削除され、ログアウトしました", data={"message": "アカウントが正常に削除されました"})
    finally:
        logger.info("delete_account - end")


@router.delete(
    "/user",
    response_model=SuccessResponse[MessageResponse],
    summary="ユーザーアカウント削除（別パス）",
    description="""現在ログイン中のユーザーアカウントを削除します。

    **処理の流れ:**
    1. get_current_user()で現在のユーザーを取得・認証
    2. delete_user()で論理削除を実行
    3. ユーザーステータスを「停止中」に変更
    4. deleted_at フィールドに削除日時を記録
    5. 全てのリフレッシュトークンを無効化
    6. 認証クッキーを削除してログアウト処理
    7. 削除完了メッセージを返却

    **論理削除の詳細:**
    - 物理削除は行わず、データベースレコードは保持
    - user_status を STATUS_SUSPENDED に変更
    - deleted_at に削除日時を記録（日本時間）
    - 削除されたユーザーは検索対象から除外

    **認証必須:** JWTトークンが必要です。

    **セキュリティ機能:**
    - 本人認証確認（ログイン中のユーザーのみ削除可能）
    - 全セッション無効化（リフレッシュトークン削除）
    - 即座ログアウト処理

    **削除方式:**
    - 論理削除（ソフトデリート）を採用
    - データは実際には残るが、非アクティブ状態に変更
    - アカウントは完全に無効化され、今後ログインできなくなります

    **注意事項:**
    - この操作は元に戻せません
    - 削除実行後は自動的にログアウトされます
    - 同じメールアドレスでの再登録が必要な場合は、新規登録を行ってください

    **パラメータ:**
    - request: リクエストオブジェクト（認証トークン取得用）
    - response: レスポンスオブジェクト（クッキー削除用）
    - db: 非同期データベースセッション

    **レスポンス:**
    - SuccessResponse[MessageResponse]: 削除完了メッセージ
    - 401エラー: 未認証状態でのアクセス時
    """,
)
async def delete_user_account_alt(request: Request, response: Response, db: AsyncSession = Depends(get_db)):
    logger.info("delete_user_account_alt - start")
    try:
        # 現在のユーザーを取得
        current_user = await get_current_user(request, db)

        # ユーザーを論理削除
        await delete_user(db, current_user)
        logger.info("delete_user_account_alt - user_deleted", user_id=current_user.user_id)


        # 認証クッキーを削除（ログアウト処理）
        response.delete_cookie(key="authToken", httponly=True, secure=not setting.DEV_MODE, samesite="lax")
        response.delete_cookie(key="refreshToken", httponly=True, secure=not setting.DEV_MODE, samesite="lax")
        logger.info("delete_user_account_alt - success", user_id=current_user.user_id)

        return create_success_response(message="ユーザーアカウントが正常に削除され、ログアウトしました", data={"message": "ユーザーアカウントが正常に削除されました"})
    finally:
        logger.info("delete_user_account_alt - end")


@router.post(
    "/refresh",
    response_model=SuccessResponse[TokenPairResponse],
    summary="アクセストークン更新",
    description="""リフレッシュトークンを使用してアクセストークンを更新します。

    **処理の流れ:**
    1. クッキーからリフレッシュトークンを取得
    2. validate_refresh_token()でリフレッシュトークンを検証
    3. 新しいアクセストークンのみを生成
    4. 新しいアクセストークンをHttpOnlyクッキーに設定
    5. 既存のリフレッシュトークンと新しいアクセストークンを返却

    **セキュリティ:**
    - リフレッシュトークンは更新せず、有効期限延長を防止
    - アクセストークンのみ新規生成（30分有効）
    - リフレッシュトークンの元の有効期限（5日）を維持

    **レスポンス:**
    - SuccessResponse[TokenPairResponse]: 新しいトークンペア情報
    - 401エラー: 無効または期限切れのリフレッシュトークン
    """,
)
async def refresh_token(request: Request, response: Response, db: AsyncSession = Depends(get_db)):
    logger.info("refresh_token - start")

    try:
        # クッキーからリフレッシュトークンを取得
        refresh_token = request.cookies.get("refreshToken")
        logger.info("refresh_token - received token from cookie", token_present=bool(refresh_token))

        if not refresh_token:
            logger.error("refresh_token - no refresh token in cookies")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="リフレッシュトークンが見つかりません",
            )

        # JWTリフレッシュトークンを検証してユーザーメールを取得
        logger.info("refresh_token - starting JWT validate_refresh_token call")
        user_email = validate_refresh_token(refresh_token)
        logger.info("refresh_token - JWT validate_refresh_token success", user_email=user_email)
        logger.info("refresh_token - JWT refresh token validated", user_email=user_email)

        # セキュリティ向上: リフレッシュトークンは更新せず、アクセストークンのみ生成
        # これにより、リフレッシュトークンの有効期限が延長されることを防ぐ
        access_token = create_access_token(user_email)
        logger.info("refresh_token - new access token created")

        # 新しいCookie設定

        # HttpOnlyクッキーとして新しいアクセストークンを設定
        response.set_cookie(
            key="authToken",
            value=access_token,
            httponly=True,
            max_age=setting.ACCESS_TOKEN_COOKIE_MAX_AGE,  # JWTより若干長い期限で整合性確保
            secure=not setting.DEV_MODE,  # 開発環境では False (HTTP許可)
            samesite="lax",
        )


        logger.info("refresh_token - success", user_email=user_email)

        # レスポンスデータを作成（既存のリフレッシュトークンを返す）
        token_pair_data = TokenPairResponse(
            access_token=access_token,
            refresh_token=refresh_token,  # 既存のリフレッシュトークンをそのまま返す
            token_type="bearer",
            expires_in=1800,  # 30分 = 1800秒
        )

        return create_success_response(message="トークンが正常に更新されました", data=token_pair_data.model_dump())
    finally:
        logger.info("refresh_token - end")


@router.post(
    "/google-login",
    response_model=SuccessResponse[MessageResponse],
    summary="Google認証ログイン",
    description="""GoogleのIDトークンを使用してログインします。

    **処理の流れ:**
    1. GoogleログインリクエストからIDトークンを受信
    2. verify_google_id_token()でGoogleIDトークンを検証
    3. IDトークンからユーザー情報（email, name等）を抽出
    4. 既存ユーザーの場合：ログイン処理を実行
    5. 新規ユーザーの場合：自動登録後ログイン処理を実行
    6. JWTアクセストークンとリフレッシュトークンを生成
    7. HttpOnlyクッキーとしてトークンを設定

    **Google認証フロー:**
    1. フロントエンドでGoogle認証を実行
    2. GoogleからIDトークンを取得
    3. このエンドポイントにIDトークンを送信
    4. サーバー側でIDトークンを検証・ユーザー作成/ログイン

    **セキュリティ:**
    - GoogleのIDトークンを厳密に検証
    - issuer、audience、email_verifiedを確認
    - HttpOnlyクッキーでXSS攻撃を防止
    - Secure属性でHTTPS通信を強制
    - SameSite=Lax設定でCSRF攻撃を軽減

    **新規ユーザー自動登録:**
    - Googleアカウントのメールアドレスとユーザー名を使用
    - デフォルトでFREEロールとACTIVEステータスを設定
    - パスワードは設定せず（Google認証のみ）

    **パラメータ:**
    - google_request: Googleログインリクエストデータ（IDトークン）
    - request: リクエストオブジェクト（クライアントIP取得用）
    - response: レスポンスオブジェクト（クッキー設定用）
    - db: 非同期データベースセッション

    **レスポンス:**
    - SuccessResponse[MessageResponse]: ログイン成功メッセージ
    - 400エラー: 無効なIDトークン
    - 401エラー: 認証失敗（メール未認証等）
    - 500エラー: サーバー内部エラー
    """,
)
async def google_login(google_request: GoogleLoginRequest, request: Request, response: Response, db: AsyncSession = Depends(get_db)):
    logger.info("google_login - start")
    try:
        # GoogleのIDトークンを検証してユーザー情報を取得
        google_user_info = await verify_google_id_token(google_request.id_token)
        logger.info("google_login - google_token_verified", email=google_user_info.email, name=google_user_info.name)

        # データベースで既存ユーザーを検索
        from api.v1.features.feature_auth.crud import get_user_by_email

        existing_user = await get_user_by_email(db, google_user_info.email)

        if existing_user:
            # 既存ユーザーの場合：ログイン処理
            if existing_user.user_status != User.STATUS_ACTIVE:
                logger.warning("google_login - inactive_user", email=google_user_info.email, status=existing_user.user_status)
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="アカウントが無効化されています",
                )

            user = existing_user
            logger.info("google_login - existing_user_login", user_id=user.user_id, email=user.email)
        else:
            # 新規ユーザーの場合：自動登録
            logger.info("google_login - creating_new_user", email=google_user_info.email)

            # Googleユーザー情報からユーザー名を生成
            generated_username = generate_username_from_google_info(google_user_info)

            # 新規ユーザーを作成
            from api.v1.features.feature_auth.crud import create_google_user

            user = await create_google_user(
                db=db,
                email=google_user_info.email,
                username=generated_username,
                google_sub=google_user_info.sub,
                full_name=google_user_info.name,
            )
            logger.info("google_login - new_user_created", user_id=user.user_id, email=user.email)

        # JWTトークンペアを生成
        access_token, refresh_token = create_token_pair(user.email)
        logger.info("google_login - token_pair_created", user_id=user.user_id)

        # HttpOnlyクッキーとしてアクセストークンを設定
        response.set_cookie(
            key="authToken",
            value=access_token,
            httponly=True,  # JavaScriptからアクセスできないようにする
            max_age=setting.ACCESS_TOKEN_COOKIE_MAX_AGE,  # JWTより若干長い期限で整合性確保
            secure=not setting.DEV_MODE,  # 開発環境ではHTTPを許可、本番環境ではHTTPSのみ
            samesite="lax",  # クロスサイトリクエストに対する制御
        )

        # HttpOnlyクッキーとしてリフレッシュトークンを設定
        response.set_cookie(
            key="refreshToken",
            value=refresh_token,
            httponly=True,  # JavaScriptからアクセスできないようにする
            max_age=setting.REFRESH_TOKEN_COOKIE_MAX_AGE,  # リフレッシュトークンCookie期限
            secure=not setting.DEV_MODE,  # 開発環境ではHTTPを許可、本番環境ではHTTPSのみ
            samesite="lax",  # クロスサイトリクエストに対する制御
        )

        logger.info("google_login - success", user_id=user.user_id, email=user.email)
        return create_message_response(message="Googleログインに成功しました")

    except ValueError as e:
        logger.error("google_login - validation_error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"認証エラー: {str(e)}",
        ) from e
    finally:
        logger.info("google_login - end")


@router.post(
    "/change-password",
    response_model=SuccessResponse[MessageResponse],
    summary="パスワード変更",
    description="""現在ログイン中のユーザーのパスワードを変更します。

    **処理の流れ:**
    1. get_current_user()で現在のユーザーを取得・認証
    2. PasswordChangeRequestスキーマでパスワード変更データを受信
    3. change_user_password()でパスワード変更処理を実行
    4. 現在のパスワードを検証
    5. 新しいパスワードをbcryptでハッシュ化して更新
    6. 全てのリフレッシュトークンを無効化（セキュリティ強化）

    **セキュリティ機能:**
    - 現在のパスワードの厳密な検証
    - 新しいパスワードの複雑性チェック
    - Googleユーザーは変更不可（エラー返却）
    - パスワード変更後のセッション無効化

    **認証必須:** JWTトークンが必要です。

    **制限事項:**
    - Googleアカウントでログインしたユーザーは使用不可
    - メール認証ユーザーのみ対象

    **パラメータ:**
    - password_data: 現在のパスワードと新しいパスワード
    - request: リクエストオブジェクト（認証用）
    - db: 非同期データベースセッション

    **レスポンス:**
    - SuccessResponse[MessageResponse]: パスワード変更成功メッセージ
    - 400エラー: 現在のパスワードが間違っている場合、Googleユーザーの場合
    - 401エラー: 未認証状態でのアクセス時
    """,
)
async def change_password(password_data: PasswordChangeRequest, request: Request, db: AsyncSession = Depends(get_db)):
    logger.info("change_password - start")
    try:
        # 現在のユーザーを取得
        current_user = await get_current_user(request, db)

        # パスワード変更処理
        await change_user_password(db, current_user, password_data.current_password, password_data.new_password)
        logger.info("change_password - password_changed", user_id=current_user.user_id)

        logger.info("change_password - jwt_stateless_design", user_id=current_user.user_id)

        logger.info("change_password - success", user_id=current_user.user_id)
        return create_message_response(message="パスワードが正常に変更されました。セキュリティのため再ログインしてください。")

    finally:
        logger.info("change_password - end")


@router.get(
    "/profile",
    response_model=SuccessResponse[ProfileResponse],
    summary="詳細プロフィール取得",
    description="""現在ログインしているユーザーの詳細プロフィール情報を取得します。

    **処理の流れ:**
    1. get_current_user()で現在のユーザーを取得・認証
    2. get_profile_info()でプロフィール情報を取得
    3. ProfileResponseスキーマに変換
    4. 成功レスポンスとして返却

    **プロフィール情報:**
    - 基本情報: email, username, contact_number, date_of_birth
    - アカウント情報: user_role, user_status, created_at, updated_at
    - 認証タイプ: is_google_user（Googleアカウントか否か）
    - プロフィール画像: profile_image_url（将来実装予定）

    **Google/メール認証統合:**
    - Googleユーザー: is_google_user = true, hashed_password = 空
    - メールユーザー: is_google_user = false, hashed_password = 有

    **認証必須:** JWTトークンが必要です。

    **パラメータ:**
    - request: リクエストオブジェクト（認証用）
    - db: 非同期データベースセッション

    **レスポンス:**
    - SuccessResponse[ProfileResponse]: 詳細プロフィール情報
    - 401エラー: 未認証状態でのアクセス時
    """,
)
async def get_user_profile(request: Request, db: AsyncSession = Depends(get_db)):
    logger.info("get_user_profile - start")
    try:
        # 現在のユーザーを取得
        current_user = await get_current_user(request, db)

        # プロフィール情報を取得
        profile_data = await get_profile_info(current_user)
        logger.info("get_user_profile - profile_retrieved", user_id=current_user.user_id)

        # ProfileResponseスキーマに変換
        profile_response = ProfileResponse.model_validate(profile_data)

        logger.info("get_user_profile - success", user_id=current_user.user_id)
        return create_success_response(message="プロフィール情報を取得しました", data=profile_response.model_dump())

    finally:
        logger.info("get_user_profile - end")


@router.patch(
    "/profile",
    response_model=SuccessResponse[ProfileResponse],
    summary="高度なプロフィール更新",
    description="""現在ログイン中のユーザーの詳細プロフィール情報を更新します。

    **処理の流れ:**
    1. get_current_user()で現在のユーザーを取得・認証
    2. AdvancedUserUpdateスキーマで更新データを受信
    3. update_advanced_user_profile()でプロフィール情報を更新
    4. メールアドレス・ユーザー名の重複チェック
    5. 更新されたプロフィール情報で新しいJWTトークンを生成
    6. 新しいトークンをHttpOnlyクッキーに設定

    **更新可能なフィールド:**
    - email: メールアドレス（重複チェック有）
    - username: ユーザー名（重複チェック有）
    - contact_number: 連絡先電話番号
    - date_of_birth: 生年月日
    - profile_image_url: プロフィール画像URL（将来実装予定）

    **セキュリティ機能:**
    - メールアドレス・ユーザー名の重複検証
    - URL形式の検証（profile_image_url）
    - 電話番号形式の検証
    - トークン自動更新（メールアドレス変更時）

    **認証必須:** JWTトークンが必要です。

    **パラメータ:**
    - profile_update: 更新するプロフィールデータ
    - request: リクエストオブジェクト（認証・IP取得用）
    - response: レスポンスオブジェクト（クッキー設定用）
    - db: 非同期データベースセッション

    **レスポンス:**
    - SuccessResponse[ProfileResponse]: 更新されたプロフィール情報
    - 409エラー: メールアドレス・ユーザー名が既に使用されている場合
    - 401エラー: 未認証状態でのアクセス時
    """,
)
async def update_user_profile_advanced(profile_update: AdvancedUserUpdate, request: Request, response: Response, db: AsyncSession = Depends(get_db)):
    logger.info("update_user_profile_advanced - start")
    try:
        # 現在のユーザーを取得
        current_user = await get_current_user(request, db)

        # プロフィール情報を更新
        updated_user = await update_advanced_user_profile(db, current_user, profile_update)
        logger.info("update_user_profile_advanced - profile_updated", user_id=updated_user.user_id)


        # 新しい認証トークンペアを生成（更新されたユーザー情報で）
        access_token, refresh_token = create_token_pair(updated_user.email)  # client_ipパラメータ削除
        logger.info("update_user_profile_advanced - token_created")

        # HttpOnlyクッキーとして新しいアクセストークンを設定
        response.set_cookie(
            key="authToken",
            value=access_token,
            httponly=True,
            max_age=setting.ACCESS_TOKEN_COOKIE_MAX_AGE,  # JWTより若干長い期限で整合性確保
            secure=not setting.DEV_MODE,
            samesite="lax",
        )

        # HttpOnlyクッキーとして新しいリフレッシュトークンを設定
        response.set_cookie(
            key="refreshToken",
            value=refresh_token,
            httponly=True,
            max_age=setting.REFRESH_TOKEN_COOKIE_MAX_AGE,  # リフレッシュトークンCookie期限
            secure=not setting.DEV_MODE,
            samesite="lax",
        )

        # プロフィール情報を取得してレスポンス作成
        profile_data = await get_profile_info(updated_user)
        profile_response = ProfileResponse.model_validate(profile_data)

        logger.info("update_user_profile_advanced - success", user_id=updated_user.user_id)
        return create_success_response(message="プロフィール情報が正常に更新され、新しい認証トークンが発行されました", data=profile_response.model_dump())

    finally:
        logger.info("update_user_profile_advanced - end")







# ============================================================================
# 管理者専用エンドポイント
# ============================================================================

@router.get(
    "/admin/users",
    response_model=SuccessResponse[AdminUserListResponse],
    summary="管理者用: ユーザー一覧取得",
    description="""管理者権限を持つユーザーが全ユーザー一覧を取得します。

    **処理の流れ:**
    1. get_current_user()で現在のユーザーを取得・認証
    2. require_admin_role()で管理者権限をチェック
    3. get_all_users_for_admin()でユーザー一覧を取得（ページネーション対応）
    4. AdminUserListResponseスキーマに変換
    5. 成功レスポンスとして返却

    **権限要件:**
    - 管理者権限（ROLE_ADMIN以上）が必要

    **ページネーション:**
    - page: ページ番号（1から開始、デフォルト: 1）
    - page_size: 1ページあたりの件数（デフォルト: 20、最大: 100）
    - include_deleted: 削除済みユーザーを含むか（デフォルト: false）

    **レスポンス:**
    - SuccessResponse[AdminUserListResponse]: ユーザー一覧情報
    - 403エラー: 管理者権限がない場合
    - 401エラー: 未認証状態でのアクセス時
    """,
)
async def get_users_for_admin(
    request: Request,
    page: int = 1,
    page_size: int = 20,
    include_deleted: bool = False,
    db: AsyncSession = Depends(get_db),
):
    logger.info("get_users_for_admin - start", page=page, page_size=page_size, include_deleted=include_deleted)
    try:
        # 現在のユーザーを取得・認証
        current_user = await get_current_user(request, db)

        # 管理者権限をチェック
        require_admin_role(current_user)

        # ページサイズの制限
        if page_size > 100:
            page_size = 100
        if page_size < 1:
            page_size = 20

        if page < 1:
            page = 1

        # ユーザー一覧を取得
        users, total_count = await get_all_users_for_admin(db, page, page_size, include_deleted)
        logger.info("get_users_for_admin - users_retrieved", user_count=len(users), total_count=total_count)

        # レスポンスデータを作成
        admin_user_responses = []
        for user in users:
            admin_user_response = AdminUserResponse(
                user_id=str(user.user_id),
                email=user.email,
                username=user.username,
                contact_number=user.contact_number,
                date_of_birth=user.date_of_birth,
                user_role=user.user_role,
                user_status=user.user_status,
                created_at=user.created_at,
                updated_at=user.updated_at,
                deleted_at=user.deleted_at,
            )
            admin_user_responses.append(admin_user_response)

        user_list_response = AdminUserListResponse(
            total_count=total_count,
            page=page,
            page_size=page_size,
            users=admin_user_responses,
        )

        logger.info("get_users_for_admin - success", total_count=total_count)
        return create_success_response(message="ユーザー一覧を取得しました", data=user_list_response.model_dump())

    finally:
        logger.info("get_users_for_admin - end")


@router.get(
    "/admin/users/{user_id}",
    response_model=SuccessResponse[AdminUserResponse],
    summary="管理者用: 特定ユーザー情報取得",
    description="""管理者権限を持つユーザーが特定のユーザー情報を取得します。

    **処理の流れ:**
    1. get_current_user()で現在のユーザーを取得・認証
    2. require_admin_role()で管理者権限をチェック
    3. get_user_by_id_for_admin()で対象ユーザーを取得
    4. AdminUserResponseスキーマに変換
    5. 成功レスポンスとして返却

    **権限要件:**
    - 管理者権限（ROLE_ADMIN以上）が必要

    **パラメータ:**
    - user_id: 取得するユーザーのID（UUID形式）

    **レスポンス:**
    - SuccessResponse[AdminUserResponse]: ユーザー情報
    - 403エラー: 管理者権限がない場合
    - 404エラー: ユーザーが見つからない場合
    - 401エラー: 未認証状態でのアクセス時
    """,
)
async def get_user_for_admin(request: Request, user_id: str, db: AsyncSession = Depends(get_db)):
    logger.info("get_user_for_admin - start", user_id=user_id)
    try:
        # 現在のユーザーを取得・認証
        current_user = await get_current_user(request, db)

        # 管理者権限をチェック
        require_admin_role(current_user)

        # 対象ユーザーを取得
        user = await get_user_by_id_for_admin(db, user_id)
        logger.info("get_user_for_admin - user_retrieved", target_user_id=user.user_id)

        # レスポンスデータを作成
        admin_user_response = AdminUserResponse(
            user_id=str(user.user_id),
            email=user.email,
            username=user.username,
            contact_number=user.contact_number,
            date_of_birth=user.date_of_birth,
            user_role=user.user_role,
            user_status=user.user_status,
            created_at=user.created_at,
            updated_at=user.updated_at,
            deleted_at=user.deleted_at,
        )

        logger.info("get_user_for_admin - success", target_user_id=user.user_id)
        return create_success_response(message="ユーザー情報を取得しました", data=admin_user_response.model_dump())

    finally:
        logger.info("get_user_for_admin - end")


@router.patch(
    "/admin/users/{user_id}",
    response_model=SuccessResponse[AdminUserResponse],
    summary="管理者用: ユーザー情報更新",
    description="""管理者権限を持つユーザーが特定のユーザー情報を更新します。

    **処理の流れ:**
    1. get_current_user()で現在のユーザーを取得・認証
    2. require_admin_role()で管理者権限をチェック
    3. update_user_by_admin()でユーザー情報を更新
    4. AdminUserResponseスキーマに変換
    5. 成功レスポンスとして返却

    **権限要件:**
    - 管理者権限（ROLE_ADMIN以上）が必要

    **更新可能なフィールド:**
    - email: メールアドレス（重複チェック有）
    - username: ユーザー名（重複チェック有）
    - user_role: ユーザー権限
    - user_status: アカウント状態
    - contact_number: 連絡先電話番号
    - date_of_birth: 生年月日

    **パラメータ:**
    - user_id: 更新するユーザーのID（UUID形式）
    - user_update: 更新データ

    **レスポンス:**
    - SuccessResponse[AdminUserResponse]: 更新されたユーザー情報
    - 403エラー: 管理者権限がない場合
    - 404エラー: ユーザーが見つからない場合
    - 409エラー: メールアドレス・ユーザー名が重複している場合
    - 401エラー: 未認証状態でのアクセス時
    """,
)
async def update_user_for_admin(
    request: Request,
    user_id: str,
    user_update: AdminUserUpdateRequest,
    db: AsyncSession = Depends(get_db),
):
    logger.info("update_user_for_admin - start", user_id=user_id)
    try:
        # 現在のユーザーを取得・認証
        current_user = await get_current_user(request, db)

        # 管理者権限をチェック
        require_admin_role(current_user)

        # ユーザー情報を更新
        updated_user = await update_user_by_admin(db, user_id, user_update)
        logger.info("update_user_for_admin - user_updated", target_user_id=updated_user.user_id)

        # レスポンスデータを作成
        admin_user_response = AdminUserResponse(
            user_id=str(updated_user.user_id),
            email=updated_user.email,
            username=updated_user.username,
            contact_number=updated_user.contact_number,
            date_of_birth=updated_user.date_of_birth,
            user_role=updated_user.user_role,
            user_status=updated_user.user_status,
            created_at=updated_user.created_at,
            updated_at=updated_user.updated_at,
            deleted_at=updated_user.deleted_at,
        )

        logger.info("update_user_for_admin - success", target_user_id=updated_user.user_id)
        return create_success_response(message="ユーザー情報を更新しました", data=admin_user_response.model_dump())

    finally:
        logger.info("update_user_for_admin - end")


@router.delete(
    "/admin/users/{user_id}",
    response_model=SuccessResponse[MessageResponse],
    summary="管理者用: ユーザー削除",
    description="""管理者権限を持つユーザーが特定のユーザーを削除します。

    **処理の流れ:**
    1. get_current_user()で現在のユーザーを取得・認証
    2. require_admin_role()で管理者権限をチェック
    3. delete_user_by_admin()でユーザーを削除（論理削除）
    4. 削除完了メッセージを返却

    **権限要件:**
    - 管理者権限（ROLE_ADMIN以上）が必要

    **削除方式:**
    - 論理削除（ソフトデリート）を実行
    - user_status を STATUS_SUSPENDED に変更
    - deleted_at に削除日時を記録

    **パラメータ:**
    - user_id: 削除するユーザーのID（UUID形式）

    **レスポンス:**
    - SuccessResponse[MessageResponse]: 削除完了メッセージ
    - 403エラー: 管理者権限がない場合
    - 404エラー: ユーザーが見つからない場合
    - 401エラー: 未認証状態でのアクセス時
    """,
)
async def delete_user_for_admin(request: Request, user_id: str, db: AsyncSession = Depends(get_db)):
    logger.info("delete_user_for_admin - start", user_id=user_id)
    try:
        # 現在のユーザーを取得・認証
        current_user = await get_current_user(request, db)

        # 管理者権限をチェック
        require_admin_role(current_user)

        # ユーザーを論理削除
        deleted_user = await delete_user_by_admin(db, user_id, permanent=False)
        logger.info("delete_user_for_admin - user_deleted", target_user_id=deleted_user.user_id)

        logger.info("delete_user_for_admin - success", target_user_id=deleted_user.user_id)
        return create_message_response(message="ユーザーを削除しました")

    finally:
        logger.info("delete_user_for_admin - end")


@router.post(
    "/admin/users/{user_id}/restore",
    response_model=SuccessResponse[AdminUserResponse],
    summary="管理者用: 削除ユーザー復活",
    description="""管理者権限を持つユーザーが論理削除されたユーザーを復活させます。

    **処理の流れ:**
    1. get_current_user()で現在のユーザーを取得・認証
    2. require_admin_role()で管理者権限をチェック
    3. restore_deleted_user_by_admin()でユーザーを復活
    4. AdminUserResponseスキーマに変換
    5. 成功レスポンスとして返却

    **権限要件:**
    - 管理者権限（ROLE_ADMIN以上）が必要

    **復活処理:**
    - user_status を STATUS_ACTIVE に変更
    - deleted_at を NULL に設定
    - メールアドレス重複チェック実行

    **パラメータ:**
    - user_id: 復活させるユーザーのID（UUID形式）

    **レスポンス:**
    - SuccessResponse[AdminUserResponse]: 復活されたユーザー情報
    - 403エラー: 管理者権限がない場合
    - 404エラー: ユーザーが見つからない場合
    - 400エラー: ユーザーが削除されていない場合
    - 409エラー: メールアドレスが重複している場合
    - 401エラー: 未認証状態でのアクセス時
    """,
)
async def restore_user_for_admin(request: Request, user_id: str, db: AsyncSession = Depends(get_db)):
    logger.info("restore_user_for_admin - start", user_id=user_id)
    try:
        # 現在のユーザーを取得・認証
        current_user = await get_current_user(request, db)

        # 管理者権限をチェック
        require_admin_role(current_user)

        # ユーザーを復活
        restored_user = await restore_deleted_user_by_admin(db, user_id)
        logger.info("restore_user_for_admin - user_restored", target_user_id=restored_user.user_id)

        # レスポンスデータを作成
        admin_user_response = AdminUserResponse(
            user_id=str(restored_user.user_id),
            email=restored_user.email,
            username=restored_user.username,
            contact_number=restored_user.contact_number,
            date_of_birth=restored_user.date_of_birth,
            user_role=restored_user.user_role,
            user_status=restored_user.user_status,
            created_at=restored_user.created_at,
            updated_at=restored_user.updated_at,
            deleted_at=restored_user.deleted_at,
        )

        logger.info("restore_user_for_admin - success", target_user_id=restored_user.user_id)
        return create_success_response(message="ユーザーを復活させました", data=admin_user_response.model_dump())

    finally:
        logger.info("restore_user_for_admin - end")
