
from app.core.config import settings
from app.integrations.email_client import send_email


def send_password_reset_email(
    recipient: str,
    reset_token: str,
) -> None:
    reset_url = (
        f"{settings.FRONTEND_URL}/reset-password"
        f"?token={reset_token}"
    )

    subject = "InfoLens - Password Reset Request"

    body = f"""
Hello,

We received a request to reset your InfoLens account password.

Use the link below to reset your password:

{reset_url}

This link will expire in 15 minutes.

If you did not request a password reset, you can safely ignore this email.

Regards,
InfoLens Team
"""

    send_email(
        recipient=recipient,
        subject=subject,
        body=body,
    )


def send_verification_email(
    recipient: str,
    verification_token: str,
) -> None:
    verification_url = (
        f"{settings.FRONTEND_URL}/verify-email"
        f"?token={verification_token}"
    )

    subject = "InfoLens - Verify Your Email Address"

    body = f"""
Hello,

Thank you for registering with InfoLens!

Please verify your email address by opening the link below:

{verification_url}

This verification link will expire in 30 minutes.

If you did not create an InfoLens account, you can safely ignore this email.

Regards,
InfoLens Team
"""

    send_email(
        recipient=recipient,
        subject=subject,
        body=body,
    )

