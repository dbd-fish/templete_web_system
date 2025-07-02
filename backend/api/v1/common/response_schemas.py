"""
統一レスポンススキーマ定義

全APIエンドポイントで使用する標準的なレスポンス形式を定義
"""

from datetime import datetime
from typing import Any, Generic, TypeVar, Optional
from pydantic import BaseModel, Field
from zoneinfo import ZoneInfo

DataT = TypeVar('DataT')


class BaseResponse(BaseModel, Generic[DataT]):
    """
    基本レスポンス形式
    
    すべてのAPIレスポンスで使用する共通フィールドを定義
    """
    success: bool = Field(..., description="処理成功フラグ")
    message: str = Field(..., description="レスポンスメッセージ")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(ZoneInfo("Asia/Tokyo")),
        description="レスポンス生成時刻 (JST)"
    )
    data: Optional[DataT] = Field(None, description="レスポンスデータ")


class SuccessResponse(BaseResponse[DataT]):
    """
    成功レスポンス
    
    API処理が正常に完了した場合のレスポンス形式
    """
    success: bool = Field(True, description="処理成功フラグ (常にTrue)")


class ErrorResponse(BaseModel):
    """
    エラーレスポンス
    
    API処理でエラーが発生した場合のレスポンス形式
    """
    success: bool = Field(False, description="処理成功フラグ (常にFalse)")
    message: str = Field(..., description="エラーメッセージ")
    error_code: str = Field(..., description="エラーコード")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(ZoneInfo("Asia/Tokyo")),
        description="エラー発生時刻 (JST)"
    )
    details: Optional[dict[str, Any]] = Field(None, description="エラー詳細情報")


class PaginationMeta(BaseModel):
    """
    ページネーション情報
    
    リスト取得APIで使用するページネーション情報
    """
    current_page: int = Field(..., description="現在のページ番号")
    per_page: int = Field(..., description="1ページあたりのアイテム数")
    total_items: int = Field(..., description="総アイテム数")
    total_pages: int = Field(..., description="総ページ数")
    has_next: bool = Field(..., description="次のページが存在するか")
    has_prev: bool = Field(..., description="前のページが存在するか")


class PaginatedResponse(SuccessResponse[list[DataT]]):
    """
    ページネーション対応レスポンス
    
    リスト取得APIで使用するページネーション対応レスポンス
    """
    pagination: PaginationMeta = Field(..., description="ページネーション情報")


# 便利な型エイリアス
SuccessResponseDict = SuccessResponse[dict[str, Any]]
SuccessResponseList = SuccessResponse[list[dict[str, Any]]]
SuccessResponseStr = SuccessResponse[str]
SuccessResponseInt = SuccessResponse[int]
SuccessResponseBool = SuccessResponse[bool]


def create_success_response(
    message: str,
    data: Any = None
) -> dict[str, Any]:
    """
    成功レスポンスを作成するヘルパー関数
    
    Args:
        message: 成功メッセージ
        data: レスポンスデータ (オプション)
        
    Returns:
        dict: 成功レスポンス辞書
    """
    return {
        "success": True,
        "message": message,
        "timestamp": datetime.now(ZoneInfo("Asia/Tokyo")),
        "data": data
    }


def create_error_response(
    message: str,
    error_code: str,
    details: Optional[dict[str, Any]] = None
) -> dict[str, Any]:
    """
    エラーレスポンスを作成するヘルパー関数
    
    Args:
        message: エラーメッセージ
        error_code: エラーコード
        details: エラー詳細情報 (オプション)
        
    Returns:
        dict: エラーレスポンス辞書
    """
    return {
        "success": False,
        "message": message,
        "error_code": error_code,
        "timestamp": datetime.now(ZoneInfo("Asia/Tokyo")),
        "details": details
    }


def create_paginated_response(
    message: str,
    data: list[Any],
    current_page: int,
    per_page: int,
    total_items: int
) -> dict[str, Any]:
    """
    ページネーション対応レスポンスを作成するヘルパー関数
    
    Args:
        message: 成功メッセージ
        data: リストデータ
        current_page: 現在のページ番号
        per_page: 1ページあたりのアイテム数
        total_items: 総アイテム数
        
    Returns:
        dict: ページネーション対応レスポンス辞書
    """
    total_pages = (total_items + per_page - 1) // per_page
    
    return {
        "success": True,
        "message": message,
        "timestamp": datetime.now(ZoneInfo("Asia/Tokyo")),
        "data": data,
        "pagination": {
            "current_page": current_page,
            "per_page": per_page,
            "total_items": total_items,
            "total_pages": total_pages,
            "has_next": current_page < total_pages,
            "has_prev": current_page > 1
        }
    }


# エラーコード定数
class ErrorCodes:
    """
    標準エラーコード定義
    """
    # 認証・認可エラー
    AUTHENTICATION_FAILED = "AUTH_001"
    AUTHORIZATION_FAILED = "AUTH_002"
    TOKEN_EXPIRED = "AUTH_003"
    TOKEN_INVALID = "AUTH_004"
    
    # バリデーションエラー
    VALIDATION_ERROR = "VALID_001"
    REQUIRED_FIELD_MISSING = "VALID_002"
    INVALID_FORMAT = "VALID_003"
    
    # リソースエラー
    RESOURCE_NOT_FOUND = "RESOURCE_001"
    RESOURCE_ALREADY_EXISTS = "RESOURCE_002"
    RESOURCE_CONFLICT = "RESOURCE_003"
    
    # サーバーエラー
    INTERNAL_SERVER_ERROR = "SERVER_001"
    DATABASE_ERROR = "SERVER_002"
    EXTERNAL_SERVICE_ERROR = "SERVER_003"
    
    # ビジネスロジックエラー
    BUSINESS_RULE_VIOLATION = "BUSINESS_001"
    OPERATION_NOT_ALLOWED = "BUSINESS_002"
    INSUFFICIENT_PERMISSIONS = "BUSINESS_003"