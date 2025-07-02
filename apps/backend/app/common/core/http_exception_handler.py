import traceback

import structlog
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse

# ロガーの設定
logger = structlog.get_logger()

async def http_exception_handler(request: Request, exc: HTTPException):
    """HTTPExceptionが発生した際のハンドラ。

    Args:
        request (Request): リクエストオブジェクト。
        exc (HTTPException): 発生したHTTP例外。

    Returns:
        JSONResponse: エラーレスポンス。

    """
    error_trace = traceback.format_exc()  # スタックトレースを取得
    user_ip = request.client.host if request.client else "unknown"  # クライアントのIPアドレスを取得
    # エラーログの記録
    logger.error(
        "HTTP error occurred",
        status_code=exc.status_code,
        detail=exc.detail,
        headers=exc.headers,
        user_ip=user_ip,
        url=request.url.path,
        method=request.method,
        stack_trace=error_trace,
    )

    # JSONレスポンスを返却
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
        },
        headers=exc.headers,
    )
