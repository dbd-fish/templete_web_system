import pytest
from unittest.mock import patch


@pytest.fixture
def mock_email_sending():
    """メール送信機能をモック化するフィクスチャ"""
    with patch("api.v1.features.feature_auth.send_verification_email.send_verification_email") as mock_verify, \
         patch("api.v1.features.feature_auth.send_reset_password_email.send_reset_password_email") as mock_reset:
        
        mock_verify.return_value = None
        mock_reset.return_value = None
        
        yield {
            "mock_verify": mock_verify,
            "mock_reset": mock_reset
        }


@pytest.fixture
def mock_smtp_settings():
    """SMTP設定をテスト用にモック化"""
    with patch.dict("os.environ", {
        "ENABLE_EMAIL_SENDING": "false",
        "SMTP_HOST": "localhost",
        "SMTP_PORT": "1025",
        "SMTP_USERNAME": "test",
        "SMTP_PASSWORD": "test"
    }):
        yield


@pytest.fixture
def enable_pytest_mode():
    """pytestモードを有効にするフィクスチャ"""
    from api.common.setting import setting
    original_pytest_mode = setting.PYTEST_MODE
    setting.PYTEST_MODE = True
    try:
        yield
    finally:
        setting.PYTEST_MODE = original_pytest_mode


@pytest.fixture
def disable_email_sending():
    """メール送信を無効化するフィクスチャ"""
    from api.common.setting import setting
    original_enable_email = setting.ENABLE_EMAIL_SENDING
    setting.ENABLE_EMAIL_SENDING = False
    try:
        yield
    finally:
        setting.ENABLE_EMAIL_SENDING = original_enable_email