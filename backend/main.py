import os
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from jwt.exceptions import InvalidTokenError as JWTError
from sqlalchemy.exc import SQLAlchemyError
from starlette.middleware.sessions import SessionMiddleware

from api.common.core.log_config import logger
from api.common.database import database
from api.common.exception_handlers import (
    BusinessLogicError,
    business_logic_exception_handler,
    general_exception_handler,
    http_exception_handler,
    jwt_exception_handler,
    sqlalchemy_exception_handler,
    validation_exception_handler,
)
from api.common.middleware import AddUserIPMiddleware
from api.common.redis_client import redis_client
from api.common.setting import setting
from api.v1.features.feature_auth.route import router as auth_router
from api.v1.features.feature_dev.route import router as dev_router

# os.environで環境変数TZを設定し日本時間を指定
os.environ["TZ"] = "Asia/Tokyo"
# time.tzset()でシステムのタイムゾーン設定を変更
time.tzset()




@asynccontextmanager
async def lifespan(app: FastAPI):
    """アプリケーションのライフサイクル管理を行うコンテキストマネージャ。"""
    logger.info("Application startup - connecting to database and Redis")

    # databasesライブラリのDatabaseオブジェクトでデータベースに接続
    await database.connect()
    # RedisクライアントでRedisサーバーに接続
    await redis_client.connect()
    yield
    logger.info("Application shutdown - disconnecting from database and Redis")
    # databasesライブラリのDatabaseオブジェクトでデータベースから切断
    await database.disconnect()
    # RedisクライアントでRedisサーバーから切断
    await redis_client.disconnect()


# FastAPIアプリケーションのインスタンスを作成し、ライフサイクルを設定
if setting.DEV_MODE:
    app = FastAPI(
        title="Template Web System API",
        description="""
## Template Web System API v1

FastAPIで構築された包括的なWebシステムテンプレートAPIです。

### 機能
- **認証**: セキュアなHttpOnlyクッキーを使用したJWTベース認証
- **ユーザー管理**: 完全なユーザーライフサイクル管理
- **ヘルス監視**: システムヘルスとデータベース接続チェック
- **開発ツール**: 開発環境用ユーティリティ

### アーキテクチャ
- **データベース**: PostgreSQL 13 + 非同期SQLAlchemy 2.0
- **セキュリティ**: bcryptパスワードハッシュ、JWTトークン
- **バリデーション**: 包括的な検証を行うPydanticモデル
- **エラーハンドリング**: 構造化ログを伴う標準化エラーレスポンス

### レスポンス形式
すべてのAPIレスポンスは統一形式に従います：
```json
{
    "success": true,
    "message": "操作が正常に完了しました",
    "timestamp": "2025-07-02T12:00:00+09:00",
    "data": { ... }
}
```

### 認証
ほとんどのエンドポイントはHttpOnlyクッキーに格納されたJWTトークンによる認証が必要です。
認証情報を取得するには `/api/v1/auth/login` を使用してください。
        """,
        version="1.0.0",
        lifespan=lifespan,
        contact={
            "name": "Template Web System",
            "email": "admin@example.com",
        },
        license_info={
            "name": "MIT License",
            "url": "https://opensource.org/licenses/MIT",
        },
        servers=[{"url": "http://localhost:8000", "description": "開発サーバー"}],
    )
else:
    # 本番環境ではOpenAPIドキュメントを無効化（セキュリティ対策）
    app = FastAPI(title="Template Web System API", lifespan=lifespan, docs_url=None, redoc_url=None, openapi_url=None)

# ミドルウェアの追加（ユーザーIP記録）
# 注意: ミドルウェアを別ファイルにする場合、@app.middleware()デコレータが機能しないため、
#       add_middlewareメソッドでミドルウェアを登録する方法を採用
app.add_middleware(AddUserIPMiddleware)

# CORS設定（ブラウザからのSwagger UIアクセス対応）
app.add_middleware(
    CORSMiddleware,
    allow_origins=setting.CORS_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Google OAuth 2.0用セッションミドルウェアを追加
app.add_middleware(SessionMiddleware, secret_key=setting.SECRET_KEY)


# 統一例外ハンドラーの登録
# FastAPIの制限により、HTTPExceptionはミドルウェアでキャッチできないため、
# 例外ハンドラーによる統一レスポンス形式を採用
# ※ UnifiedErrorHandlerMiddlewareは削除し、例外ハンドラーによる処理に統一
app.add_exception_handler(HTTPException, http_exception_handler)  # type: ignore
app.add_exception_handler(RequestValidationError, validation_exception_handler)  # type: ignore
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)  # type: ignore
app.add_exception_handler(JWTError, jwt_exception_handler)  # type: ignore
app.add_exception_handler(BusinessLogicError, business_logic_exception_handler)  # type: ignore
app.add_exception_handler(Exception, general_exception_handler)  # type: ignore

# ルーターをアプリケーションに追加
if setting.DEV_MODE:
    # 開発環境用のルーター定義（ヘルスチェック機能も含む）
    app.include_router(dev_router, prefix="/api/v1/dev", tags=["開発ツール"])

# 認証関連のルーター（ユーザー管理機能も含む）
app.include_router(auth_router, prefix="/api/v1/auth", tags=["認証"])


# デバッグ用ルートエンドポイント（Swagger UIリンク提供）
@app.get("/", tags=["システム情報"])
async def root():
    """
    ルートエンドポイント - API情報とSwagger UIへのリンクを提供

    開発中のAPI確認に便利な基本情報を提供します。
    """
    return {"message": "Template Web System API", "version": "1.0.0", "swagger_ui": "http://localhost:8000/docs", "openapi_json": "http://localhost:8000/openapi.json", "status": "running"}


# スクリプトが直接実行された場合のUvicornサーバー起動設定
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("api.v1.main:app", host="0.0.0.0", port=8000, reload=True)
