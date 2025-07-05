"""
CRUD操作の単体テスト（AAAパターン）
"""

import uuid
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException

from api.common.test_data import TestData
from api.v1.features.feature_auth.crud import (
    create_user,
    create_user_service,
    decode_password_reset_token,
    delete_user,
    get_current_user,
    get_user_by_email,
    get_user_by_email_including_deleted,
    get_user_by_id,
    get_user_by_username,
    reset_password,
    reset_password_email,
    restore_user,
    update_user_password,
    update_user_profile,
    update_user_with_schema,
    verify_email_token,
)
from api.v1.features.feature_auth.models.user import User
from api.v1.features.feature_auth.schemas.user import UserCreate, UserUpdate


@pytest.mark.asyncio
async def test_get_user_by_email_found():
    """get_user_by_email

    【正常系】アクティブなユーザーが正常に取得できることを確認。
    """
    # Arrange: モックユーザーとセッションを準備
    mock_user = User(
        email=TestData.TEST_USER_EMAIL_1,
        username=TestData.DOC_USERNAME_EXAMPLE,
        hashed_password="hashed_password",
        user_role=User.ROLE_FREE,
        user_status=User.STATUS_ACTIVE,
    )

    mock_session = AsyncMock()
    mock_result = MagicMock()
    mock_scalars = MagicMock()
    mock_scalars.first.return_value = mock_user
    mock_result.scalars.return_value = mock_scalars
    mock_session.execute.return_value = mock_result

    # Act: メールアドレスでユーザー検索を実行
    result = await get_user_by_email(mock_session, TestData.TEST_USER_EMAIL_1)

    # Assert: 正しいユーザーが取得されることを確認
    assert result == mock_user
    assert result.email == TestData.TEST_USER_EMAIL_1
    assert result.user_status == User.STATUS_ACTIVE


@pytest.mark.asyncio
async def test_get_user_by_email_not_found():
    """get_user_by_email

    【正常系】存在しないメールアドレスでNoneが返されることを確認。
    """
    # Arrange: ユーザーが見つからない場合のモックセッションを準備
    mock_session = AsyncMock()
    mock_result = MagicMock()
    mock_scalars = MagicMock()
    mock_scalars.first.return_value = None
    mock_result.scalars.return_value = mock_scalars
    mock_session.execute.return_value = mock_result

    # Act: 存在しないメールアドレスでユーザー検索を実行
    result = await get_user_by_email(mock_session, TestData.TEST_NONEXISTENT_EMAIL)

    # Assert: Noneが返されることを確認
    assert result is None


@pytest.mark.asyncio
async def test_get_user_by_email_including_deleted_found():
    """get_user_by_email_including_deleted

    【正常系】論理削除済みユーザーも含めて取得できることを確認。
    """
    # Arrange: 論理削除済みユーザーのモックを準備
    mock_deleted_user = User(
        email=TestData.TEST_USER_EMAIL_1,
        username=TestData.TEST_DELETED_USERNAME,
        hashed_password="hashed_password",
        user_role=User.ROLE_FREE,
        user_status=User.STATUS_SUSPENDED,
        deleted_at=datetime.now(),
    )

    mock_session = AsyncMock()
    mock_result = MagicMock()
    mock_scalars = MagicMock()
    mock_scalars.first.return_value = mock_deleted_user
    mock_result.scalars.return_value = mock_scalars
    mock_session.execute.return_value = mock_result

    # Act: 論理削除済みユーザーを含む検索を実行
    result = await get_user_by_email_including_deleted(mock_session, TestData.TEST_USER_EMAIL_1)

    # Assert: 論理削除済みユーザーが取得されることを確認
    assert result == mock_deleted_user
    assert result.email == TestData.TEST_USER_EMAIL_1
    assert result.deleted_at is not None


