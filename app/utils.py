"""
app/utils.py — LINO Email OTP Utility
Sends beautifully branded HTML emails for OTP verification.
"""

import secrets
import threading
from django.core.mail import EmailMultiAlternatives, get_connection
from django.conf import settings


def _send_email_async(msg, target_email):
    """Worker thread to dispatch email asynchronously without blocking HTTP response."""
    try:
        msg.send(fail_silently=False)
        if getattr(settings, "DEBUG", False):
            print(f"[LINO EMAIL SUCCESS] OTP sent to {target_email}")
    except Exception as exc:
        if getattr(settings, "DEBUG", False):
            print(f"[LINO EMAIL ERROR] {target_email}: {exc}")


# ─────────────────────────────────────────────────────────────────
# OTP Generator
# ─────────────────────────────────────────────────────────────────

def generate_otp() -> str:
    """Return a cryptographically safe 6-digit OTP string."""
    return str(secrets.randbelow(900000) + 100000)


# ─────────────────────────────────────────────────────────────────
# HTML Email Builder
# ─────────────────────────────────────────────────────────────────

def _build_otp_html(user_name: str, otp_code: str, purpose: str, valid_minutes: int = 10) -> str:
    """Return a beautifully branded LINO HTML email body."""

    purpose_titles = {
        "password_reset":  "Password Reset OTP",
        "change_password": "Password Change OTP",
        "verify_email":    "Email Verification OTP",
    }
    purpose_desc = {
        "password_reset":  "to reset your LINO account password",
        "change_password": "to confirm your password change",
        "verify_email":    "to verify your email address",
    }

    title = purpose_titles.get(purpose, "Your OTP Code")
    desc  = purpose_desc.get(purpose,  "to complete your request")

    # Build individual digit boxes
    digit_boxes = []
    for d in otp_code:
        digit_boxes.append(
            '<span style="display:inline-block;width:44px;height:54px;line-height:54px;'
            'text-align:center;background:#1a1208;border:1px solid rgba(212,175,55,0.4);'
            'border-radius:8px;font-size:1.8rem;font-weight:700;color:#D4AF37;'
            'margin:0 3px;">' + d + '</span>'
        )
    otp_digits_html = "".join(digit_boxes)

    html = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>LINO &bull; """ + title + """</title>
</head>
<body style="margin:0;padding:0;background:#0d0a08;font-family:'Segoe UI',Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#0d0a08;padding:40px 16px;">
    <tr><td align="center">
      <table width="540" cellpadding="0" cellspacing="0"
             style="background:#14100c;border:1px solid rgba(212,175,55,0.25);
                    border-radius:16px;overflow:hidden;max-width:540px;width:100%;">

        <!-- Header -->
        <tr>
          <td style="background:linear-gradient(135deg,#1c1510 0%,#0d0a08 100%);
                     padding:32px 40px;text-align:center;
                     border-bottom:1px solid rgba(212,175,55,0.2);">
            <p style="margin:0 0 8px;font-size:0.75rem;color:#a0958a;
                      letter-spacing:4px;text-transform:uppercase;">L I N O</p>
            <h1 style="margin:0;font-size:1.5rem;font-weight:300;color:#ffffff;letter-spacing:2px;">ATELIER</h1>
            <p style="margin:10px 0 0;font-size:0.8rem;color:#D4AF37;
                      letter-spacing:1.5px;text-transform:uppercase;">""" + title + """</p>
          </td>
        </tr>

        <!-- Body -->
        <tr>
          <td style="padding:36px 40px;">
            <p style="margin:0 0 6px;font-size:0.85rem;color:#a0958a;">
              Hello, <strong style="color:#e5ded7;">""" + user_name + """</strong>
            </p>
            <p style="margin:0 0 28px;font-size:0.9rem;color:#c4b6a8;line-height:1.6;">
              Use the 6-digit code below """ + desc + """. This code is valid for
              <strong style="color:#D4AF37;">""" + str(valid_minutes) + """ minutes</strong> only.
            </p>

            <!-- OTP Digits -->
            <div style="text-align:center;margin:0 0 28px;">
              """ + otp_digits_html + """
            </div>

            <!-- Security Notice -->
            <table width="100%" cellpadding="0" cellspacing="0"
                   style="background:rgba(212,175,55,0.06);border:1px solid rgba(212,175,55,0.15);
                          border-radius:8px;margin-bottom:28px;">
              <tr>
                <td style="padding:14px 18px;">
                  <p style="margin:0;font-size:0.78rem;color:#8c8278;line-height:1.5;">
                    &#128274; <strong style="color:#D4AF37;">Never share this code</strong> with anyone,
                    including LINO support. If you did not request this, please ignore this email.
                  </p>
                </td>
              </tr>
            </table>

            <p style="margin:0;font-size:0.82rem;color:#6b5e55;line-height:1.6;">
              Warm regards,<br>
              <strong style="color:#a0958a;">The LINO Atelier Team</strong>
            </p>
          </td>
        </tr>

        <!-- Footer -->
        <tr>
          <td style="padding:20px 40px;text-align:center;border-top:1px solid rgba(255,255,255,0.05);">
            <p style="margin:0;font-size:0.72rem;color:#4a3f38;line-height:1.5;">
              &copy; 2026 LINO Atelier &bull; mylino2026@gmail.com<br>
              This is an automated message &mdash; please do not reply.
            </p>
          </td>
        </tr>

      </table>
    </td></tr>
  </table>
</body>
</html>"""
    return html


