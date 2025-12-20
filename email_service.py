import os
import resend

resend.api_key = os.getenv("RESEND_API_KEY")

FROM_EMAIL = "Sehatra <onboarding@resend.dev>"  # abhi ye use karo


def send_verification_email(to_email, verify_link):
    try:
        resend.Emails.send({
            "from": FROM_EMAIL,
            "to": [to_email],
            "subject": "Verify your email - Sehatra",
            "html": f"""
                <h2>Welcome to Sehatra</h2>
                <p>Please verify your email by clicking the link below:</p>
                <a href="{verify_link}">Verify Email</a>
            """
        })
        return True
    except Exception as e:
        print("Resend error:", e)
        return False
