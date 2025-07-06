"""
例外ハンドラーの単体テスト（AAAパターン）
"""

from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from api.common.exception_handlers import (
    BusinessLogicError,
    business_logic_exception_handler,
    general_exception_handler,
    http_exception_handler,
    sqlalchemy_exception_handler,
    validation_exception_handler,
)
from api.common.response_schemas import ErrorCodes


@pytest.mark.asyncio
async def test_http_exception_handler_401():
    """http_exception_handler

    【正常系】401 Unauthorizedエラーが適切にハンドリングされることを確認。
    """
    # Arrange: 401エラーとリクエストオブジェクトを準備
    mock_request = MagicMock(spec=Request)
    mock_request.url.path = "/api/v1/auth/me"
    mock_request.method = "GET"

    http_exc = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="認証情報が無効です")

    # Act: HTTPException用ハンドラーを実行
    response = await http_exception_handler(mock_request, http_exc)

    # Assert: 適切なエラーレスポンスが生成されることを確認
    assert isinstance(response, JSONResponse)
    assert response.status_code == 401
    response_data = response.body.decode()
    assert "認証情報が無効です" in response_data
    assert ErrorCodes.AUTHENTICATION_FAILED in response_data


@pytest.mark.asyncio
async def test_http_exception_handler_404():
    """http_exception_handler

    【正常系】404 Not Foundエラーが適切にハンドリングされることを確認。
    """
    # Arrange: 404エラーとリクエストオブジェクトを準備
    mock_request = MagicMock(spec=Request)
    mock_request.url.path = "/api/v1/users/nonexistent"
    mock_request.method = "GET"

    http_exc = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="リソースが見つかりません")

    # Act: HTTPException用ハンドラーを実行
    response = await http_exception_handler(mock_request, http_exc)

    # Assert: 適切なエラーレスポンスが生成されることを確認
    assert isinstance(response, JSONResponse)
    assert response.status_code == 404
    response_data = response.body.decode()
    assert "リソースが見つかりません" in response_data
    assert ErrorCodes.RESOURCE_NOT_FOUND in response_data


@pytest.mark.asyncio
async def test_http_exception_handler_409():
    """http_exception_handler

    【正常系】409 Conflictエラーが適切にハンドリングされることを確認。
    """
    # Arrange: 409エラーとリクエストオブジェクトを準備
    mock_request = MagicMock(spec=Request)
    mock_request.url.path = "/api/v1/auth/signup"
    mock_request.method = "POST"

    http_exc = HTTPException(status_code=status.HTTP_409_CONFLICT, detail="このメールアドレスは既に使用されています")

    # Act: HTTPException用ハンドラーを実行
    response = await http_exception_handler(mock_request, http_exc)

    # Assert: 適切なエラーレスポンスが生成されることを確認
    assert isinstance(response, JSONResponse)
    assert response.status_code == 409
    response_data = response.body.decode()
    assert "このメールアドレスは既に使用されています" in response_data
    assert ErrorCodes.RESOURCE_CONFLICT in response_data


@pytest.mark.asyncio
async def test_http_exception_handler_unknown_status():
    """http_exception_handler

    【正常系】未定義のステータスコードでもエラーハンドリングされることを確認。
    """
    # Arrange: 未定義のステータスコードエラーを準備
    mock_request = MagicMock(spec=Request)
    mock_request.url.path = "/api/v1/test"
    mock_request.method = "POST"

    http_exc = HTTPException(
        status_code=418,  # I'm a teapot - 未定義のステータスコード
        detail="未定義のエラー",
    )

    # Act: HTTPException用ハンドラーを実行
    response = await http_exception_handler(mock_request, http_exc)

    # Assert: デフォルトエラーコードが使用されることを確認
    assert isinstance(response, JSONResponse)
    assert response.status_code == 418
    response_data = response.body.decode()
    assert "未定義のエラー" in response_data
    assert "HTTP_ERROR" in response_data


