import os
import resend

resend.api_key = os.getenv("RESEND_API_KEY")

def send_email(subject, to_email, html):
    try:
        resend.Emails.send({
            "from": os.getenv("EMAIL_FROM"),
            "to": [to_email],
            "subject": subject,
            "html": html
        })
        return True
    except Exception as e:
        print("Resend error:", e)
        return False
