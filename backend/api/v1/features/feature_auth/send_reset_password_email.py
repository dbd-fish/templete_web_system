import smtplib
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import structlog

from api.common.setting import setting

# ログの設定
logger = structlog.get_logger()

async def send_reset_password_email(email: str, reset_password_url: str):
    """
    パスワードリセット用メールを送信する（標準ライブラリ使用）。

    Args:
        email (str): 受信者のメールアドレス。
        reset_password_url (str): リセットリンク。

    Returns:
        None
    """
    logger.info("send_reset_password_email - start", email=email)
    
    # テスト環境でメール送信が無効化されている場合はスキップ
    # SMTP認証情報が設定されていない場合もスキップ
    if not setting.ENABLE_EMAIL_SENDING or setting.PYTEST_MODE or not setting.SMTP_USERNAME or not setting.SMTP_PASSWORD:
        logger.info("Email sending disabled - using mock mode", 
                   email=email, 
                   reset_password_url=reset_password_url,
                   reason="Missing SMTP credentials or disabled")
        return
    
    try:
        # メールの内容
        subject = "パスワード再設定のお願い"
        body = f"""
        お世話になります。
        {setting.APP_NAME}です。

        以下のリンクをクリックして、パスワード再設定を完了してください:
        {reset_password_url}

        このリンクは一定時間のみ有効です。
        """

        # MIME形式でメールを作成
        msg = MIMEMultipart()
        msg["From"] = setting.SMTP_USERNAME or "test@example.com"
        msg["To"] = email
        msg["Subject"] = str(Header(subject, "utf-8"))

        # メール本文を設定
        msg.attach(MIMEText(body, "plain", "utf-8"))

        # テスト環境の場合は異なるSMTP設定を使用
        if setting.PYTEST_MODE:
            smtp_server = setting.TEST_SMTP_SERVER
            smtp_port = setting.TEST_SMTP_PORT
            use_tls = False
            use_auth = False
        else:
            smtp_server = setting.SMTP_SERVER
            smtp_port = setting.SMTP_PORT
            use_tls = True
            use_auth = bool(setting.SMTP_USERNAME and setting.SMTP_PASSWORD)

        # SMTPサーバーに接続
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            if use_tls:
                server.starttls()  # TLSで暗号化
            if use_auth:
                server.login(setting.SMTP_USERNAME, setting.SMTP_PASSWORD)  # ログイン
            server.sendmail(msg["From"], email, msg.as_string())  # メール送信
        logger.info("reset password email sent", email=email)
    except Exception as e:
        logger.info("Failed to send reset password email", email=email, error=str(e))
        raise e
    finally:
        logger.info("send_reset_password_email - end")
