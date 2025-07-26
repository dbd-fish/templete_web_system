"""
統一エラーハンドリングミドルウェア

FastAPIの例外処理を統一化し、エラー発生箇所の追跡機能を提供
"""

import sys
import traceback
from typing import Any, Dict, Optional

import structlog
from fastapi import HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from jose.exceptions import JWTError
from sqlalchemy.exc import SQLAlchemyError
from starlette.middleware.base import BaseHTTPMiddleware

from api.common.response_schemas import ErrorCodes, create_error_response

logger = structlog.get_logger()


class BusinessLogicError(Exception):
    """
    ビジネスロジックエラー用のカスタム例外
    """

    def __init__(self, message: str, error_code: str = ErrorCodes.BUSINESS_RULE_VIOLATION, details: dict | None = None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


def get_error_location() -> Dict[str, Any]:
    """
    例外が実際に発生した場所の情報を取得
    
    Returns:
        dict: エラー発生箇所の情報
    """
    # 現在の例外情報を取得
    exc_type, exc_value, exc_tb = sys.exc_info()
    if not exc_tb:
        return {}
    
    # トレースバックから最も深い（最初の）エラー発生箇所を取得
    tb_list = traceback.extract_tb(exc_tb)
    
    # apiディレクトリ内で、middleware/error_handling_middleware.py以外の最初のフレームを探す
    for frame in tb_list:
        if "/api/" in frame.filename and "error_handling_middleware.py" not in frame.filename:
            return {
                "error_file": frame.filename.split("/")[-1],
                "error_function": frame.name,
                "error_line": frame.lineno,
                "error_code": frame.line,  # 実際のコード行
            }
    
    # 見つからない場合は最後のフレーム
    if tb_list:
        frame = tb_list[-1]
        return {
            "error_file": frame.filename.split("/")[-1],
            "error_function": frame.name,
            "error_line": frame.lineno,
            "error_code": frame.line,
        }
    
    return {}


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """統一エラーハンドリングミドルウェア"""

    async def dispatch(self, request: Request, call_next):
        """
        リクエスト処理中の例外を統一的にハンドリング
        
        Args:
            request: FastAPIリクエストオブジェクト
            call_next: 次のミドルウェアまたはエンドポイントを呼び出す関数
            
        Returns:
            Response: 処理後のレスポンスオブジェクト
        """
        try:
            response = await call_next(request)
            return response
        except HTTPException as exc:
            return await self._handle_http_exception(request, exc)
        except RequestValidationError as exc:
            return await self._handle_validation_error(request, exc)
        except SQLAlchemyError as exc:
            return await self._handle_sqlalchemy_error(request, exc)
        except JWTError as exc:
            return await self._handle_jwt_error(request, exc)
        except BusinessLogicError as exc:
            return await self._handle_business_logic_error(request, exc)
        except Exception as exc:
            return await self._handle_general_exception(request, exc)

    async def _handle_http_exception(self, request: Request, exc: HTTPException) -> JSONResponse:
        """HTTPException用のハンドラー"""
        error_location = get_error_location()
        
        logger.warning(
            "HTTP exception occurred",
            status_code=exc.status_code,
            detail=exc.detail,
            path=request.url.path,
            method=request.method,
            **error_location,
            exc_info=True
        )

        # ステータスコードに応じてエラーコードを決定
        error_code_map = {
            status.HTTP_401_UNAUTHORIZED: ErrorCodes.AUTHENTICATION_FAILED,
            status.HTTP_403_FORBIDDEN: ErrorCodes.AUTHORIZATION_FAILED,
            status.HTTP_404_NOT_FOUND: ErrorCodes.RESOURCE_NOT_FOUND,
            status.HTTP_409_CONFLICT: ErrorCodes.RESOURCE_CONFLICT,
            status.HTTP_422_UNPROCESSABLE_ENTITY: ErrorCodes.VALIDATION_ERROR,
            status.HTTP_500_INTERNAL_SERVER_ERROR: ErrorCodes.INTERNAL_SERVER_ERROR,
            status.HTTP_501_NOT_IMPLEMENTED: ErrorCodes.OPERATION_NOT_ALLOWED,
        }

        error_code = error_code_map.get(exc.status_code, "HTTP_ERROR")

        error_response = create_error_response(
            message=str(exc.detail),
            error_code=error_code,
            details={
                "status_code": exc.status_code,
                "path": request.url.path,
                "method": request.method
            }
        )

        return JSONResponse(status_code=exc.status_code, content=error_response)

    async def _handle_validation_error(self, request: Request, exc: RequestValidationError) -> JSONResponse:
        """バリデーションエラー用のハンドラー"""
        error_location = get_error_location()
        
        logger.warning(
            "Validation error occurred",
            errors=exc.errors(),
            path=request.url.path,
            method=request.method,
            **error_location,
            exc_info=True
        )

        # Format validation error details
        validation_errors = []
        for error in exc.errors():
            validation_errors.append({
                "field": ".".join(str(loc) for loc in error["loc"]),
                "message": error["msg"],
                "type": error["type"],
                "input": error.get("input")
            })

        error_response = create_error_response(
            message="入力データの検証に失敗しました",
            error_code=ErrorCodes.VALIDATION_ERROR,
            details={
                "validation_errors": validation_errors,
                "path": request.url.path,
                "method": request.method
            }
        )

        return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content=error_response)

    async def _handle_sqlalchemy_error(self, request: Request, exc: SQLAlchemyError) -> JSONResponse:
        """SQLAlchemyエラー用のハンドラー"""
        error_location = get_error_location()
        
        logger.error(
            "Database error occurred",
            error=str(exc),
            path=request.url.path,
            method=request.method,
            **error_location,
            exc_info=True
        )

        error_response = create_error_response(
            message="データベースエラーが発生しました",
            error_code=ErrorCodes.DATABASE_ERROR,
            details={
                "path": request.url.path,
                "method": request.method,
                # Don't include detailed error info in production
                "error_detail": str(exc) if logger.level == "DEBUG" else None,
            }
        )

        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=error_response)

    async def _handle_jwt_error(self, request: Request, exc: JWTError) -> JSONResponse:
        """JWTエラー用のハンドラー"""
        error_location = get_error_location()
        
        logger.warning(
            "JWT error occurred",
            error=str(exc),
            path=request.url.path,
            method=request.method,
            **error_location,
            exc_info=True
        )

        # エラーメッセージをより具体的に
        error_message = "無効または期限切れのトークンです"
        error_str = str(exc).lower()
        if "expired" in error_str:
            error_message = "トークンが期限切れです"
        elif "invalid" in error_str:
            error_message = "無効なトークンです"

        error_response = create_error_response(
            message=error_message,
            error_code=ErrorCodes.TOKEN_INVALID,
            details={
                "path": request.url.path,
                "method": request.method,
            }
        )

        return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content=error_response)

    async def _handle_business_logic_error(self, request: Request, exc: BusinessLogicError) -> JSONResponse:
        """ビジネスロジックエラー用のハンドラー"""
        error_location = get_error_location()
        
        logger.info(
            "Business logic error occurred",
            message=exc.message,
            error_code=exc.error_code,
            path=request.url.path,
            method=request.method,
            **error_location,
            exc_info=True
        )

        error_response = create_error_response(
            message=exc.message,
            error_code=exc.error_code,
            details={
                **exc.details,
                "path": request.url.path,
                "method": request.method
            }
        )

        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=error_response)

    async def _handle_general_exception(self, request: Request, exc: Exception) -> JSONResponse:
        """予期しない例外用のハンドラー"""
        error_location = get_error_location()
        
        logger.error(
            "Unexpected error occurred",
            error=str(exc),
            error_type=type(exc).__name__,
            path=request.url.path,
            method=request.method,
            **error_location,
            exc_info=True
        )

        error_response = create_error_response(
            message="予期しないエラーが発生しました",
            error_code=ErrorCodes.INTERNAL_SERVER_ERROR,
            details={
                "path": request.url.path,
                "method": request.method,
                # Don't include detailed error info in production
                "error_type": type(exc).__name__ if logger.level == "DEBUG" else None,
            }
        )

        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=error_response)