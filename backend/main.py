import os
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError

from api.common.core.log_config import logger
from api.common.exception_handlers import (
    http_exception_handler,
    validation_exception_handler,
    sqlalchemy_exception_handler,
    general_exception_handler,
    business_logic_exception_handler,
    BusinessLogicError
)
from sqlalchemy.exc import SQLAlchemyError
from api.common.database import database
from api.common.middleware import AddUserIPMiddleware, ErrorHandlerMiddleware
from api.common.setting import setting
from api.v1.features.feature_auth.auth_controller import router as auth_router
from api.v1.features.feature_dev.dev_controller import router as dev_router
from api.v1.routes.users import router as users_router
from api.v1.routes.health import router as health_router

# タイムゾーンをJST（日本標準時）に設定
os.environ["TZ"] = "Asia/Tokyo"
time.tzset()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """アプリケーションのライフサイクル管理を行うコンテキストマネージャ。
    """
    logger.info("Application startup - connecting to database")

    # 明示的にイベントループを設定（最新バージョンでも安全）
    # loop = asyncio.get_running_loop()
    # asyncio.set_event_loop(loop)

    await database.connect()
    yield
    logger.info("Application shutdown - disconnecting from database")
    await database.disconnect()

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
        servers=[
            {
                "url": "http://localhost:8000",
                "description": "開発サーバー"
            }
        ]
    )
else:
    # 本番環境ではOpenAPIドキュメントを無効化（セキュリティ対策）
    app = FastAPI(
        title="Template Web System API",
        lifespan=lifespan, 
        docs_url=None, 
        redoc_url=None, 
        openapi_url=None
    )

# ミドルウェアの追加（ユーザーIP記録とエラーハンドリング）
# 注意: ミドルウェアを別ファイルにする場合、@app.middleware()デコレータが機能しないため、
#       add_middlewareメソッドでミドルウェアを登録する方法を採用
app.add_middleware(AddUserIPMiddleware)
app.add_middleware(ErrorHandlerMiddleware)

# 統一例外ハンドラーの登録
app.add_exception_handler(HTTPException, http_exception_handler) # type: ignore
app.add_exception_handler(RequestValidationError, validation_exception_handler) # type: ignore
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler) # type: ignore
app.add_exception_handler(BusinessLogicError, business_logic_exception_handler) # type: ignore
app.add_exception_handler(Exception, general_exception_handler) # type: ignore

# ルーターをアプリケーションに追加
if setting.DEV_MODE:
    # 開発環境用のルーター定義
    app.include_router(dev_router, prefix="/api/v1/dev", tags=["開発ツール"])

# 認証関連のルーター
app.include_router(auth_router, prefix="/api/v1/auth", tags=["認証"])

# ユーザー管理関連のルーター
app.include_router(users_router, prefix="/api/v1/users", tags=["ユーザー管理"])

# ヘルスチェック関連のルーター
app.include_router(health_router, prefix="/api/v1/health", tags=["ヘルスチェック"])

# スクリプトが直接実行された場合のUvicornサーバー起動設定
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.v1.main:app", host="0.0.0.0", port=8000, reload=True)
