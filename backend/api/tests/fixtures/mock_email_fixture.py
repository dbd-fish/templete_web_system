import pytest


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
