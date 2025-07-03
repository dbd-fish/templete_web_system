from datetime import datetime, timedelta

import pytest
from jwt.exceptions import InvalidTokenError as JWTError

from api.v1.features.feature_auth.security import (
    authenticate_user,
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)
from api.v1.features.feature_auth.models.user import User


@pytest.mark.asyncio
async def test_hash_password_not_empty():
    """hash_passwordの出力が空でないことを確認。
    """
    plain_password = "securepassword"
    hashed_password = hash_password(plain_password)

    # ハッシュ値が元のパスワードと異なること
    assert plain_password != hashed_password

    # 同じ入力でハッシュ値が異なること（ソルトが適用されているか確認）
    hashed_password2 = hash_password(plain_password)
    assert hashed_password != hashed_password2


@pytest.mark.asyncio
async def test_verify_password_special_case():
    """verify_passwordの特殊ケースをテスト。
    """
    plain_password = "特殊文字!@#$%^&*()"
    hashed_password = hash_password(plain_password)

    assert verify_password(plain_password, hashed_password), "Password with special characters should be verified successfully."

    # 不一致のパスワードを検証
    assert not verify_password("wrongpassword", hashed_password), "Mismatched password should not be verified."


@pytest.mark.asyncio
async def test_create_access_token_no_expiry():
    """create_access_tokenで有効期限を指定しないケースをテスト。
    """
    data = {"sub": "test_user_id"}
    token = create_access_token(data=data)

    decoded_data = decode_access_token(token)
    assert decoded_data["sub"] == "test_user_id", "Token without expiry should be decodable."


@pytest.mark.asyncio
async def test_create_access_token_expiry():
    """create_access_tokenで有効期限を指定するケースをテスト。
    """
    data = {"sub": "test_user_id"}
    
    # 正常な期限内トークンのテスト
    expires_delta = timedelta(seconds=60)  # 60秒の有効期限
    token = create_access_token(data=data, expires_delta=expires_delta)
    decoded_data = decode_access_token(token)
    assert decoded_data["sub"] == "test_user_id", "Token should be decodable within expiry time."
    
    # 既に期限切れのトークンのテスト
    expired_token = create_access_token(data=data, expires_delta=timedelta(seconds=-1))
    with pytest.raises(Exception):  # PyJWTでは異なる例外が発生する場合がある
        decode_access_token(expired_token)


@pytest.mark.asyncio
async def test_decode_access_token_missing_field():
    """decode_access_tokenでトークンからsubフィールドが欠落しているケースをテスト。
    """
    data = {"other_field": "value"}
    token = create_access_token(data=data)

    decoded_data = decode_access_token(token)

    # トークンに 'sub' フィールドが含まれていない場合、デコード結果にも含まれていないことを確認
    assert "sub" not in decoded_data
    # トークンに含まれているフィールド 'other_field' が正しくデコードされていることを確認
    assert decoded_data["other_field"] == "value"


@pytest.mark.asyncio
async def test_decode_access_token_invalid_token():
    """jwtとして不適切なトークンをdecode_access_tokenに渡した場合のテスト。
    """
    from fastapi import HTTPException
    
    invalid_token = "invalid.token.value"
    with pytest.raises(HTTPException):
        decode_access_token(invalid_token)

    # 空文字列を渡した場合
    with pytest.raises(HTTPException):
        decode_access_token("")

    # トークン形式が破損している場合
    with pytest.raises(HTTPException):
        decode_access_token("header.payload")


@pytest.mark.asyncio
async def test_authenticate_user_password_mismatch():
    """authenticate_userでパスワードが一致しなかった場合のテスト。
    """
    from unittest.mock import AsyncMock, MagicMock
    from fastapi import HTTPException
    
    # モックセッションの作成
    mock_session = AsyncMock()
    mock_result = MagicMock()
    mock_scalars = MagicMock()
    mock_user = User(
        email="user@example.com",
        hashed_password=hash_password("correct_password"),
        username="testuser",
        user_role=User.ROLE_FREE,
        user_status=User.STATUS_ACTIVE,
    )
    mock_scalars.first.return_value = mock_user
    mock_result.scalars.return_value = mock_scalars
    mock_session.execute.return_value = mock_result

    # 間違ったパスワードを使用して認証
    with pytest.raises(HTTPException) as exc_info:
        await authenticate_user("user@example.com", "wrongpassword", mock_session)
    
    assert exc_info.value.status_code == 401
    assert "メールアドレスまたはパスワードが無効です" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_authenticate_user_inactive_status():
    """authenticate_userで非アクティブなユーザーをテスト。
    """
    from unittest.mock import AsyncMock, MagicMock
    from fastapi import HTTPException
    
    # モックセッションの作成
    mock_session = AsyncMock()
    mock_result = MagicMock()
    mock_scalars = MagicMock()
    mock_scalars.first.return_value = None  # 非アクティブユーザーは取得されない
    mock_result.scalars.return_value = mock_scalars
    mock_session.execute.return_value = mock_result

    # 非アクティブなユーザーで認証
    with pytest.raises(HTTPException) as exc_info:
        await authenticate_user("inactiveuser@example.com", "securepassword", mock_session)
    
    assert exc_info.value.status_code == 401
    assert "メールアドレスまたはパスワードが無効です" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_authenticate_user_deleted():
    """authenticate_userで削除済みのユーザーをテスト。
    """
    from unittest.mock import AsyncMock, MagicMock
    from fastapi import HTTPException
    
    # モックセッションの作成
    mock_session = AsyncMock()
    mock_result = MagicMock()
    mock_scalars = MagicMock()
    mock_scalars.first.return_value = None  # 削除済みユーザーは取得されない
    mock_result.scalars.return_value = mock_scalars
    mock_session.execute.return_value = mock_result

    # 削除済みユーザーで認証
    with pytest.raises(HTTPException) as exc_info:
        await authenticate_user("deleteduser@example.com", "securepassword", mock_session)
    
    assert exc_info.value.status_code == 401
    assert "メールアドレスまたはパスワードが無効です" in str(exc_info.value.detail)