# ─────────────────────────────────────────────────────────────────
# Public Send Function
# ─────────────────────────────────────────────────────────────────

def send_otp_email(user_or_email, otp_code: str, purpose: str = "password_reset", valid_minutes: int = 15) -> bool:
    """
    Send a branded LINO OTP email asynchronously.

    Args:
        user_or_email : Django User object or email address string
        otp_code      : 6-digit OTP string
        purpose       : 'password_reset' | 'change_password' | 'verify_email'
        valid_minutes : OTP validity window shown in email

    Returns:
        True on success, False on failure.
    """
    purpose_subjects = {
        "password_reset":  "LINO - Your Password Reset OTP",
        "change_password": "LINO - Confirm Password Change OTP",
        "verify_email":    "LINO - Email Verification OTP",
    }

    subject = purpose_subjects.get(purpose, "LINO - Your OTP Code")
    if hasattr(user_or_email, 'email'):
        target_email = user_or_email.email
        user_name = user_or_email.get_full_name() or user_or_email.username
    else:
        target_email = str(user_or_email).strip().lower()
        user_name = target_email.split('@')[0]

    from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "LINO Atelier <mylino2026@gmail.com>")
    html_body  = _build_otp_html(user_name, otp_code, purpose, valid_minutes)

    plain_body = (
        f"Hello {user_name},\n\n"
        f"Your LINO OTP code is: {otp_code}\n\n"
        f"This code is valid for {valid_minutes} minutes. "
        f"Do not share it with anyone.\n\n"
        f"Warm regards,\nThe LINO Atelier Team"
    )

    # Write to local log file for instant zero-delay access
    try:
        from django.utils import timezone
        log_dir = settings.BASE_DIR / "logs"
        log_dir.mkdir(exist_ok=True)
        otp_log_file = log_dir / "otp.log"
        with open(otp_log_file, "a", encoding="utf-8") as f:
            now_str = timezone.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{now_str}] Purpose: {purpose} | Target: {target_email} | OTP: {otp_code}\n")
    except Exception:
        pass

    try:
        connection = get_connection(fail_silently=False, timeout=5)
        msg = EmailMultiAlternatives(
            subject=subject,
            body=plain_body,
            from_email=from_email,
            to=[target_email],
            connection=connection,
        )
        msg.attach_alternative(html_body, "text/html")

        # Spawn non-blocking background thread for instant UI response
        email_thread = threading.Thread(target=_send_email_async, args=(msg, target_email), daemon=True)
        email_thread.start()
        return True
    except Exception as exc:
        if getattr(settings, "DEBUG", False):
            print(f"[LINO EMAIL ERROR] {target_email}: {exc}")
        return False

