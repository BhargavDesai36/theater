# Python imports
import secrets
import smtplib
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Tuple

# Django imports
from django.utils import timezone

# App imports
from theater.settings import SMTP_PORT, SMTP_SERVER


def send_email(email_data):
    try:
        msg = MIMEMultipart()
        msg["From"] = email_data["sender_email"]
        msg["To"] = email_data["receiver_email"]
        msg["Subject"] = email_data["subject"]

        msg.attach(MIMEText(email_data["html"], "html"))

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()

        server.login(email_data["sender_email"], email_data["sender_password"])

        server.sendmail(
            email_data["sender_email"], email_data["receiver_email"], msg.as_string()
        )
        server.quit()
        return True
    except smtplib.SMTPAuthenticationError:
        return False
    except smtplib.SMTPConnectError:
        return False
    except smtplib.SMTPException:
        return False


def generate_token() -> Tuple[str, datetime]:
    otp = str(secrets.randbelow(900000) + 100000)
    expiration_time = timezone.now() + timedelta(minutes=5)
    return otp, expiration_time


def is_otp_expired(expiration_time) -> bool:
    now = datetime.now(timezone.utc)
    return now > expiration_time if expiration_time else True