@pytest.mark.asyncio
async def test_get_user_by_username_found():
    """get_user_by_username

    【正常系】ユーザー名で正常にユーザーが取得できることを確認。
    """
    # Arrange: モックユーザーとセッションを準備
    mock_user = User(
        email=TestData.TEST_USER_EMAIL_1,
        username=TestData.DOC_USERNAME_EXAMPLE,
        hashed_password="hashed_password",
        user_role=User.ROLE_FREE,
        user_status=User.STATUS_ACTIVE,
    )

    mock_session = AsyncMock()
    mock_result = MagicMock()
    mock_scalars = MagicMock()
    mock_scalars.first.return_value = mock_user
    mock_result.scalars.return_value = mock_scalars
    mock_session.execute.return_value = mock_result

    # Act: ユーザー名でユーザー検索を実行
    result = await get_user_by_username(mock_session, TestData.DOC_USERNAME_EXAMPLE)

    # Assert: 正しいユーザーが取得されることを確認
    assert result == mock_user
    assert result.username == TestData.DOC_USERNAME_EXAMPLE


@pytest.mark.asyncio
async def test_get_user_by_id_found():
    """get_user_by_id

    【正常系】ユーザーIDで正常にユーザーが取得できることを確認。
    """
    # Arrange: モックユーザーとセッションを準備
    test_user_id = str(uuid.uuid4())
    mock_user = User(
        user_id=test_user_id,
        email=TestData.TEST_USER_EMAIL_1,
        username=TestData.DOC_USERNAME_EXAMPLE,
        hashed_password="hashed_password",
        user_role=User.ROLE_FREE,
        user_status=User.STATUS_ACTIVE,
    )

    mock_session = AsyncMock()
    mock_result = MagicMock()
    mock_scalars = MagicMock()
    mock_scalars.first.return_value = mock_user
    mock_result.scalars.return_value = mock_scalars
    mock_session.execute.return_value = mock_result

    # Act: ユーザーIDでユーザー検索を実行
    result = await get_user_by_id(mock_session, test_user_id)

    # Assert: 正しいユーザーが取得されることを確認
    assert result == mock_user
    assert str(result.user_id) == test_user_id


@pytest.mark.asyncio
async def test_create_user_success():
    """create_user

    【正常系】新しいユーザーが正常に作成されることを確認。
    """
    # Arrange: 新しいユーザーオブジェクトとモックセッションを準備
    new_user = User(
        email=TestData.TEST_USER_EMAIL_1,
        username=TestData.DOC_NEW_USERNAME,
        hashed_password="hashed_password",
        user_role=User.ROLE_FREE,
        user_status=User.STATUS_ACTIVE,
    )

    mock_session = AsyncMock()
    mock_session.add = MagicMock()
    mock_session.commit = AsyncMock()
    mock_session.refresh = AsyncMock()

    # Act: ユーザー作成を実行
    result = await create_user(mock_session, new_user)

    # Assert: ユーザーが正常に作成されることを確認
    assert result == new_user
    mock_session.add.assert_called_once_with(new_user)
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once_with(new_user)


@pytest.mark.asyncio
async def test_update_user_password_success():
    """update_user_password

    【正常系】ユーザーのパスワードが正常に更新されることを確認。
    """
    # Arrange: 既存ユーザーと新しいハッシュパスワードを準備
    existing_user = User(
        email=TestData.TEST_USER_EMAIL_1,
        username=TestData.DOC_USERNAME_EXAMPLE,
        hashed_password="old_password_hash",
        user_role=User.ROLE_FREE,
        user_status=User.STATUS_ACTIVE,
    )
    new_hashed_password = "new_password_hash"

    mock_session = AsyncMock()
    mock_session.commit = AsyncMock()
    mock_session.refresh = AsyncMock()

    # Act: パスワード更新を実行
    result = await update_user_password(mock_session, existing_user, new_hashed_password)

    # Assert: パスワードが正常に更新されることを確認
    assert result.hashed_password == new_hashed_password
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once_with(existing_user)


