import smtplib
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import structlog

from app.common.setting import setting

# ログの設定
logger = structlog.get_logger()

async def send_reset_password_email(email: str, reset_password_url: str):
    """
    認証用メールを送信する（標準ライブラリ使用）。

    Args:
        email (str): 受信者のメールアドレス。
        reset_password_url (str): 認証リンク。

    Returns:
        None
    """
    logger.info("send_reset_password_email - start", email=email)
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
        msg["From"] = setting.SMTP_USERNAME
        msg["To"] = email
        msg["Subject"] = str(Header(subject, "utf-8"))

        # メール本文を設定
        msg.attach(MIMEText(body, "plain", "utf-8"))

        # SMTPサーバーに接続
        with smtplib.SMTP(setting.SMTP_SERVER, setting.SMTP_PORT) as server:
            server.starttls()  # TLSで暗号化
            server.login(setting.SMTP_USERNAME, setting.SMTP_PASSWORD)  # ログイン
            server.sendmail(setting.SMTP_USERNAME, email, msg.as_string())  # メール送信
        logger.info("reset password email sent", email=email)
    except Exception as e:
        logger.info("Failed to send reset password email",email=email)
        raise e
    finally:
        logger.info("send_reset_password_email - end")
