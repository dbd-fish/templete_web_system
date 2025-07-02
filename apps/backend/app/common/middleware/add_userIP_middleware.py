from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.common.core.log_config import logger, structlog


class AddUserIPMiddleware(BaseHTTPMiddleware):
    """リクエストのIPアドレスを取得し、ログのコンテキストに追加するミドルウェア。
    """

    async def dispatch(self, request: Request, call_next):
        """リクエストのIPアドレスを取得し、ログのコンテキストに追加します。

        Args:
            request (Request): FastAPIのリクエストオブジェクト。
            call_next (Callable): 次のミドルウェアまたはエンドポイントを呼び出す関数。

        Returns:
            Response: 処理後のレスポンスオブジェクト。

        """
        user_ip = request.client.host if request.client else "unknown"  # クライアントのIPアドレスを取得
        structlog.contextvars.bind_contextvars(user_ip=user_ip)  # ログコンテキストにIPアドレスをバインド
        logger.info("User IP added to log context", user_ip=user_ip)  # IPアドレスをログに記録
        try:
            response = await call_next(request)  # 次の処理を実行
        finally:
            structlog.contextvars.clear_contextvars()  # ログコンテキストをクリア
        return response
