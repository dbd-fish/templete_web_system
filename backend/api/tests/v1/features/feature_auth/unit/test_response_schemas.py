"""
レスポンススキーマの単体テスト（AAAパターン）
"""

from datetime import datetime

import pytest
from pydantic import ValidationError

from api.common.response_schemas import (
    BaseResponse,
    EmptyData,
    ErrorCodes,
    ErrorResponse,
    MessageResponse,
    PaginationMeta,
    SuccessResponse,
    create_empty_response,
    create_error_response,
    create_message_response,
    create_paginated_response,
    create_success_response,
)


def test_success_response_creation():
    """SuccessResponse

    【正常系】成功レスポンスが正常に作成されることを確認。
    """
    # Arrange: 成功レスポンス用のデータを準備
    test_data = {"user_id": "12345", "username": "testuser"}
    test_message = "操作が正常に完了しました"

    # Act: SuccessResponseを作成
    response = SuccessResponse[dict](message=test_message, data=test_data)

    # Assert: レスポンスが正しく作成されることを確認
    assert response.success is True
    assert response.message == test_message
    assert response.data == test_data
    assert isinstance(response.timestamp, datetime)


def test_success_response_without_data():
    """SuccessResponse

    【正常系】データなしの成功レスポンスが正常に作成されることを確認。
    """
    # Arrange: データなしの成功レスポンス用メッセージを準備
    test_message = "削除が完了しました"

    # Act: データなしのSuccessResponseを作成
    response = SuccessResponse[None](message=test_message)

    # Assert: データがNoneでもレスポンスが正しく作成されることを確認
    assert response.success is True
    assert response.message == test_message
    assert response.data is None
    assert isinstance(response.timestamp, datetime)


def test_error_response_creation():
    """ErrorResponse

    【正常系】エラーレスポンスが正常に作成されることを確認。
    """
    # Arrange: エラーレスポンス用のデータを準備
    test_message = "認証に失敗しました"
    test_error_code = ErrorCodes.AUTHENTICATION_FAILED
    test_details = {"field": "password", "reason": "incorrect"}

    # Act: ErrorResponseを作成
    response = ErrorResponse(message=test_message, error_code=test_error_code, details=test_details)

    # Assert: エラーレスポンスが正しく作成されることを確認
    assert response.success is False
    assert response.message == test_message
    assert response.error_code == test_error_code
    assert response.details == test_details
    assert isinstance(response.timestamp, datetime)


def test_error_response_without_details():
    """ErrorResponse

    【正常系】詳細なしのエラーレスポンスが正常に作成されることを確認。
    """
    # Arrange: 詳細なしのエラーレスポンス用データを準備
    test_message = "サーバーエラーが発生しました"
    test_error_code = ErrorCodes.INTERNAL_SERVER_ERROR

    # Act: 詳細なしのErrorResponseを作成
    response = ErrorResponse(message=test_message, error_code=test_error_code)

    # Assert: 詳細がNoneでもエラーレスポンスが正しく作成されることを確認
    assert response.success is False
    assert response.message == test_message
    assert response.error_code == test_error_code
    assert response.details is None
    assert isinstance(response.timestamp, datetime)


def test_message_response_creation():
    """MessageResponse

    【正常系】メッセージレスポンスが正常に作成されることを確認。
    """
    # Arrange: メッセージレスポンス用データを準備
    test_message = "メール送信が完了しました"

    # Act: MessageResponseを作成
    response = MessageResponse(message=test_message)

    # Assert: メッセージレスポンスが正しく作成されることを確認
    assert response.message == test_message


def test_create_success_response_function():
    """create_success_response

    【正常系】成功レスポンス作成関数が正常に動作することを確認。
    """
    # Arrange: 成功レスポンス作成用データを準備
    test_message = "ユーザー登録が完了しました"
    test_data = {"user_id": "abc123", "email": "test@example.com"}

    # Act: create_success_response関数を実行
    response_dict = create_success_response(message=test_message, data=test_data)

    # Assert: 適切な辞書形式のレスポンスが作成されることを確認
    assert response_dict["success"] is True
    assert response_dict["message"] == test_message
    assert response_dict["data"] == test_data
    assert "timestamp" in response_dict
    assert isinstance(response_dict["timestamp"], str)  # ISO形式の文字列として返される


