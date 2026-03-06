import os
from dotenv import load_dotenv

load_dotenv()

# MongoDB Atlas
MONGO_URI = os.getenv("MONGO_URI")

# Gmail SMTP
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

# JWT
JWT_SECRET = os.getenv("JWT_SECRET")
JWT_EXPIRY_SECONDS = 86400  # 1 day
