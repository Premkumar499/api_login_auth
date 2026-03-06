import random
import jwt
from datetime import datetime, timedelta, timezone
import smtplib
from email.message import EmailMessage
from werkzeug.security import generate_password_hash, check_password_hash
from config import EMAIL_ADDRESS, EMAIL_PASSWORD, JWT_SECRET, JWT_EXPIRY_SECONDS


def generate_otp():
    return random.randint(100000, 999999)

def send_otp_email(to_email, otp):
    try:
        msg = EmailMessage()
        msg.set_content(f"Your OTP is: {otp}\nValid for 5 minutes.")
        msg["Subject"] = "Account Verification OTP"
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = to_email

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
    except smtplib.SMTPAuthenticationError as e:
        print(f"SMTP Authentication Error: {e}")
        raise Exception("Gmail authentication failed. Check EMAIL_ADDRESS and EMAIL_PASSWORD")
    except Exception as e:
        print(f"Email sending error: {e}")
        raise

def hash_password(password):
    return generate_password_hash(password)

def verify_password(password, hashed):
    return check_password_hash(hashed, password)

def create_jwt(email):
    payload = {
        "email": email,
        "exp": datetime.now(timezone.utc) + timedelta(seconds=JWT_EXPIRY_SECONDS)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")
