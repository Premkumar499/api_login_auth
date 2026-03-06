from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, timedelta, timezone
import jwt
import os
from functools import wraps

from config import JWT_SECRET
from database import users_col, otp_col, levels_col, topics_col
from auth import generate_otp, send_otp_email, create_jwt, hash_password, verify_password


app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})   # set frontend domain here 


# ------------------ ROOT & HEALTH CHECK ------------------

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "API is running",
        "version": "1.0",
        "endpoints": {
            "auth": ["/auth/signup", "/auth/login", "/auth/verify-otp", "/auth/set-password", 
                    "/auth/forgot-password", "/auth/verify-reset-otp", "/auth/reset-password"],
            "user": ["/profile"],
            "content": ["/levels", "/topics/<level>"],
            "admin": ["/admin/stats", "/admin/users", "/topic", "/admin/make-admin", 
                     "/admin/remove-admin", "/admin/delete-user"]
        }
    }), 200

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy"}), 200


# ------------------ AUTH MIDDLEWARE ------------------

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.headers.get("Authorization")

        if not auth or not auth.startswith("Bearer "):
            return jsonify({"error": "Login required"}), 401

        token = auth.split(" ")[1]

        try:
            decoded = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Session expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401

        request.user = decoded
        return f(*args, **kwargs)

    return decorated


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        email = request.user["email"]
        user = users_col.find_one({"email": email})

        if not user or user.get("role") != "admin":
            return jsonify({"error": "Admin only access"}), 403

        return f(*args, **kwargs)
    return decorated



# ------------------ SIGNUP (Email & Name Only) ------------------

@app.route("/auth/signup", methods=["POST"])
def signup():
    data = request.json
    email = data.get("email", "").strip()
    name = data.get("name", "").strip()

    if not email or not name:
        return jsonify({"error": "Email and name are required"}), 400

    # Check if user already exists (either registered or pending OTP verification)
    if users_col.find_one({"email": email}):
        return jsonify({"error": "User already exists"}), 400
    
    # Check if there's already a pending verification for this email
    existing_otp = otp_col.find_one({"email": email, "verified": False})
    if existing_otp and not existing_otp.get("type"):
        return jsonify({"error": "OTP already sent. Please verify or wait for expiry."}), 400

    otp = generate_otp()
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=5)

    otp_col.delete_many({"email": email})

    otp_col.insert_one({
        "email": email,
        "name": name,
        "otp": otp,
        "expires_at": expires_at,
        "verified": False
    })

    try:
        send_otp_email(email, otp)
    except:
        return jsonify({"error": "Failed to send OTP email"}), 500

    return jsonify({"message": "OTP sent to email. Please verify."}), 200



# ------------------ SET PASSWORD (After OTP Verification) ------------------

@app.route("/auth/set-password", methods=["POST"])
def set_password():
    data = request.json
    email = data.get("email", "").strip()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400

    # Check if OTP was verified
    record = otp_col.find_one({"email": email, "verified": True})

    if not record:
        return jsonify({"error": "Please verify OTP first"}), 400

    # Check if user already exists
    if users_col.find_one({"email": email}):
        return jsonify({"error": "User already exists"}), 400

    # Assign admin to first user only
    total_users = users_col.count_documents({})
    role = "admin" if total_users == 0 else "user"

    hashed_password = hash_password(password)

    users_col.insert_one({
        "email": email,
        "name": record.get("name"),
        "password": hashed_password,
        "role": role,
        "is_verified": True,
        "created_at": datetime.now(timezone.utc)
    })

    # Clean up OTP record
    otp_col.delete_one({"email": email})

    return jsonify({"message": "Account created successfully. Please login."}), 200



# ------------------ FORGOT PASSWORD ------------------