def test_create_message_response_function():
    """create_message_response

    【正常系】メッセージレスポンス作成関数が正常に動作することを確認。
    """
    # Arrange: メッセージレスポンス作成用データを準備
    test_message = "ログアウトしました"

    # Act: create_message_response関数を実行
    response_dict = create_message_response(message=test_message)

    # Assert: 適切な辞書形式のメッセージレスポンスが作成されることを確認
    assert response_dict["success"] is True
    assert response_dict["message"] == test_message
    assert response_dict["data"]["message"] == test_message
    assert "timestamp" in response_dict


def test_create_error_response_function():
    """create_error_response

    【正常系】エラーレスポンス作成関数が正常に動作することを確認。
    """
    # Arrange: エラーレスポンス作成用データを準備
    test_message = "バリデーションエラーが発生しました"
    test_error_code = ErrorCodes.VALIDATION_ERROR
    test_details = {"field": "email", "error": "invalid format"}

    # Act: create_error_response関数を実行
    response_dict = create_error_response(message=test_message, error_code=test_error_code, details=test_details)

    # Assert: 適切な辞書形式のエラーレスポンスが作成されることを確認
    assert response_dict["success"] is False
    assert response_dict["message"] == test_message
    assert response_dict["error_code"] == test_error_code
    assert response_dict["details"] == test_details
    assert "timestamp" in response_dict


def test_error_codes_constants():
    """ErrorCodes

    【正常系】エラーコード定数が正しく定義されていることを確認。
    """
    # Arrange: エラーコード定数を確認
    # Act: 各エラーコードの値を検証
    # Assert: すべてのエラーコードが適切に定義されることを確認
    assert ErrorCodes.VALIDATION_ERROR == "VALID_001"
    assert ErrorCodes.AUTHENTICATION_FAILED == "AUTH_001"
    assert ErrorCodes.AUTHORIZATION_FAILED == "AUTH_002"
    assert ErrorCodes.RESOURCE_NOT_FOUND == "RESOURCE_001"
    assert ErrorCodes.RESOURCE_CONFLICT == "RESOURCE_003"
    assert ErrorCodes.BUSINESS_RULE_VIOLATION == "BUSINESS_001"
    assert ErrorCodes.EXTERNAL_SERVICE_ERROR == "SERVER_003"
    assert ErrorCodes.DATABASE_ERROR == "SERVER_002"
    assert ErrorCodes.INTERNAL_SERVER_ERROR == "SERVER_001"
    assert ErrorCodes.OPERATION_NOT_ALLOWED == "BUSINESS_002"


def test_base_response_with_generic_type():
    """BaseResponse

    【正常系】ジェネリック型を使用したBaseResponseが正常に動作することを確認。
    """
    # Arrange: ジェネリック型のデータを準備
    test_data = ["item1", "item2", "item3"]
    test_message = "リスト取得が完了しました"

    # Act: BaseResponseをリスト型で作成
    response = BaseResponse[list](success=True, message=test_message, data=test_data)

    # Assert: ジェネリック型が正しく動作することを確認
    assert response.success is True
    assert response.message == test_message
    assert response.data == test_data
    assert isinstance(response.data, list)
    assert len(response.data) == 3


