from datetime import timedelta

import structlog
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from api.common.database import get_db
from api.common.response_schemas import ErrorCodes, SuccessResponse, create_error_response, create_success_response
from api.v1.features.feature_auth.crud import reset_password
from api.v1.features.feature_auth.security import create_access_token
from api.v1.features.feature_dev.seed_data import clear_data, seed_data

# ロガーの設定
logger = structlog.get_logger()

router = APIRouter()


@router.post(
    "/clear_data",
    response_model=dict,
    summary="全テーブルデータクリア",
    description="""【開発用】全テーブルのデータをクリアします。

    **注意:** このエンドポイントは開発環境専用です。

    **パラメータ:**
    - db: データベースセッション

    **レスポンス:**
    - dict: 成功メッセージ
    """,
)
async def clear_data_endpoint(
    db: AsyncSession = Depends(get_db),
):
    logger.info("clear_data_endpoint - start")
    try:
        await clear_data(db)
        logger.info("clear_data_endpoint - success")
        return {"msg": "clear_data API successfully"}
    finally:
        logger.info("clear_data_endpoint - end")


@router.post(
    "/seed_data",
    response_model=dict,
    summary="テストデータ投入",
    description="""【開発用】全テーブルにテスト用のシードデータを投入します。

    **注意:** このエンドポイントは開発環境専用です。

    **パラメータ:**
    - db: データベースセッション

    **レスポンス:**
    - dict: 成功メッセージ
    """,
)
async def seed_data_endpoint(
    db: AsyncSession = Depends(get_db),
):
    logger.info("seed_data_endpoint - start")
    try:
        await seed_data(db)
        logger.info("seed_data_endpoint - success")
        return {"msg": "seed_data API successfully"}
    finally:
        logger.info("seed_data_endpoint - end")


# =============================================================================
# 開発用パスワードリセットテスト機能
# =============================================================================


class TestPasswordResetData(BaseModel):
    email: str
    new_password: str


@router.post(
    "/test-reset-password",
    response_model=dict,
    summary="【開発用】パスワードリセットテスト",
    description="""【開発用】認証不要でパスワードリセット機能をテストします。

    **注意:** このエンドポイントは開発環境専用です。本番環境では使用しないでください。

    **パラメータ:**
    - email: テスト対象のメールアドレス
    - new_password: 新しいパスワード

    **レスポンス:**
    - dict: テスト結果とトークン情報
    """,
)
async def test_reset_password_endpoint(
    test_data: TestPasswordResetData,
    db: AsyncSession = Depends(get_db),
):
    logger.info("test_reset_password_endpoint - start", email=test_data.email)
    try:
        # 1. パスワードリセットトークンを生成（実際のメール送信プロセスをシミュレート）
        reset_token = create_access_token(data={"email": test_data.email}, expires_delta=timedelta(hours=1))
        logger.info("test_reset_password_endpoint - token generated", email=test_data.email)

        # 2. 生成されたトークンを使ってパスワードリセットを実行
        await reset_password(test_data.email, test_data.new_password, db)
        logger.info("test_reset_password_endpoint - password reset completed", email=test_data.email)

        return {
            "msg": "Password reset test completed successfully",
            "email": test_data.email,
            "reset_token": reset_token,
            "reset_url": f"http://localhost:3000/auth/reset-password?token={reset_token}",
            "note": "This is a development test endpoint. The password has been actually changed.",
        }
    except Exception as e:
        logger.error("test_reset_password_endpoint - error", email=test_data.email, error=str(e))
        return {"msg": "Password reset test failed", "email": test_data.email, "error": str(e)}
    finally:
        logger.info("test_reset_password_endpoint - end", email=test_data.email)


# =============================================================================
# ヘルスチェック機能
# =============================================================================


@router.get(
    "/health",
    response_model=SuccessResponse[dict],
    summary="基本ヘルスチェック",
    description="""システムの基本的なヘルスチェックを行います。

    APIサーバーが正常に動作しているかどうかを確認できます。

    **使用ケース:**
    - システム監視ツールによる定期チェック
    - ロードバランサーのヘルスチェック
    - デプロイ後の動作確認

    **認証:** 不要
    """,
)
async def health_check() -> dict:
    logger.info("health_check - start")
    try:
        result = create_success_response(message="APIが正常に動作しています", data={"status": "healthy"})
        logger.info("health_check - success")
        return result
    finally:
        logger.info("health_check - end")


@router.get(
    "/health/db",
    response_model=SuccessResponse[dict],
    summary="データベースヘルスチェック",
    description="""データベース接続状態のヘルスチェックを行います。

    PostgreSQLデータベースへの接続確認と基本的なクエリ実行を
    行い、データベースが正常に動作しているかを確認します。

    **チェック内容:**
    - データベースコネクションの確認
    - シンプルなSELECTクエリの実行
    - レスポンス時間の測定

    **使用ケース:**
    - データベースサービスの状態監視
    - アプリケーションデプロイ後の確認
    - データベースメンテナンス後の動作確認

    **認証:** 不要
    """,
)
async def health_check_db(session: AsyncSession = Depends(get_db)) -> dict:
    logger.info("health_check_db - start")
    try:
        # シンプルなクエリでデータベース接続確認
        result = await session.execute(text("SELECT 1"))
        result.scalar()

        response = create_success_response(message="データベースに正常に接続しています", data={"status": "healthy", "database": "connected"})
        logger.info("health_check_db - success")
        return response
    except Exception as e:
        logger.error("health_check_db - database connection failed", error=str(e))
        response = create_error_response(message="データベース接続に失敗しました", error_code=ErrorCodes.DATABASE_ERROR, details={"database": "disconnected", "error": str(e)})
        return response
    finally:
        logger.info("health_check_db - end")