@app.route("/auth/forgot-password", methods=["POST"])
def forgot_password():
    data = request.json
    email = data.get("email", "").strip()

    if not email:
        return jsonify({"error": "Email required"}), 400

    # Check if user exists
    user = users_col.find_one({"email": email})
    if not user:
        return jsonify({"error": "User not found"}), 404

    otp = generate_otp()
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=5)

    otp_col.delete_many({"email": email})
    otp_col.insert_one({
        "email": email,
        "otp": otp,
        "expires_at": expires_at,
        "verified": False,
        "type": "password_reset"
    })

    try:
        send_otp_email(email, otp)
    except:
        return jsonify({"error": "Failed to send OTP"}), 500

    return jsonify({"message": "Password reset OTP sent to email"}), 200



# ------------------ VERIFY FORGOT PASSWORD OTP ------------------

@app.route("/auth/verify-reset-otp", methods=["POST"])
def verify_reset_otp():
    data = request.json
    email = data.get("email", "").strip()
    otp = str(data.get("otp", "")).strip()

    record = otp_col.find_one({"email": email, "type": "password_reset"})

    if not record:
        return jsonify({"error": "OTP not found"}), 400

    if str(record["otp"]) != otp:
        return jsonify({"error": "Invalid OTP"}), 400

    expires_at = record["expires_at"]
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    if datetime.now(timezone.utc) > expires_at:
        return jsonify({"error": "OTP expired"}), 400

    # Mark OTP as verified for password reset
    otp_col.update_one(
        {"email": email, "type": "password_reset"},
        {"$set": {"verified": True}}
    )

    return jsonify({
        "message": "OTP verified. You can now reset your password.",
        "redirect": "reset-password",
        "email": email
    }), 200



# ------------------ RESET PASSWORD ------------------

