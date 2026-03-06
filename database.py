from pymongo import MongoClient
from config import MONGO_URI
import certifi

client = MongoClient(
    MONGO_URI,
    tlsCAFile=certifi.where()
)

db = client["prompt_library"]

users_col = db["users"]
otp_col = db["otp"]
levels_col = db["levels"]
topics_col = db["topics"]

# performance + safety
users_col.create_index("email", unique=True)
topics_col.create_index("level")