@pytest.mark.asyncio
async def test_update_user_profile_partial_update():
    """update_user_profile

    【正常系】ユーザープロフィールの部分更新が正常に動作することを確認。
    """
    # Arrange: 既存ユーザーと更新データを準備
    existing_user = User(
        email=TestData.TEST_USER_EMAIL_1,
        username=TestData.TEST_OLD_USERNAME,
        hashed_password="hashed_password",
        user_role=User.ROLE_FREE,
        user_status=User.STATUS_ACTIVE,
        contact_number=None,
    )

    mock_session = AsyncMock()
    mock_session.commit = AsyncMock()
    mock_session.refresh = AsyncMock()

    # Act: ユーザー名と連絡先のみ更新を実行
    result = await update_user_profile(mock_session, existing_user, username=TestData.TEST_NEW_USERNAME, contact_number=TestData.DOC_CONTACT_NUMBER)

    # Assert: 指定したフィールドのみ更新されることを確認
    assert result.username == TestData.TEST_NEW_USERNAME
    assert result.contact_number == TestData.DOC_CONTACT_NUMBER
    assert result.email == TestData.TEST_USER_EMAIL_1  # 変更されていないことを確認
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once_with(existing_user)


@pytest.mark.asyncio
async def test_delete_user_success():
    """delete_user

    【正常系】ユーザーが正常に論理削除されることを確認。
    """
    # Arrange: アクティブなユーザーとモックセッションを準備
    active_user = User(
        email=TestData.TEST_USER_EMAIL_1,
        username=TestData.DOC_USERNAME_EXAMPLE,
        hashed_password="hashed_password",
        user_role=User.ROLE_FREE,
        user_status=User.STATUS_ACTIVE,
        deleted_at=None,
    )

    mock_session = AsyncMock()
    mock_session.commit = AsyncMock()
    mock_session.refresh = AsyncMock()

    # Act: ユーザー論理削除を実行
    result = await delete_user(mock_session, active_user)

    # Assert: 論理削除が正常に実行されることを確認
    assert result.user_status == User.STATUS_SUSPENDED
    assert result.deleted_at is not None
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once_with(active_user)


@pytest.mark.asyncio
async def test_restore_user_success():
    """restore_user

    【正常系】論理削除済みユーザーが正常に復活されることを確認。
    """
    # Arrange: 論理削除済みユーザーと復活用データを準備
    deleted_user = User(
        email=TestData.TEST_USER_EMAIL_1,
        username=TestData.TEST_DELETED_USERNAME,
        hashed_password="old_password_hash",
        user_role=User.ROLE_FREE,
        user_status=User.STATUS_SUSPENDED,
        deleted_at=datetime.now(),
    )

    mock_session = AsyncMock()
    mock_session.commit = AsyncMock()
    mock_session.refresh = AsyncMock()

    # Act: ユーザー復活を実行
    result = await restore_user(mock_session, deleted_user, TestData.TEST_RESTORED_USERNAME, TestData.TEST_NEW_PASSWORD)

    # Assert: ユーザーが正常に復活されることを確認
    assert result.username == TestData.TEST_RESTORED_USERNAME
    assert result.user_status == User.STATUS_ACTIVE
    assert result.deleted_at is None
    assert result.hashed_password != "old_password_hash"  # パスワードが更新されている
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once_with(deleted_user)


@pytest.mark.asyncio
async def test_get_current_user_success():
    """get_current_user

    【正常系】有効なトークンから現在のユーザーが正常に取得できることを確認。
    """
    # Arrange: 有効なトークンとユーザーのモックを準備
    mock_request = MagicMock()
    mock_request.cookies.get.return_value = "valid_token"

    mock_user = User(
        email=TestData.TEST_USER_EMAIL_1,
        username=TestData.DOC_USERNAME_EXAMPLE,
        hashed_password="hashed_password",
        user_role=User.ROLE_FREE,
        user_status=User.STATUS_ACTIVE,
    )

    mock_session = AsyncMock()

    # Act & Assert: トークンデコードとユーザー取得をモック化して実行
    with patch("api.v1.features.feature_auth.crud.decode_access_token") as mock_decode, patch("api.v1.features.feature_auth.crud.get_user_by_email") as mock_get_user:
        mock_decode.return_value = {"sub": TestData.TEST_USER_EMAIL_1}
        mock_get_user.return_value = mock_user

        result = await get_current_user(mock_request, mock_session)

        assert result == mock_user
        mock_decode.assert_called_once_with("valid_token")
        mock_get_user.assert_called_once_with(mock_session, email=TestData.TEST_USER_EMAIL_1)