@pytest.mark.asyncio
async def test_validation_exception_handler():
    """validation_exception_handler

    【正常系】バリデーションエラーが適切にハンドリングされることを確認。
    """
    # Arrange: バリデーションエラーとリクエストオブジェクトを準備
    mock_request = MagicMock(spec=Request)
    mock_request.url.path = "/api/v1/auth/signup"
    mock_request.method = "POST"

    # RequestValidationErrorのモック作成
    validation_errors = [
        {"loc": ("body", "email"), "msg": "field required", "type": "value_error.missing", "input": {}},
        {"loc": ("body", "username"), "msg": "ensure this value has at least 3 characters", "type": "value_error.any_str.min_length", "input": "ab"},
    ]

    validation_exc = RequestValidationError(validation_errors)

    # Act: バリデーションエラー用ハンドラーを実行
    response = await validation_exception_handler(mock_request, validation_exc)

    # Assert: 適切なバリデーションエラーレスポンスが生成されることを確認
    assert isinstance(response, JSONResponse)
    assert response.status_code == 422
    response_data = response.body.decode()
    assert "入力データの検証に失敗しました" in response_data
    assert ErrorCodes.VALIDATION_ERROR in response_data
    assert "body.email" in response_data
    assert "body.username" in response_data


@pytest.mark.asyncio
async def test_sqlalchemy_exception_handler():
    """sqlalchemy_exception_handler

    【正常系】SQLAlchemyエラーが適切にハンドリングされることを確認。
    """
    # Arrange: SQLAlchemyエラーとリクエストオブジェクトを準備
    mock_request = MagicMock(spec=Request)
    mock_request.url.path = "/api/v1/users"
    mock_request.method = "POST"

    sql_exc = SQLAlchemyError("Database connection failed")

    # Act: SQLAlchemyエラー用ハンドラーを実行
    response = await sqlalchemy_exception_handler(mock_request, sql_exc)

    # Assert: 適切なデータベースエラーレスポンスが生成されることを確認
    assert isinstance(response, JSONResponse)
    assert response.status_code == 500
    response_data = response.body.decode()
    assert "データベースエラーが発生しました" in response_data
    assert ErrorCodes.DATABASE_ERROR in response_data


@pytest.mark.asyncio
async def test_general_exception_handler():
    """general_exception_handler

    【正常系】予期しない例外が適切にハンドリングされることを確認。
    """
    # Arrange: 一般的な例外とリクエストオブジェクトを準備
    mock_request = MagicMock(spec=Request)
    mock_request.url.path = "/api/v1/unexpected"
    mock_request.method = "GET"

    general_exc = Exception("Unexpected error occurred")

    # Act: 一般例外用ハンドラーを実行
    response = await general_exception_handler(mock_request, general_exc)

    # Assert: 適切な一般エラーレスポンスが生成されることを確認
    assert isinstance(response, JSONResponse)
    assert response.status_code == 500
    response_data = response.body.decode()
    assert "予期しないエラーが発生しました" in response_data
    assert ErrorCodes.INTERNAL_SERVER_ERROR in response_data


@pytest.mark.asyncio
async def test_business_logic_exception_handler():
    """business_logic_exception_handler

    【正常系】ビジネスロジックエラーが適切にハンドリングされることを確認。
    """
    # Arrange: ビジネスロジックエラーとリクエストオブジェクトを準備
    mock_request = MagicMock(spec=Request)
    mock_request.url.path = "/api/v1/business/action"
    mock_request.method = "POST"

    business_exc = BusinessLogicError(message="ビジネスルール違反です", error_code=ErrorCodes.BUSINESS_RULE_VIOLATION, details={"rule": "max_attempts_exceeded"})

    # Act: ビジネスロジックエラー用ハンドラーを実行
    response = await business_logic_exception_handler(mock_request, business_exc)

    # Assert: 適切なビジネスロジックエラーレスポンスが生成されることを確認
    assert isinstance(response, JSONResponse)
    assert response.status_code == 400
    response_data = response.body.decode()
    assert "ビジネスルール違反です" in response_data
    assert ErrorCodes.BUSINESS_RULE_VIOLATION in response_data
    assert "max_attempts_exceeded" in response_data


