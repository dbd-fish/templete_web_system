"""
統一エラーハンドラー

FastAPIの例外ハンドラーを標準レスポンス形式に統一
"""


import structlog
from fastapi import HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from .response_schemas import ErrorCodes, create_error_response

logger = structlog.get_logger()


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """
    HTTPException用の統一エラーハンドラー

    Args:
        request: FastAPIリクエストオブジェクト
        exc: HTTPException

    Returns:
        JSONResponse: 統一フォーマットのエラーレスポンス
    """
    logger.warning("HTTP exception occurred", status_code=exc.status_code, detail=exc.detail, path=request.url.path, method=request.method)

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

    error_response = create_error_response(message=str(exc.detail), error_code=error_code, details={"status_code": exc.status_code, "path": request.url.path, "method": request.method})

    return JSONResponse(status_code=exc.status_code, content=error_response)


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    バリデーションエラー用の統一エラーハンドラー

    Args:
        request: FastAPIリクエストオブジェクト
        exc: RequestValidationError

    Returns:
        JSONResponse: 統一フォーマットのエラーレスポンス
    """
    logger.warning("Validation error occurred", errors=exc.errors(), path=request.url.path, method=request.method)

    # Format validation error details
    validation_errors = []
    for error in exc.errors():
        validation_errors.append({"field": ".".join(str(loc) for loc in error["loc"]), "message": error["msg"], "type": error["type"], "input": error.get("input")})

    error_response = create_error_response(
        message="入力データの検証に失敗しました", error_code=ErrorCodes.VALIDATION_ERROR, details={"validation_errors": validation_errors, "path": request.url.path, "method": request.method}
    )

    return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content=error_response)


async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    """
    SQLAlchemyエラー用の統一エラーハンドラー

    Args:
        request: FastAPIリクエストオブジェクト
        exc: SQLAlchemyError

    Returns:
        JSONResponse: 統一フォーマットのエラーレスポンス
    """
    logger.error("Database error occurred", error=str(exc), path=request.url.path, method=request.method)

    error_response = create_error_response(
        message="データベースエラーが発生しました",
        error_code=ErrorCodes.DATABASE_ERROR,
        details={
            "path": request.url.path,
            "method": request.method,
            # Don't include detailed error info in production
            "error_detail": str(exc) if logger.level == "DEBUG" else None,
        },
    )

    return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=error_response)


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    予期しない例外用の統一エラーハンドラー

    Args:
        request: FastAPIリクエストオブジェクト
        exc: Exception

    Returns:
        JSONResponse: 統一フォーマットのエラーレスポンス
    """
    logger.error("Unexpected error occurred", error=str(exc), error_type=type(exc).__name__, path=request.url.path, method=request.method, exc_info=True)

    error_response = create_error_response(
        message="予期しないエラーが発生しました",
        error_code=ErrorCodes.INTERNAL_SERVER_ERROR,
        details={
            "path": request.url.path,
            "method": request.method,
            # Don't include detailed error info in production
            "error_type": type(exc).__name__ if logger.level == "DEBUG" else None,
        },
    )

    return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=error_response)


# カスタム例外クラス
class BusinessLogicError(Exception):
    """
    ビジネスロジックエラー用のカスタム例外
    """

    def __init__(self, message: str, error_code: str = ErrorCodes.BUSINESS_RULE_VIOLATION, details: dict | None = None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


async def business_logic_exception_handler(request: Request, exc: BusinessLogicError) -> JSONResponse:
    """
    ビジネスロジックエラー用の統一エラーハンドラー

    Args:
        request: FastAPIリクエストオブジェクト
        exc: BusinessLogicError

    Returns:
        JSONResponse: 統一フォーマットのエラーレスポンス
    """
    logger.info("Business logic error occurred", message=exc.message, error_code=exc.error_code, path=request.url.path, method=request.method)

    error_response = create_error_response(message=exc.message, error_code=exc.error_code, details={**exc.details, "path": request.url.path, "method": request.method})

    return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=error_response)
