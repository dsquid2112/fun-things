"""Send HTML email via Gmail SMTP using an App Password."""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import config


def send_email(subject: str, html_body: str) -> None:
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = config.GMAIL_USER
    msg["To"] = config.RECIPIENT_EMAIL

    msg.attach(MIMEText(html_body, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(config.GMAIL_USER, config.GMAIL_APP_PASSWORD)
        server.sendmail(config.GMAIL_USER, config.RECIPIENT_EMAIL, msg.as_string())
