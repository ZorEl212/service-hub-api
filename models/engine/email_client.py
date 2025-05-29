import asyncio
import os
import smtplib, ssl
from email.message import EmailMessage
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


class EmailClient:
    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        username: Optional[str] = None,
        password: Optional[str] = None
    ):
        self.host = host or os.getenv("EMAIL_HOST")
        self.port = int(port or os.getenv("EMAIL_PORT", 465))  # SSL typically uses port 465
        self.username = username or os.getenv("EMAIL_USERNAME")
        self.password = password or os.getenv("EMAIL_PASSWORD")
        self.context = ssl.create_default_context()

        if not all([self.host, self.port, self.username, self.password]):
            raise ValueError("Missing required email configuration")

    async def _send_email(self, to: str, subject: str, body: str, html: bool = False):
        def send():
            msg = EmailMessage()
            msg['Subject'] = subject
            msg['From'] = self.username
            msg['To'] = to

            if html:
                msg.add_alternative(body, subtype='html')
            else:
                msg.set_content(body)

            # Use SMTP_SSL instead of SMTP + starttls
            with smtplib.SMTP_SSL(self.host, self.port, context=self.context) as server:
                server.login(self.username, self.password)
                server.send_message(msg)

        await asyncio.to_thread(send)

    async def send_verification_email(self, to: str, token: str):
        subject = "Verify Your Email Address"
        url = f"http://localhost:3000/verify-email/?token={token}&email={to}"
        body = f"""
        <h2>Email Verification</h2>
        <p>Please verify your email by clicking the link below:</p>
        <p><a href="{url}">Click here to verify your email</a></p>
        """
        await self._send_email(to, subject, body, html=True)

    async def send_password_reset_email(self, to: str, token: str):
        subject = "Password Reset Request"
        body = f"""
        <h2>Password Reset</h2>
        <p>Click the link below to reset your password:</p>
        <p><a href="{reset_link}">{reset_link}</a></p>
        """
        await self._send_email(to, subject, body, html=True)

    async def send_notification(self, to: str, subject: str, message: str, html: bool = False):
        await self._send_email(to, subject, message, html=html)
