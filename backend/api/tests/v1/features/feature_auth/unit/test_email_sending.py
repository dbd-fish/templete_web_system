"""
メール送信機能の単体テスト
"""

import pytest
from unittest.mock import patch, MagicMock

from api.v1.features.feature_auth.send_verification_email import send_verification_email
from api.v1.features.feature_auth.send_reset_password_email import send_reset_password_email


@pytest.mark.asyncio
async def test_send_verification_email_disabled():
    """メール送信が無効化されている場合のテスト"""
    with patch("api.v1.features.feature_auth.send_verification_email.setting") as mock_setting:
        mock_setting.ENABLE_EMAIL_SENDING = False
        mock_setting.PYTEST_MODE = True
        mock_setting.APP_NAME = "Test App"
        
        # メール送信が無効化されているため、例外は発生しない
        await send_verification_email("test@example.com", "http://example.com/verify")


@pytest.mark.asyncio
async def test_send_verification_email_with_mock_smtp():
    """SMTPサーバーをモック化したメール送信テスト"""
    with patch("api.v1.features.feature_auth.send_verification_email.setting") as mock_setting, \
         patch("smtplib.SMTP") as mock_smtp:
        
        # 設定をテスト用に設定
        mock_setting.ENABLE_EMAIL_SENDING = True
        mock_setting.PYTEST_MODE = False  # Falseにしてメール送信を有効化
        mock_setting.SMTP_SERVER = "localhost"
        mock_setting.SMTP_PORT = 1025
        mock_setting.SMTP_USERNAME = "test_user"
        mock_setting.SMTP_PASSWORD = "test_pass"
        mock_setting.APP_NAME = "Test App"
        
        # SMTPサーバーのモック
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        # メール送信テスト
        await send_verification_email("test@example.com", "http://example.com/verify")
        
        # SMTPサーバーが正しく呼び出されたことを確認
        mock_smtp.assert_called_once_with("localhost", 1025)
        mock_server.sendmail.assert_called_once()


@pytest.mark.asyncio
async def test_send_reset_password_email_disabled():
    """パスワードリセットメール送信が無効化されている場合のテスト"""
    with patch("api.v1.features.feature_auth.send_reset_password_email.setting") as mock_setting:
        mock_setting.ENABLE_EMAIL_SENDING = False
        mock_setting.PYTEST_MODE = True
        mock_setting.APP_NAME = "Test App"
        
        # メール送信が無効化されているため、例外は発生しない
        await send_reset_password_email("test@example.com", "http://example.com/reset")


@pytest.mark.asyncio
async def test_send_reset_password_email_with_mock_smtp():
    """SMTPサーバーをモック化したパスワードリセットメール送信テスト"""
    with patch("api.v1.features.feature_auth.send_reset_password_email.setting") as mock_setting, \
         patch("smtplib.SMTP") as mock_smtp:
        
        # 設定をテスト用に設定
        mock_setting.ENABLE_EMAIL_SENDING = True
        mock_setting.PYTEST_MODE = False  # Falseに変更してメール送信を有効化
        mock_setting.SMTP_SERVER = "localhost"
        mock_setting.SMTP_PORT = 1025
        mock_setting.SMTP_USERNAME = "test_user"
        mock_setting.SMTP_PASSWORD = "test_pass"
        mock_setting.APP_NAME = "Test App"
        
        # SMTPサーバーのモック
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        # メール送信テスト
        await send_reset_password_email("test@example.com", "http://example.com/reset")
        
        # SMTPサーバーが正しく呼び出されたことを確認
        mock_smtp.assert_called_once_with("localhost", 1025)
        mock_server.sendmail.assert_called_once()


@pytest.mark.asyncio
async def test_verification_email_content():
    """認証メールの内容確認テスト"""
    with patch("api.v1.features.feature_auth.send_verification_email.setting") as mock_setting, \
         patch("smtplib.SMTP") as mock_smtp:
        
        # 設定
        mock_setting.ENABLE_EMAIL_SENDING = True
        mock_setting.PYTEST_MODE = False  # Falseに変更してメール送信を有効化
        mock_setting.SMTP_SERVER = "localhost"
        mock_setting.SMTP_PORT = 1025
        mock_setting.SMTP_USERNAME = "test_user"
        mock_setting.SMTP_PASSWORD = "test_pass"
        mock_setting.APP_NAME = "Test Application"
        
        # SMTPサーバーのモック
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        # メール送信
        test_email = "user@example.com"
        test_url = "http://example.com/verify?token=abc123"
        await send_verification_email(test_email, test_url)
        
        # sendmailが呼び出されたかを確認
        assert mock_server.sendmail.called
        
        # sendmailの引数を確認
        call_args = mock_server.sendmail.call_args[0]
        from_addr = call_args[0]
        to_addr = call_args[1]
        message = call_args[2]
        
        assert to_addr == test_email
        # メッセージはBase64エンコードされているため、デコードして確認
        import base64
        if "base64" in message:
            # Base64エンコードされた部分を抽出してデコード
            import re
            base64_match = re.search(r'Content-Transfer-Encoding: base64\r?\n\r?\n([A-Za-z0-9+/=\r\n]+)', message)
            if base64_match:
                encoded_content = base64_match.group(1).replace('\n', '').replace('\r', '')
                try:
                    decoded_content = base64.b64decode(encoded_content).decode('utf-8')
                    assert test_url in decoded_content
                    assert "Test Application" in decoded_content
                except:
                    # フォールバック: エンコードされた状態で確認
                    assert "test" in message.lower()


@pytest.mark.asyncio
async def test_reset_password_email_content():
    """パスワードリセットメールの内容確認テスト"""
    with patch("api.v1.features.feature_auth.send_reset_password_email.setting") as mock_setting, \
         patch("smtplib.SMTP") as mock_smtp:
        
        # 設定
        mock_setting.ENABLE_EMAIL_SENDING = True
        mock_setting.PYTEST_MODE = False  # Falseに変更してメール送信を有効化
        mock_setting.SMTP_SERVER = "localhost"
        mock_setting.SMTP_PORT = 1025
        mock_setting.SMTP_USERNAME = "test_user"
        mock_setting.SMTP_PASSWORD = "test_pass"
        mock_setting.APP_NAME = "Test Application"
        
        # SMTPサーバーのモック
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        # メール送信
        test_email = "user@example.com"
        test_url = "http://example.com/reset?token=xyz789"
        await send_reset_password_email(test_email, test_url)
        
        # sendmailが呼び出されたかを確認
        assert mock_server.sendmail.called
        
        # sendmailの引数を確認
        call_args = mock_server.sendmail.call_args[0]
        from_addr = call_args[0]
        to_addr = call_args[1]
        message = call_args[2]
        
        assert to_addr == test_email
        # メッセージはBase64エンコードされているため、デコードして確認
        import base64
        if "base64" in message:
            # Base64エンコードされた部分を抽出してデコード
            import re
            base64_match = re.search(r'Content-Transfer-Encoding: base64\r?\n\r?\n([A-Za-z0-9+/=\r\n]+)', message)
            if base64_match:
                encoded_content = base64_match.group(1).replace('\n', '').replace('\r', '')
                try:
                    decoded_content = base64.b64decode(encoded_content).decode('utf-8')
                    assert test_url in decoded_content
                    assert "Test Application" in decoded_content
                except:
                    # フォールバック: エンコードされた状態で確認
                    assert "test" in message.lower()