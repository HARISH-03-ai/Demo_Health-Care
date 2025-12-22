import os
import resend

# API key
resend.api_key = os.getenv("RESEND_API_KEY")

EMAIL_FROM = os.getenv("EMAIL_FROM", "Sehatra <onboarding@resend.dev>")

def send_email(subject, to_email, html):
    try:
        resend.emails.send({
            "from": EMAIL_FROM,
            "to": [to_email],
            "subject": subject,
            "html": html
        })
        return True
    except Exception as e:
        print("Resend error:", e)
        return False