"""
カスタム例外クラスの単体テスト（AAAパターン）
"""

from api.common.middleware.error_handling_middleware import BusinessLogicError
from api.common.response_schemas import ErrorCodes


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