@pytest.mark.asyncio
async def test_get_current_user_no_token():
    """get_current_user

    【異常系】トークンが存在しない場合にHTTPExceptionが発生することを確認。
    """
    # Arrange: トークンが存在しないリクエストを準備
    mock_request = MagicMock()
    mock_request.cookies.get.return_value = None
    mock_session = AsyncMock()

    # Act & Assert: 認証エラーが発生することを確認
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(mock_request, mock_session)

    assert exc_info.value.status_code == 401
    assert "認証情報が無効です" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_create_user_service_new_user():
    """create_user_service

    【正常系】新規ユーザーが正常に作成されることを確認。
    """
    # Arrange: 新規ユーザー情報とモックセッションを準備
    email = TestData.DOC_NEW_USER_EMAIL
    username = TestData.DOC_NEW_USERNAME
    password = TestData.DOC_PASSWORD_EXAMPLE

    mock_session = AsyncMock()

    # Act & Assert: 既存ユーザーチェックとユーザー作成をモック化して実行
    with patch("api.v1.features.feature_auth.crud.get_user_by_email_including_deleted") as mock_get_existing, patch("api.v1.features.feature_auth.crud.create_user") as mock_create:
        mock_get_existing.return_value = None  # 既存ユーザーなし

        created_user = User(
            email=email,
            username=username,
            user_role=User.ROLE_FREE,
            user_status=User.STATUS_ACTIVE,
        )
        mock_create.return_value = created_user

        result = await create_user_service(email, username, password, mock_session)

        assert result == created_user
        mock_get_existing.assert_called_once_with(mock_session, email)
        mock_create.assert_called_once()


@pytest.mark.asyncio
async def test_create_user_service_restore_deleted_user():
    """create_user_service

    【正常系】論理削除済みユーザーの復活が正常に動作することを確認。
    """
    # Arrange: 論理削除済みユーザーと復活用データを準備
    email = TestData.TEST_USER_EMAIL_1
    username = TestData.TEST_RESTORED_USERNAME
    password = TestData.TEST_NEW_PASSWORD

    deleted_user = User(
        email=email,
        username=TestData.TEST_OLD_USERNAME,
        user_status=User.STATUS_SUSPENDED,
        deleted_at=datetime.now(),
    )

    mock_session = AsyncMock()

    # Act & Assert: 削除済みユーザーの復活をモック化して実行
    with patch("api.v1.features.feature_auth.crud.get_user_by_email_including_deleted") as mock_get_existing, patch("api.v1.features.feature_auth.crud.restore_user") as mock_restore:
        mock_get_existing.return_value = deleted_user

        restored_user = User(
            email=email,
            username=username,
            user_status=User.STATUS_ACTIVE,
            deleted_at=None,
        )
        mock_restore.return_value = restored_user

        result = await create_user_service(email, username, password, mock_session)

        assert result == restored_user
        mock_restore.assert_called_once_with(mock_session, deleted_user, username, password)


