import random
from typing import Optional, Callable
from fastapi import BackgroundTasks
import logging
import httpx
from services.settings import settings

def generate_otp() -> str:
    """Return a random 6-digit numeric OTP as a string."""
    return f"{random.randint(100000, 999999)}"

async def _send_via_brevo(to_email: str, subject: str, html_content: str):
    """Internal helper to send email via Brevo (formerly Sendinblue) HTTP API."""
    api_key = getattr(settings, "BREVO_API_KEY", None)
    if not api_key:
        logging.error("BREVO_API_KEY not found in settings")
        return

    # Use the verified sender email from settings or default to the admin email
    sender_email = getattr(settings, "MAIL_FROM", "autoplan3d@gmail.com")

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "https://api.brevo.com/v3/smtp/email",
                headers={
                    "api-key": api_key,
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
                json={
                    "sender": {"name": "AutoPlan", "email": sender_email},
                    "to": [{"email": to_email}],
                    "subject": subject,
                    "htmlContent": html_content,
                },
                timeout=10.0
            )
            if response.status_code >= 400:
                logging.error(f"Brevo API error: {response.text}")
        except Exception as e:
            logging.error(f"Failed to send email via Brevo: {e}")

def send_otp_email(
    email_to: str,
    background_tasks: BackgroundTasks,
    save_callback: Optional[Callable[[str, str], None]] = None,   
    subject: str = "Your Registration OTP",
    expires_minutes: int = 10,
) -> dict:
    otp = generate_otp()

    html = f"""
    <html>
        <body>
            <p>Hello,</p>
            <p>Your verification code is: <b>{otp}</b></p>
            <p>This code will expire in {expires_minutes} minutes.</p>
        </body>
    </html>
    """

    if save_callback:
        try:
            save_callback(email_to, otp)
        except Exception:
            pass

    background_tasks.add_task(_send_via_brevo, email_to, subject, html)
    return {"otp": otp}

def send_support_email(
    email_from: str,
    category: str,
    details: str,
    background_tasks: BackgroundTasks,
) -> bool:
    admin_email = getattr(settings, "ADMIN_EMAIL", "autoplan3d@gmail.com")

    html = f"""
    <html>
        <body>
            <h3>New Support Request</h3>
            <p><b>User Email:</b> {email_from}</p>
            <p><b>Category:</b> {category}</p>
            <p><b>Details:</b></p>
            <p style="white-space: pre-wrap;">{details}</p>
        </body>
    </html>
    """

    background_tasks.add_task(_send_via_brevo, admin_email, f"Support Request: {category}", html)
    return True

__all__ = ["generate_otp", "send_otp_email", "send_support_email"]
