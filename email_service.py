from flask_mail import Message
from main import mail   # agar circular ho to main se import adjust karo

def send_email(subject, recipients, html_body):
    try:
        msg = Message(
            subject=subject,
            recipients=recipients
        )
        msg.html = html_body
        mail.send(msg)
        return True
    except Exception as e:
        print("Email error:", e)
        return False
