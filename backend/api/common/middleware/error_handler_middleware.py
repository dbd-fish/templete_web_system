import traceback

import structlog
from fastapi import HTTPException, Request
from jwt.exceptions import InvalidTokenError as JWTError
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

# ログ設定
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
            # Handle HTTPException
            error_trace = traceback.format_exc()  # Get stack trace
            logger.warning(
                "HTTP exception occurred",
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
            # Handle ValidationError
            error_trace = traceback.format_exc()  # Get stack trace
            logger.error(
                "Validation error occurred",
                errors=val_exc.errors(),
                # user_ip=request.client.host,
                path=request.url.path,
                method=request.method,
                stack_trace=error_trace,
            )
            return JSONResponse(
                status_code=422,
                content={"message": "バリデーションエラー", "errors": val_exc.errors()},
            )
        except SQLAlchemyError as db_exc:
            # Handle SQLAlchemyError
            error_trace = traceback.format_exc()  # Get stack trace
            logger.error(
                "SQLAlchemy error occurred",
                error=str(db_exc),
                # user_ip=request.client.host,
                path=request.url.path,
                method=request.method,
                stack_trace=error_trace,
            )
            return JSONResponse(
                status_code=500,
                content={"message": "データベースエラーが発生しました"},
            )

        except JWTError as jwt_exc:
            # Handle JWTError
            error_trace = traceback.format_exc()  # Get stack trace
            logger.error(
                "JWT error occurred",
                error=str(jwt_exc),
                path=request.url.path,
                method=request.method,
                stack_trace=error_trace,
            )
            return JSONResponse(
                status_code=401,
                content={"message": "無効または期限切れのトークンです"},
            )

        except Exception as exc:
            # Handle other unexpected exceptions
            error_trace = traceback.format_exc()  # Get stack trace
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
                content={"message": "内部サーバーエラー"},
            )