@pytest.mark.asyncio
async def test_create_user_service_user_already_exists():
    """create_user_service

    【異常系】アクティブなユーザーが既に存在する場合にHTTPExceptionが発生することを確認。
    """
    # Arrange: 既存のアクティブユーザーを準備
    email = TestData.TEST_USER_EMAIL_1
    username = TestData.DOC_USERNAME_EXAMPLE
    password = TestData.DOC_PASSWORD_EXAMPLE

    existing_user = User(
        email=email,
        username=TestData.TEST_EXISTING_USERNAME,
        user_status=User.STATUS_ACTIVE,
        deleted_at=None,
    )

    mock_session = AsyncMock()

    # Act & Assert: 重複ユーザーエラーが発生することを確認
    with patch("api.v1.features.feature_auth.crud.get_user_by_email_including_deleted") as mock_get_existing:
        mock_get_existing.return_value = existing_user

        with pytest.raises(HTTPException) as exc_info:
            await create_user_service(email, username, password, mock_session)

        assert exc_info.value.status_code == 409
        assert "このメールアドレスは既に使用されています" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_verify_email_token_success():
    """verify_email_token

    【正常系】有効なメール認証トークンが正常にデコードされることを確認。
    """
    # Arrange: 有効なトークンペイロードを準備
    token = "valid_email_token"

    # Act & Assert: トークンデコードをモック化して実行
    with patch("api.v1.features.feature_auth.crud.decode_access_token") as mock_decode:
        mock_decode.return_value = {"email": TestData.TEST_USER_EMAIL_1, "username": TestData.DOC_USERNAME_EXAMPLE, "password": TestData.DOC_PASSWORD_EXAMPLE}

        result = await verify_email_token(token)

        assert isinstance(result, UserCreate)
        assert result.email == TestData.TEST_USER_EMAIL_1
        assert result.username == TestData.DOC_USERNAME_EXAMPLE
        assert result.password == TestData.DOC_PASSWORD_EXAMPLE


@pytest.mark.asyncio
async def test_verify_email_token_invalid_token():
    """verify_email_token

    【異常系】無効なメール認証トークンでHTTPExceptionが発生することを確認。
    """
    # Arrange: 無効なトークンを準備
    token = "invalid_token"

    # Act & Assert: 無効トークンエラーが発生することを確認
    with patch("api.v1.features.feature_auth.crud.decode_access_token") as mock_decode:
        mock_decode.side_effect = Exception("Invalid token")

        with pytest.raises(HTTPException) as exc_info:
            await verify_email_token(token)

        assert exc_info.value.status_code == 400
        assert "無効な認証トークンです" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_reset_password_email_success():
    """reset_password_email

    【正常系】パスワードリセットメールが正常に送信されることを確認。
    """
    # Arrange: 有効なユーザーとバックグラウンドタスクを準備
    email = TestData.TEST_USER_EMAIL_1
    mock_user = User(
        email=email,
        username=TestData.DOC_USERNAME_EXAMPLE,
        user_status=User.STATUS_ACTIVE,
    )

    mock_background_tasks = MagicMock()
    mock_session = AsyncMock()

    # Act & Assert: ユーザー検索とメール送信をモック化して実行
    with patch("api.v1.features.feature_auth.crud.get_user_by_email") as mock_get_user, patch("api.v1.features.feature_auth.crud.create_access_token") as mock_create_token:
        mock_get_user.return_value = mock_user
        mock_create_token.return_value = "reset_token"

        await reset_password_email(email, mock_background_tasks, mock_session)

        mock_get_user.assert_called_once_with(mock_session, email)
        mock_background_tasks.add_task.assert_called_once()


@pytest.mark.asyncio
async def test_reset_password_email_user_not_found():
    """reset_password_email

    【異常系】存在しないユーザーでHTTPExceptionが発生することを確認。
    """
    # Arrange: 存在しないユーザーのメールアドレスを準備
    email = TestData.TEST_NONEXISTENT_EMAIL
    mock_background_tasks = MagicMock()
    mock_session = AsyncMock()

    # Act & Assert: ユーザー未発見エラーが発生することを確認
    with patch("api.v1.features.feature_auth.crud.get_user_by_email") as mock_get_user:
        mock_get_user.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            await reset_password_email(email, mock_background_tasks, mock_session)

        assert exc_info.value.status_code == 404
        assert "指定されたメールアドレスのユーザーが見つかりません" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_decode_password_reset_token_success():
    """decode_password_reset_token

    【正常系】有効なパスワードリセットトークンが正常にデコードされることを確認。
    """
    # Arrange: 有効なトークンを準備
    token = "valid_reset_token"

    # Act & Assert: トークンデコードをモック化して実行
    with patch("api.v1.features.feature_auth.crud.decode_access_token") as mock_decode:
        mock_decode.return_value = {"email": TestData.TEST_USER_EMAIL_1}

        result = await decode_password_reset_token(token)

        assert result == TestData.TEST_USER_EMAIL_1