def test_response_timestamp_japan_timezone():
    """レスポンスタイムスタンプ（日本時間）

    【正常系】レスポンスのタイムスタンプが日本時間で設定されることを確認。
    """
    # Arrange: レスポンス作成前の時刻を記録（日本時間）
    from zoneinfo import ZoneInfo

    before_creation = datetime.now(ZoneInfo("Asia/Tokyo"))

    # Act: レスポンスを作成
    response = SuccessResponse[None](message="タイムゾーンテスト")

    # Assert: タイムスタンプが適切に設定されることを確認
    after_creation = datetime.now(ZoneInfo("Asia/Tokyo"))

    assert response.timestamp >= before_creation
    assert response.timestamp <= after_creation
    # 日本時間のタイムスタンプであることを確認
    assert response.timestamp.tzinfo is not None


def test_response_serialization():
    """レスポンスシリアライゼーション

    【正常系】レスポンスオブジェクトが正しくJSON形式にシリアライズされることを確認。
    """
    # Arrange: シリアライズ用のレスポンスデータを準備
    test_data = {"key": "value", "number": 123}
    response = SuccessResponse[dict](message="シリアライズテスト", data=test_data)

    # Act: レスポンスを辞書形式に変換
    response_dict = response.model_dump()

    # Assert: 適切にシリアライズされることを確認
    assert "success" in response_dict
    assert "message" in response_dict
    assert "timestamp" in response_dict
    assert "data" in response_dict
    assert response_dict["success"] is True
    assert response_dict["message"] == "シリアライズテスト"
    assert response_dict["data"] == test_data


def test_response_validation_error():
    """レスポンスバリデーションエラー

    【異常系】必須フィールドが不足している場合にValidationErrorが発生することを確認。
    """
    # Arrange: 不正なレスポンスデータを準備（messageフィールドなし）
    # Act & Assert: ValidationErrorが発生することを確認
    with pytest.raises(ValidationError) as exc_info:
        SuccessResponse[None](success=True)  # messageフィールドが不足

    # バリデーションエラーの詳細を確認
    assert "message" in str(exc_info.value)


def test_error_response_validation():
    """ErrorResponseバリデーション

    【異常系】ErrorResponseで必須フィールドが不足している場合のエラーを確認。
    """
    # Arrange: 不正なエラーレスポンスデータを準備
    # Act & Assert: ValidationErrorが発生することを確認
    with pytest.raises(ValidationError) as exc_info:
        ErrorResponse(message="エラーメッセージ")  # error_codeフィールドが不足

    # バリデーションエラーの詳細を確認
    assert "error_code" in str(exc_info.value)


def test_response_field_descriptions():
    """レスポンスフィールド説明

    【正常系】レスポンススキーマのフィールド説明が正しく設定されていることを確認。
    """
    # Arrange: SuccessResponseのスキーマ情報を取得
    schema = SuccessResponse[dict].model_json_schema()

    # Act: フィールドの説明を検証
    # Assert: 適切なフィールド説明が設定されることを確認
    properties = schema["properties"]

    assert "description" in properties["success"]
    assert "description" in properties["message"]
    assert "description" in properties["timestamp"]
    assert "description" in properties["data"]

    # 具体的な説明文の確認
    assert "処理成功フラグ" in properties["success"]["description"]
    assert "レスポンスメッセージ" in properties["message"]["description"]
    assert "JST" in properties["timestamp"]["description"]


def test_complex_data_structure_response():
    """複雑なデータ構造のレスポンス

    【正常系】ネストした複雑なデータ構造でもレスポンスが正常に作成されることを確認。
    """
    # Arrange: 複雑なネストデータ構造を準備
    complex_data = {
        "user": {"id": "123", "profile": {"name": "テストユーザー", "settings": {"notifications": True, "theme": "dark"}}},
        "metadata": {"version": "1.0", "features": ["auth", "notifications", "analytics"]},
    }

    # Act: 複雑なデータでSuccessResponseを作成
    response = SuccessResponse[dict](message="複雑なデータ取得が完了しました", data=complex_data)

    # Assert: 複雑なデータ構造でも正しくレスポンスが作成されることを確認
    assert response.success is True
    assert response.data["user"]["profile"]["name"] == "テストユーザー"
    assert response.data["metadata"]["features"] == ["auth", "notifications", "analytics"]
    assert len(response.data["metadata"]["features"]) == 3


