from datetime import timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException

from api.v1.features.feature_auth.models.user import User
from api.v1.features.feature_auth.security import (
    authenticate_user,
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


@pytest.mark.asyncio
async def test_hash_password_not_empty():
    """hash_password

    【正常系】hash_passwordの出力が空でなく、ソルト付きハッシュが生成されることを確認。
    """
    # Arrange: テストデータの準備
    plain_password = "securepassword"

    # Act: テスト対象の実行
    hashed_password = hash_password(plain_password)
    hashed_password2 = hash_password(plain_password)

    # Assert: 結果の検証
    assert plain_password != hashed_password  # ハッシュ値が元のパスワードと異なること
    assert hashed_password != hashed_password2  # 同じ入力でもソルトにより異なるハッシュ値になること
    assert len(hashed_password) > 0  # ハッシュ値が空でないこと


@pytest.mark.asyncio
async def test_verify_password_special_case():
    """verify_password

    【正常系】特殊文字を含むパスワードの検証が正常に動作することを確認。
    """
    # Arrange: 特殊文字を含むパスワードとそのハッシュを準備
    plain_password = "特殊文字!@#$%^&*()"
    hashed_password = hash_password(plain_password)
    wrong_password = "wrongpassword"

    # Act & Assert: 正しいパスワードの検証
    assert verify_password(plain_password, hashed_password) is True

    # Act & Assert: 間違ったパスワードの検証
    assert verify_password(wrong_password, hashed_password) is False


@pytest.mark.asyncio
async def test_create_access_token_no_expiry():
    """create_access_token

    【正常系】有効期限を指定しないJWTトークンが正常に作成・デコードできることを確認。
    """
    # Arrange: トークンに含めるデータを準備
    data = {"sub": "test_user_id"}

    # Act: 有効期限なしでトークンを作成
    token = create_access_token(data=data)

    # Assert: トークンが正常にデコードできること
    decoded_data = decode_access_token(token)
    assert decoded_data["sub"] == "test_user_id"
    assert "exp" in decoded_data  # デフォルトの有効期限が設定されていること


@pytest.mark.asyncio
async def test_create_access_token_with_expiry():
    """create_access_token

    【正常系】有効期限を指定したJWTトークンが正常に作成・デコードできることを確認。
    """
    # Arrange: トークンデータと有効期限を準備
    data = {"sub": "test_user_id"}
    expires_delta = timedelta(seconds=60)

    # Act: 有効期限付きでトークンを作成
    token = create_access_token(data=data, expires_delta=expires_delta)

    # Assert: トークンが正常にデコードできること
    decoded_data = decode_access_token(token)
    assert decoded_data["sub"] == "test_user_id"
    assert "exp" in decoded_data


@pytest.mark.asyncio
async def test_create_access_token_expired():
    """create_access_token

    【異常系】期限切れのJWTトークンのデコードが適切にエラーになることを確認。
    """
    # Arrange: 既に期限切れのトークンを準備
    data = {"sub": "test_user_id"}
    expired_delta = timedelta(seconds=-1)  # 1秒前に期限切れ
    expired_token = create_access_token(data=data, expires_delta=expired_delta)

    # Act & Assert: 期限切れトークンのデコードでHTTPExceptionが発生すること
    try:
        decode_access_token(expired_token)
        raise AssertionError("Expected HTTPException was not raised")
    except HTTPException as e:
        assert e.status_code == 401
        assert "トークンが期限切れです" in str(e.detail)
    except Exception as e:
        raise AssertionError(f"Unexpected exception type: {type(e).__name__}: {e}") from e


@pytest.mark.asyncio
async def test_decode_access_token_missing_field():
    """decode_access_token

    【正常系】subフィールドが欠落したトークンも正常にデコードできることを確認。
    """
    # Arrange: subフィールド以外のデータを含むトークンを準備
    data = {"other_field": "value", "user_role": "admin"}
    token = create_access_token(data=data)

    # Act: トークンをデコード
    decoded_data = decode_access_token(token)

    # Assert: 含まれているフィールドは正しくデコードされ、subフィールドは含まれないこと
    assert "sub" not in decoded_data
    assert decoded_data["other_field"] == "value"
    assert decoded_data["user_role"] == "admin"


@pytest.mark.asyncio
async def test_decode_access_token_invalid_token():
    """decode_access_token

    【異常系】不正な形式のトークンでHTTPExceptionが発生することを確認。
    """
    # Arrange: 不正な形式のトークンを準備
    invalid_tokens = [
        "invalid.token.value",  # 不正な署名
        "",  # 空文字列
        "header.payload",  # 署名部分が欠落
        "not.a.jwt.token.at.all",  # 完全に不正な形式
    ]

    # Act & Assert: 全ての不正トークンでHTTPExceptionが発生すること
    for invalid_token in invalid_tokens:
        with pytest.raises(HTTPException) as exc_info:
            decode_access_token(invalid_token)
        assert exc_info.value.status_code == 401


@pytest.mark.asyncio
async def test_authenticate_user_success():
    """authenticate_user

    【正常系】正しい認証情報でユーザー認証が成功することを確認。
    """
    # Arrange: 正常なユーザーとモックセッションを準備
    email = "user@example.com"
    password = "correct_password"
    hashed_password = hash_password(password)
    
    mock_user = User(
        email=email,
        hashed_password=hashed_password,
        username="testuser",
        user_role=User.ROLE_FREE,
        user_status=User.STATUS_ACTIVE,
    )
    
    mock_session = AsyncMock()
    mock_result = MagicMock()
    mock_scalars = MagicMock()
    mock_scalars.first.return_value = mock_user
    mock_result.scalars.return_value = mock_scalars
    mock_session.execute.return_value = mock_result

    # Act: 認証を実行
    result = await authenticate_user(email, password, mock_session)

    # Assert: 認証が成功し、正しいユーザーが返されること
    assert result == mock_user
    assert result.email == email
    assert result.user_status == User.STATUS_ACTIVE


@pytest.mark.asyncio
async def test_authenticate_user_password_mismatch():
    """authenticate_user

    【異常系】パスワードが一致しない場合に認証が失敗することを確認。
    """
    # Arrange: 正しいパスワードでハッシュ化されたユーザーを準備
    email = "user@example.com"
    correct_password = "correct_password"
    wrong_password = "wrong_password"
    hashed_password = hash_password(correct_password)
    
    mock_user = User(
        email=email,
        hashed_password=hashed_password,
        username="testuser",
        user_role=User.ROLE_FREE,
        user_status=User.STATUS_ACTIVE,
    )
    
    mock_session = AsyncMock()
    mock_result = MagicMock()
    mock_scalars = MagicMock()
    mock_scalars.first.return_value = mock_user
    mock_result.scalars.return_value = mock_scalars
    mock_session.execute.return_value = mock_result

    # Act & Assert: 間違ったパスワードで認証を試行し、HTTPExceptionが発生すること
    with pytest.raises(HTTPException) as exc_info:
        await authenticate_user(email, wrong_password, mock_session)
    
    assert exc_info.value.status_code == 401
    assert "メールアドレスまたはパスワードが無効です" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_authenticate_user_inactive_status():
    """authenticate_user

    【異常系】非アクティブなユーザーでの認証が失敗することを確認。
    """
    # Arrange: 非アクティブユーザーは検索結果に含まれないモックを準備
    email = "inactive@example.com"
    password = "password"
    
    mock_session = AsyncMock()
    mock_result = MagicMock()
    mock_scalars = MagicMock()
    mock_scalars.first.return_value = None  # 非アクティブユーザーは取得されない
    mock_result.scalars.return_value = mock_scalars
    mock_session.execute.return_value = mock_result

    # Act & Assert: 非アクティブユーザーでの認証でHTTPExceptionが発生すること
    with pytest.raises(HTTPException) as exc_info:
        await authenticate_user(email, password, mock_session)
    
    assert exc_info.value.status_code == 401
    assert "メールアドレスまたはパスワードが無効です" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_authenticate_user_deleted():
    """authenticate_user

    【異常系】削除済みユーザーでの認証が失敗することを確認。
    """
    # Arrange: 削除済みユーザーは検索結果に含まれないモックを準備
    email = "deleted@example.com"
    password = "password"
    
    mock_session = AsyncMock()
    mock_result = MagicMock()
    mock_scalars = MagicMock()
    mock_scalars.first.return_value = None  # 削除済みユーザーは取得されない
    mock_result.scalars.return_value = mock_scalars
    mock_session.execute.return_value = mock_result

    # Act & Assert: 削除済みユーザーでの認証でHTTPExceptionが発生すること
    with pytest.raises(HTTPException) as exc_info:
        await authenticate_user(email, password, mock_session)
    
    assert exc_info.value.status_code == 401
    assert "メールアドレスまたはパスワードが無効です" in str(exc_info.value.detail)