import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from app.core.config import (
    SMTP_HOST,
    SMTP_PORT,
    SMTP_USER,
    SMTP_PASSWORD,
    SMTP_FROM_EMAIL,
    SMTP_USE_TLS,
)
from app.core.logger import logger


def send_password_reset_email(to_email: str, reset_token: str) -> None:
    subject = "Match Combat - Password Reset"
    body = (
        f"You have requested a password reset.\n\n"
        f"Use the following token to reset your password:\n\n"
        f"{reset_token}\n\n"
        f"This token expires in 1 hour.\n"
        f"If you did not request this, please ignore this email."
    )

    msg = MIMEMultipart()
    msg["From"] = SMTP_FROM_EMAIL
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
        if SMTP_USE_TLS:
            server.starttls()
        if SMTP_USER and SMTP_PASSWORD:
            server.login(SMTP_USER, SMTP_PASSWORD)
        server.sendmail(SMTP_FROM_EMAIL, to_email, msg.as_string())
        server.quit()
        logger.info(f"Password reset email sent to {to_email}")
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {e}")
        raise