def test_business_logic_error_initialization():
    """BusinessLogicError

    【正常系】BusinessLogicErrorクラスが正しく初期化されることを確認。
    """
    # Arrange: ビジネスロジックエラーのパラメータを準備
    message = "テストエラーメッセージ"
    error_code = "TEST_ERROR"
    details = {"field": "test_field", "value": "invalid_value"}

    # Act: BusinessLogicErrorインスタンスを作成
    error = BusinessLogicError(message=message, error_code=error_code, details=details)

    # Assert: すべての属性が正しく設定されることを確認
    assert error.message == message
    assert error.error_code == error_code
    assert error.details == details
    assert str(error) == message


def test_business_logic_error_default_values():
    """BusinessLogicError

    【正常系】BusinessLogicErrorのデフォルト値が正しく設定されることを確認。
    """
    # Arrange: 最小限のパラメータを準備
    message = "デフォルト値テスト"

    # Act: デフォルト値でBusinessLogicErrorインスタンスを作成
    error = BusinessLogicError(message=message)

    # Assert: デフォルト値が正しく設定されることを確認
    assert error.message == message
    assert error.error_code == ErrorCodes.BUSINESS_RULE_VIOLATION
    assert error.details == {}


@pytest.mark.asyncio
async def test_http_exception_handler_with_logging():
    """http_exception_handler

    【正常系】HTTPエラーハンドリング時にログが正しく出力されることを確認。
    """
    # Arrange: ログモックとエラーを準備
    mock_request = MagicMock(spec=Request)
    mock_request.url.path = "/api/v1/test"
    mock_request.method = "POST"

    http_exc = HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="サーバーエラー")

    # Act & Assert: ログ出力をモックして実行
    with patch("api.common.exception_handlers.logger") as mock_logger:
        response = await http_exception_handler(mock_request, http_exc)

        # ログが正しく呼び出されることを確認
        mock_logger.warning.assert_called_once()

        # レスポンスの確認
        assert response.status_code == 500
        response_data = response.body.decode()
        assert "サーバーエラー" in response_data


@pytest.mark.asyncio
async def test_sqlalchemy_exception_handler_debug_mode():
    """sqlalchemy_exception_handler

    【正常系】デバッグモード時に詳細エラー情報が含まれることを確認。
    """
    # Arrange: デバッグモードのロガーとSQLエラーを準備
    mock_request = MagicMock(spec=Request)
    mock_request.url.path = "/api/v1/database"
    mock_request.method = "GET"

    sql_exc = SQLAlchemyError("Detailed database error")

    # Act & Assert: デバッグレベルのロガーをモックして実行
    with patch("api.common.exception_handlers.logger") as mock_logger:
        mock_logger.level = "DEBUG"

        response = await sqlalchemy_exception_handler(mock_request, sql_exc)

        # レスポンスにエラー詳細が含まれることを確認
        assert response.status_code == 500
        response_data = response.body.decode()
        assert "データベースエラーが発生しました" in response_data
        assert "Detailed database error" in response_data


@pytest.mark.asyncio
async def test_general_exception_handler_production_mode():
    """general_exception_handler

    【正常系】本番モード時にエラータイプが隠されることを確認。
    """
    # Arrange: 本番モードのロガーと一般例外を準備
    mock_request = MagicMock(spec=Request)
    mock_request.url.path = "/api/v1/production"
    mock_request.method = "DELETE"

    general_exc = ValueError("Sensitive error information")

    # Act & Assert: 本番レベルのロガーをモックして実行
    with patch("api.common.exception_handlers.logger") as mock_logger:
        mock_logger.level = "INFO"  # デバッグモードではない

        response = await general_exception_handler(mock_request, general_exc)

        # レスポンスに敏感な情報が含まれないことを確認
        assert response.status_code == 500
        response_data = response.body.decode()
        assert "予期しないエラーが発生しました" in response_data
        # 本番モードではエラータイプが null になることを確認
        assert '"error_type": null' in response_data or '"error_type":null' in response_data
