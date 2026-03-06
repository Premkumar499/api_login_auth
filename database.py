from pymongo import MongoClient
from config import MONGO_URI
import certifi

try:
    client = MongoClient(
        MONGO_URI,
        tlsCAFile=certifi.where(),
        serverSelectionTimeoutMS=5000
    )
    # Test the connection
    client.admin.command('ping')
    print("✅ MongoDB connected successfully!")
except Exception as e:
    print(f"❌ MongoDB connection error: {e}")
    raise

db = client["prompt_library"]

users_col = db["users"]
otp_col = db["otp"]
levels_col = db["levels"]
topics_col = db["topics"]

# Create indexes for performance + safety
try:
    users_col.create_index("email", unique=True)
    topics_col.create_index("level")
    print("✅ Database indexes created successfully!")
except Exception as e:
    print(f"⚠️  Warning: Could not create indexes: {e}")
