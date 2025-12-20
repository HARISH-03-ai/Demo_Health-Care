import resend
import os

resend.api_key = os.getenv("RESEND_API_KEY")

def send_verification_email(email, verify_link):
    resend.Emails.send({
        "from": "Sehatra <onboarding@resend.dev>",
        "to": email,
        "subject": "Verify your email",
        "html": f"""
        <h3>Verify your email</h3>
        <p>Click below to verify:</p>
        <a href="{verify_link}">Verify Email</a>
        """
    })
