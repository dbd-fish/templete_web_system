import traceback

import structlog
from fastapi import HTTPException, Request
from jose import JWTError
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

# ログの設定
logger = structlog.get_logger()


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """リクエスト処理中に発生した例外をキャッチし、適切なレスポンスを返すミドルウェア。
    """

    async def dispatch(self, request: Request, call_next):
        """リクエスト処理中に発生した例外をキャッチし、適切なレスポンスを返します。

        Args:
            request (Request): FastAPIのリクエストオブジェクト。
            call_next (Callable): 次のミドルウェアまたはエンドポイントを呼び出す関数。

        Returns:
            Response: エラーレスポンスまたは処理後のレスポンスオブジェクト。

        """
        try:
            response = await call_next(request)  # 次の処理を実行
            return response
        except HTTPException as http_exc:
            # HTTPExceptionが発生した場合の処理
            error_trace = traceback.format_exc()  # スタックトレースを取得
            logger.warning(
                "HTTPException occurred",
                detail=http_exc.detail,
                status_code=http_exc.status_code,
                # user_ip=request.client.host,
                path=request.url.path,
                method=request.method,
                stack_trace=error_trace,
            )
            return JSONResponse(
                status_code=http_exc.status_code,
                content={"message": http_exc.detail},
                headers=http_exc.headers,
            )
        except ValidationError as val_exc:
            # ValidationErrorが発生した場合の処理
            error_trace = traceback.format_exc()  # スタックトレースを取得
            logger.error(
                "ValidationError occurred",
                errors=val_exc.errors(),
                # user_ip=request.client.host,
                path=request.url.path,
                method=request.method,
                stack_trace=error_trace,
            )
            return JSONResponse(
                status_code=422,
                content={"message": "Validation error", "errors": val_exc.errors()},
            )
        except SQLAlchemyError as db_exc:
            # SQLAlchemyErrorが発生した場合の処理
            error_trace = traceback.format_exc()  # スタックトレースを取得
            logger.error(
                "SQLAlchemyError occurred",
                error=str(db_exc),
                # user_ip=request.client.host,
                path=request.url.path,
                method=request.method,
                stack_trace=error_trace,
            )
            return JSONResponse(
                status_code=500,
                content={"message": "Database error occurred"},
            )

        except JWTError as jwt_exc:
            # JWTError が発生した場合の処理
            error_trace = traceback.format_exc()  # スタックトレースを取得
            logger.error(
                "JWTError occurred",
                error=str(jwt_exc),
                path=request.url.path,
                method=request.method,
                stack_trace=error_trace,
            )
            return JSONResponse(
                status_code=401,
                content={"message": "Invalid or expired token"},
            )

        except Exception as exc:
            # その他の予期しない例外が発生した場合の処理
            error_trace = traceback.format_exc()  # スタックトレースを取得
            logger.error(
                "Unhandled exception occurred",
                error=str(exc),
                # user_ip=request.client.host,
                path=request.url.path,
                method=request.method,
                stack_trace=error_trace,
            )
            return JSONResponse(
                status_code=500,
                content={"message": "Internal Server Error"},
            )