@pytest.mark.asyncio
async def test_decode_password_reset_token_invalid():
    """decode_password_reset_token

    【異常系】無効なパスワードリセットトークンでHTTPExceptionが発生することを確認。
    """
    # Arrange: 無効なトークンを準備
    token = "invalid_reset_token"

    # Act & Assert: 無効トークンエラーが発生することを確認
    with patch("api.v1.features.feature_auth.crud.decode_access_token") as mock_decode:
        mock_decode.side_effect = Exception("Invalid token")

        with pytest.raises(HTTPException) as exc_info:
            await decode_password_reset_token(token)

        assert exc_info.value.status_code == 400
        assert "無効なリセットトークンです" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_reset_password_success():
    """reset_password

    【正常系】パスワードリセットが正常に実行されることを確認。
    """
    # Arrange: 有効なユーザーと新しいパスワードを準備
    email = TestData.TEST_USER_EMAIL_1
    new_password = TestData.TEST_RESET_NEW_PASSWORD

    mock_user = User(
        email=email,
        username=TestData.DOC_USERNAME_EXAMPLE,
        user_status=User.STATUS_ACTIVE,
    )

    mock_session = AsyncMock()

    # Act & Assert: ユーザー検索とパスワード更新をモック化して実行
    with patch("api.v1.features.feature_auth.crud.get_user_by_email") as mock_get_user, patch("api.v1.features.feature_auth.crud.update_user_password") as mock_update_password:
        mock_get_user.return_value = mock_user

        await reset_password(email, new_password, mock_session)

        mock_get_user.assert_called_once_with(mock_session, email)
        mock_update_password.assert_called_once()


@pytest.mark.asyncio
async def test_reset_password_user_not_found():
    """reset_password

    【異常系】存在しないユーザーでHTTPExceptionが発生することを確認。
    """
    # Arrange: 存在しないユーザーのデータを準備
    email = TestData.TEST_NONEXISTENT_EMAIL
    new_password = TestData.TEST_RESET_NEW_PASSWORD
    mock_session = AsyncMock()

    # Act & Assert: ユーザー未発見エラーが発生することを確認
    with patch("api.v1.features.feature_auth.crud.get_user_by_email") as mock_get_user:
        mock_get_user.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            await reset_password(email, new_password, mock_session)

        assert exc_info.value.status_code == 404
        assert "ユーザーが見つかりません" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_update_user_with_schema_success():
    """update_user_with_schema

    【正常系】UserUpdateスキーマを使ったユーザー更新が正常に動作することを確認。
    """
    # Arrange: 既存ユーザーと更新スキーマを準備
    existing_user = User(
        email=TestData.TEST_USER_EMAIL_1,
        username=TestData.TEST_OLD_USERNAME,
        user_status=User.STATUS_ACTIVE,
    )

    user_update = UserUpdate(username=TestData.TEST_NEW_USERNAME, contact_number=TestData.DOC_CONTACT_NUMBER)

    mock_session = AsyncMock()

    # Act & Assert: プロフィール更新をモック化して実行
    with patch("api.v1.features.feature_auth.crud.update_user_profile") as mock_update_profile:
        updated_user = User(
            email=TestData.TEST_USER_EMAIL_1,
            username=TestData.TEST_NEW_USERNAME,
            contact_number=TestData.DOC_CONTACT_NUMBER,
            user_status=User.STATUS_ACTIVE,
        )
        mock_update_profile.return_value = updated_user

        result = await update_user_with_schema(mock_session, existing_user, user_update)

        assert result == updated_user
        mock_update_profile.assert_called_once_with(
            db=mock_session,
            user=existing_user,
            username=TestData.TEST_NEW_USERNAME,
            email=None,
            contact_number=TestData.DOC_CONTACT_NUMBER,
            date_of_birth=None
        )
