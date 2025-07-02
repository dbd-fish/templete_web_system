from datetime import datetime, timedelta

import pytest
from jose import JWTError

from app.features.feature_auth.security import (
    authenticate_user,
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)
from app.models.user import User


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
    expires_delta = timedelta(seconds=1)  # 1秒の有効期限
    token = create_access_token(data=data, expires_delta=expires_delta)

    decoded_data = decode_access_token(token)
    assert decoded_data["sub"] == "test_user_id", "Token should be decodable before expiry."

    # 1秒後にトークンが無効化されることを確認
    import time
    time.sleep(2)
    with pytest.raises(JWTError, match="Signature has expired"):
        decode_access_token(token)


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
    invalid_token = "invalid.token.value"
    with pytest.raises(JWTError):
        decode_access_token(invalid_token)

    # 空文字列を渡した場合
    with pytest.raises(JWTError):
        decode_access_token("")

    # トークン形式が破損している場合
    with pytest.raises(JWTError):
        decode_access_token("header.payload")


@pytest.mark.asyncio
async def test_authenticate_user_password_mismatch(setup_test_db):
    """authenticate_userでパスワードが一致しなかった場合のテスト。
    """
    test_email = "user@example.com"
    correct_password = "securepassword"
    hashed_password = hash_password(correct_password)

    user = User(
        email=test_email,
        hashed_password=hashed_password,
        username="testuser",
        user_role=User.ROLE_FREE,
        user_status=User.STATUS_ACTIVE,
    )
    override_get_db = setup_test_db["override_get_db"]  # 関数を取得
    async for db_session in override_get_db():
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        # 間違ったパスワードを使用して認証
        with pytest.raises(Exception, match="Invalid email or password"):
            await authenticate_user(test_email, "wrongpassword", db_session)


@pytest.mark.asyncio
async def test_authenticate_user_inactive_status(setup_test_db):
    """authenticate_userで非アクティブなユーザーをテスト。
    """
    test_email = "inactiveuser@example.com"
    test_password = "securepassword"
    hashed_password = hash_password(test_password)

    user = User(
        email=test_email,
        hashed_password=hashed_password,
        username="inactiveuser",
        user_role=User.ROLE_FREE,
        user_status=User.STATUS_SUSPENDED,  # 非アクティブなステータス
    )
    override_get_db = setup_test_db["override_get_db"]  # 関数を取得
    async for db_session in override_get_db():
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        with pytest.raises(Exception, match="Invalid email or password"):
            await authenticate_user(test_email, test_password, db_session)


@pytest.mark.asyncio
async def test_authenticate_user_deleted(setup_test_db):
    """authenticate_userで削除済みのユーザーをテスト。
    """
    test_email = "deleteduser@example.com"
    test_password = "securepassword"
    hashed_password = hash_password(test_password)

    user = User(
        email=test_email,
        hashed_password=hashed_password,
        username="deleteduser",
        user_role=User.ROLE_FREE,
        user_status=User.STATUS_ACTIVE,
        deleted_at= datetime.strptime("2024-01-01 00:00:00", "%Y-%m-%d %H:%M:%S"),  # 削除されたユーザー
    )
    override_get_db = setup_test_db["override_get_db"]  # 関数を取得
    async for db_session in override_get_db():
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        with pytest.raises(Exception, match="Invalid email or password"):
            await authenticate_user(test_email, test_password, db_session)
