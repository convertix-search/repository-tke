#!/usr/bin/env python3
import importlib
import os
import smtplib
import sys
import traceback
from email.message import EmailMessage as StdEmailMessage


# Set this before running the script.
TO_EMAIL = "harshana.narangoda@qualitapps.com"


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lead_form.settings")
    settings_module_name = os.environ.get("DJANGO_SETTINGS_MODULE", "lead_form.settings")

    if not TO_EMAIL or TO_EMAIL == "replace-with-real-recipient@example.com":
        print("[ERROR] Please update TO_EMAIL in email_test_send.py before running.")
        return 1

    settings = None
    use_django_mail = False
    django_email_message = None

    try:
        import django
        django.setup()
        from django.conf import settings as django_settings
        from django.core.mail import EmailMessage as DjangoEmailMessage
        settings = django_settings
        django_email_message = DjangoEmailMessage
        use_django_mail = True
        print("[INFO] Django path enabled.")
    except Exception as exc:
        print("[WARN] Django mail path unavailable, switching to SMTP fallback:", exc)
        try:
            settings = importlib.import_module(settings_module_name)
        except Exception:
            settings = importlib.import_module("lead_form.settings_dev")

    from_email = getattr(settings, "EMAIL_HOST_USER", None)

    if use_django_mail:
        try:
            from constance import config
            from_email = config.FROM_EMAIL
        except Exception:
            pass

    if not from_email:
        print("[ERROR] Missing FROM address. Set CONSTANCE FROM_EMAIL or EMAIL_HOST_USER.")
        return 1

    subject = "SMTP test from Lead Form"
    body = (
        "This is a test email from the Lead Form project.\n\n"
        "If you received this message, SMTP configuration is working."
    )

    print("[INFO] Sending with settings:")
    print("  EMAIL_HOST=", getattr(settings, "EMAIL_HOST", None))
    print("  EMAIL_PORT=", getattr(settings, "EMAIL_PORT", None))
    print("  EMAIL_USE_TLS=", getattr(settings, "EMAIL_USE_TLS", None))
    print("  EMAIL_USE_SSL=", getattr(settings, "EMAIL_USE_SSL", None))
    print("  EMAIL_TIMEOUT=", getattr(settings, "EMAIL_TIMEOUT", None))
    print("  FROM=", from_email)
    print("  TO=", TO_EMAIL)

    try:
        if use_django_mail:
            email = django_email_message(subject=subject, body=body, from_email=from_email, to=[TO_EMAIL])
            sent = email.send(fail_silently=False)
            print("[OK] Django email send call completed. Provider return value:", sent)
        else:
            msg = StdEmailMessage()
            msg["Subject"] = subject
            msg["From"] = from_email
            msg["To"] = TO_EMAIL
            msg.set_content(body)

            host = getattr(settings, "EMAIL_HOST", None)
            port = int(getattr(settings, "EMAIL_PORT", 587))
            use_tls = bool(getattr(settings, "EMAIL_USE_TLS", False))
            username = getattr(settings, "EMAIL_HOST_USER", None)
            password = getattr(settings, "EMAIL_HOST_PASSWORD", None)
            timeout = int(getattr(settings, "EMAIL_TIMEOUT", 15))

            if not host or not username or not password:
                print("[ERROR] Missing SMTP host/user/password in settings.")
                return 1

            with smtplib.SMTP(host, port, timeout=timeout) as server:
                server.ehlo()
                if use_tls:
                    server.starttls()
                    server.ehlo()
                server.login(username, password)
                server.send_message(msg)
            print("[OK] SMTP fallback send completed.")
        return 0
    except Exception as exc:
        print("[ERROR] Email send failed:", exc)
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
