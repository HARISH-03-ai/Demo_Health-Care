import os
import resend

resend.api_key = os.getenv("RESEND_API_KEY")

def send_email(subject, to, html):
    try:
        resend.Emails.send({
            "from": "Sehatra <onboarding@resend.dev>",
            "to": [to],
            "subject": subject,
            "html": html
        })
        return True
    except Exception as e:
        print("Resend error:", e)
        return False