def test_create_empty_response_function():
    """create_empty_response

    【正常系】空データレスポンス作成関数が正常に動作することを確認。
    """
    # Arrange: 空データレスポンス作成用データを準備
    test_message = "削除が完了しました"

    # Act: create_empty_response関数を実行
    response_dict = create_empty_response(message=test_message)

    # Assert: 適切な空データレスポンスが作成されることを確認
    assert response_dict["success"] is True
    assert response_dict["message"] == test_message
    assert response_dict["data"] == {}
    assert "timestamp" in response_dict


def test_create_paginated_response_function():
    """create_paginated_response

    【正常系】ページネーション対応レスポンス作成関数が正常に動作することを確認。
    """
    # Arrange: ページネーション対応レスポンス用データを準備
    test_message = "ユーザーリスト取得が完了しました"
    test_data = [{"id": 1, "name": "user1"}, {"id": 2, "name": "user2"}]
    current_page = 1
    per_page = 10
    total_items = 25

    # Act: create_paginated_response関数を実行
    response_dict = create_paginated_response(message=test_message, data=test_data, current_page=current_page, per_page=per_page, total_items=total_items)

    # Assert: 適切なページネーション対応レスポンスが作成されることを確認
    assert response_dict["success"] is True
    assert response_dict["message"] == test_message
    assert response_dict["data"] == test_data
    assert "pagination" in response_dict

    pagination = response_dict["pagination"]
    assert pagination["current_page"] == 1
    assert pagination["per_page"] == 10
    assert pagination["total_items"] == 25
    assert pagination["total_pages"] == 3  # (25 + 10 - 1) // 10 = 3
    assert pagination["has_next"] is True  # 1 < 3
    assert pagination["has_prev"] is False  # 1 > 1


def test_pagination_meta_model():
    """PaginationMeta

    【正常系】PaginationMetaモデルが正常に動作することを確認。
    """
    # Arrange: ページネーション情報を準備
    pagination_data = {"current_page": 2, "per_page": 5, "total_items": 12, "total_pages": 3, "has_next": True, "has_prev": True}

    # Act: PaginationMetaモデルを作成
    pagination = PaginationMeta(**pagination_data)

    # Assert: すべてのフィールドが正しく設定されることを確認
    assert pagination.current_page == 2
    assert pagination.per_page == 5
    assert pagination.total_items == 12
    assert pagination.total_pages == 3
    assert pagination.has_next is True
    assert pagination.has_prev is True


def test_empty_data_model():
    """EmptyData

    【正常系】EmptyDataモデルが正常に作成されることを確認。
    """
    # Arrange: 空データモデルを準備
    # Act: EmptyDataインスタンスを作成
    empty_data = EmptyData()

    # Assert: EmptyDataが正常に作成されることを確認
    assert isinstance(empty_data, EmptyData)

    # 辞書形式に変換して空であることを確認
    empty_dict = empty_data.model_dump()
    assert empty_dict == {}


def test_paginated_response_with_empty_list():
    """create_paginated_response

    【正常系】空リストでのページネーション対応レスポンスが正常に動作することを確認。
    """
    # Arrange: 空リストのページネーション用データを準備
    test_message = "該当するアイテムが見つかりませんでした"
    test_data = []
    current_page = 1
    per_page = 10
    total_items = 0

    # Act: 空リストでcreate_paginated_response関数を実行
    response_dict = create_paginated_response(message=test_message, data=test_data, current_page=current_page, per_page=per_page, total_items=total_items)

    # Assert: 空リストでも適切なレスポンスが作成されることを確認
    assert response_dict["success"] is True
    assert response_dict["data"] == []

    pagination = response_dict["pagination"]
    assert pagination["total_items"] == 0
    assert pagination["total_pages"] == 0  # (0 + 10 - 1) // 10 = 0
    assert pagination["has_next"] is False
    assert pagination["has_prev"] is False
