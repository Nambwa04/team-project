from flask_mail import Message
from flask import current_app
from models import mail

def send_email(subject, recipients, body):
    try:
        msg = Message(
            subject,
            sender=current_app.config['MAIL_DEFAULT_SENDER'],
            recipients=recipients
        )
        msg.body = body
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False

def send_temp_password_email(email, password, role):
    """Send temporary password to new user"""
    subject = 'Your SafeHaven Account Credentials'
    recipients = [email]
    body = f"""
Hello,

An administrator has created a {role} account for you on SafeHaven.

Your temporary login credentials are:
Email: {email}
Password: {password}

Please login and change your password immediately.

Best regards,
SafeHaven Team
    """
    return send_email(subject, recipients, body)