@app.route("/auth/reset-password", methods=["POST"])
def reset_password():
    data = request.json
    email = data.get("email", "").strip()
    new_password = data.get("password", "")

    if not email or not new_password:
        return jsonify({"error": "Email and password are required"}), 400

    if len(new_password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400

    # Check if reset OTP was verified
    record = otp_col.find_one({"email": email, "type": "password_reset", "verified": True})

    if not record:
        return jsonify({"error": "Please verify OTP first"}), 400

    # Update user password
    hashed_password = hash_password(new_password)
    result = users_col.update_one(
        {"email": email},
        {"$set": {"password": hashed_password}}
    )

    if result.modified_count == 0:
        return jsonify({"error": "Failed to reset password"}), 500

    # Clean up OTP record
    otp_col.delete_one({"email": email})

    return jsonify({"message": "Password reset successfully. Please login."}), 200


# ------------------ VERIFY OTP ------------------

@app.route("/auth/verify-otp", methods=["POST"])
def verify_otp():
    data = request.json
    email = data.get("email", "").strip()
    otp = str(data.get("otp", "")).strip()

    record = otp_col.find_one({"email": email})

    if not record:
        return jsonify({"error": "OTP not found"}), 400

    if str(record["otp"]) != otp:
        return jsonify({"error": "Invalid OTP"}), 400

    expires_at = record["expires_at"]
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    if datetime.now(timezone.utc) > expires_at:
        return jsonify({"error": "OTP expired"}), 400

    # Mark OTP as verified, don't create user yet (will be created after password is set)
    otp_col.update_one(
        {"email": email},
        {"$set": {"verified": True}}
    )

    return jsonify({
        "message": "OTP verified successfully",
        "redirect": "set-password",
        "email": email
    }), 200
    return jsonify({"message": "Account verified successfully"})



# ------------------ LOGIN ------------------

@app.route("/auth/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email", "").strip()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400

    user = users_col.find_one({"email": email})
    if not user:
        return jsonify({"error": "User not found"}), 404

    if not user.get("is_verified"):
        return jsonify({"error": "Email not verified"}), 403

    if not verify_password(password, user["password"]):
        return jsonify({"error": "Invalid password"}), 401

    token = create_jwt(email)

    return jsonify({
        "message": "Login successful",
        "token": token,
        "name": user.get("name"),
        "email": email,
        "role": user.get("role", "user")
    }), 200




# ------------------ PROFILE ------------------

@app.route("/profile", methods=["GET"])
@token_required
def profile():
    email = request.user["email"]

    user = users_col.find_one(
        {"email": email},
        {"_id": 0, "password": 0}
    )

    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify(user), 200




# ------------------ CONTENT APIs ------------------

@app.route("/levels", methods=["GET"])
def get_levels():
    levels = list(levels_col.find({}, {"_id": 0}))
    return jsonify(levels), 200


@app.route("/topics/<int:level>", methods=["GET"])
def topics(level):
    topics = list(topics_col.find({"level": level}, {"_id": 0}))
    return jsonify(topics), 200


@app.route("/topic", methods=["POST"])
@token_required
@admin_required
def add_topic():
    data = request.json

    required = ["level", "title", "content"]
    if not all(k in data for k in required):
        return jsonify({"error": "level, title and content required"}), 400

    topics_col.insert_one(data)
    return jsonify({"message": "Topic added"}), 200


# ------------------ ADMIN STATS ------------------

@app.route("/admin/stats", methods=["GET"])
@token_required
@admin_required
def admin_stats():
    return jsonify({
        "users": users_col.count_documents({}),
        "levels": levels_col.count_documents({}),
        "topics": topics_col.count_documents({})
    }), 200


# ------------------ ADMIN USER MANAGEMENT ------------------

@app.route("/admin/users", methods=["GET"])
@token_required
@admin_required
def get_users():
    users = list(users_col.find({}, {"password": 0, "_id": 0}))
    return jsonify(users), 200


@app.route("/admin/make-admin", methods=["PUT"])
@token_required
@admin_required
def make_admin():
    email = request.json.get("email")

    users_col.update_one(
        {"email": email},
        {"$set": {"role": "admin"}}
    )

    return jsonify({"message": "User promoted to admin"}), 200


@app.route("/admin/remove-admin", methods=["PUT"])
@token_required
@admin_required
def remove_admin():
    email = request.json.get("email")

    users_col.update_one(
        {"email": email},
        {"$set": {"role": "user"}}
    )

    return jsonify({"message": "Admin role removed"}), 200


@app.route("/admin/delete-user", methods=["DELETE"])
@token_required
@admin_required
def delete_user():
    email = request.json.get("email")

    users_col.delete_one({"email": email})
    return jsonify({"message": "User deleted"}), 200


# ------------------ ADMIN LEVEL MANAGEMENT ------------------

@app.route("/levels", methods=["POST"])
@token_required
@admin_required
def add_level():
    data = request.json
    levels_col.insert_one(data)
    return jsonify({"message": "Level added"}), 200


@app.route("/levels/<int:level>", methods=["PUT"])
@token_required
@admin_required
def update_level(level):
    data = request.json
    levels_col.update_one({"level": level}, {"$set": data})
    return jsonify({"message": "Level updated"}), 200


@app.route("/levels/<int:level>", methods=["DELETE"])
@token_required
@admin_required
def delete_level(level):
    levels_col.delete_one({"level": level})
    topics_col.delete_many({"level": level})
    return jsonify({"message": "Level deleted"}), 200


# ------------------ ADMIN TOPIC MANAGEMENT ------------------

@app.route("/topic/<string:title>", methods=["PUT"])
@token_required
@admin_required
def update_topic(title):
    data = request.json
    topics_col.update_one({"title": title}, {"$set": data})
    return jsonify({"message": "Topic updated"}), 200


@app.route("/topic/<string:title>", methods=["DELETE"])
@token_required
@admin_required
def delete_topic(title):
    topics_col.delete_one({"title": title})
    return jsonify({"message": "Topic deleted"}), 200




# ------------------ RUN 
# --------------------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    app.run(host="0.0.0.0", port=port, debug=False)
