import secrets
import string
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from flask_mail import Message
from config import Config
from flask import current_app

def generate_default_password(length=12):
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(characters) for _ in range(length))

def generate_reset_token(email):
    serializer = URLSafeTimedSerializer(Config.SECRET_KEY)
    return serializer.dumps(email, salt="password-reset-salt")

def verify_reset_token(token, max_age=3600):
    serializer = URLSafeTimedSerializer(Config.SECRET_KEY)
    try:
        email = serializer.loads(token, salt="password-reset-salt", max_age=max_age)
        return email

    except(BadSignature, SignatureExpired):
        return None

def send_reset_email(email, token):
    reset_link = f"{Config.FRONTEND_URL}/reset_password?token={token}"
    msg = Message(
        subject="Password Reset Request",
        sender=Config.ADMIN_USERNAME,
        recipients=[email],
    )
    msg.body = f"Click the link to reset your password: {reset_link}"
    current_app.extensions['mail'].send(msg)