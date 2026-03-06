import os
from dotenv import load_dotenv

# Load .env file (for local development)
load_dotenv()

# MongoDB Atlas
MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise ValueError("MONGO_URI environment variable is not set!")

# Gmail SMTP
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
    raise ValueError("EMAIL_ADDRESS and EMAIL_PASSWORD environment variables must be set!")

# JWT
JWT_SECRET = os.getenv("JWT_SECRET")
if not JWT_SECRET:
    raise ValueError("JWT_SECRET environment variable is not set!")
JWT_EXPIRY_SECONDS = 86400  # 1 day
