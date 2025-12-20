from flask_mail import Message

def send_email(mail, subject, recipients, html_body):
    try:
        msg = Message(
            subject=subject,
            recipients=recipients,
            html=html_body
        )
        mail.send(msg)
        return True
    except Exception as e:
        print("Email error:", e)
        return False