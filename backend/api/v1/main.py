import os
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError

from .common.core.log_config import logger
from .common.exception_handlers import (
    http_exception_handler,
    validation_exception_handler,
    sqlalchemy_exception_handler,
    general_exception_handler,
    business_logic_exception_handler,
    BusinessLogicError
)
from sqlalchemy.exc import SQLAlchemyError
from .common.database import database
from .common.middleware import AddUserIPMiddleware, ErrorHandlerMiddleware
from .common.setting import setting
from .features.feature_auth.auth_controller import router as auth_router
from .features.feature_dev.dev_controller import router as dev_router

# タイムゾーンをJST（日本標準時）に設定
os.environ["TZ"] = "Asia/Tokyo"
time.tzset()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """アプリケーションのライフサイクル管理を行うコンテキストマネージャ。
    """
    logger.info("Application startup - connecting to database.")

    # 明示的にイベントループを設定（最新バージョンでも安全）
    # loop = asyncio.get_running_loop()
    # asyncio.set_event_loop(loop)

    await database.connect()
    yield
    logger.info("Application shutdown - disconnecting from database.")
    await database.disconnect()

# FastAPIアプリケーションのインスタンスを作成し、lifespanを設定
if setting.DEV_MODE:
    app = FastAPI(
        title="Template Web System API",
        lifespan=lifespan
    )
else:
    # 本番環境ではOpenAPIなどを無効化
    app = FastAPI(
        title="Template Web System API",
        lifespan=lifespan, 
        docs_url=None, 
        redoc_url=None, 
        openapi_url=None
    )

# ミドルウェアの追加 (ユーザーIP記録とエラーハンドリング)
# NOTE: ミドルウェアを別ファイルにする場合、@app.middleware()が機能しないっぽい。
#       そのため、add_middlewareでミドルウェアを登録する方法にする。
app.add_middleware(AddUserIPMiddleware)
app.add_middleware(ErrorHandlerMiddleware)

# 統一例外ハンドラの登録
app.add_exception_handler(HTTPException, http_exception_handler) # type: ignore
app.add_exception_handler(RequestValidationError, validation_exception_handler) # type: ignore
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler) # type: ignore
app.add_exception_handler(BusinessLogicError, business_logic_exception_handler) # type: ignore
app.add_exception_handler(Exception, general_exception_handler) # type: ignore

# ルーターをアプリケーションに追加
if setting.DEV_MODE:
    # 開発用のルーター定義
    app.include_router(dev_router, prefix="/api/v1/dev", tags=["dev"])

# 認証用のルーター
app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])

# このスクリプトが直接実行された場合、Uvicornサーバーを起動
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.v1.main:app", host="0.0.0.0", port=8000, reload=True)
