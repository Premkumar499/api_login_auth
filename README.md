---
title: Flask Auth API
emoji: 🔐
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
app_port: 7860
---

# Flask Authentication API

A secure Flask-based authentication API with OTP verification and JWT authentication.

## 🚀 Quick Start - Deploy to Hugging Face

### Step 1: Create a New Space

1. Go to [Hugging Face Spaces](https://huggingface.co/spaces)
2. Click **"Create new Space"**
3. Choose:
   - Space name: `your-api-name`
   - License: Apache 2.0 (or your choice)
   - **SDK: Docker** (Important!)
   - Visibility: Public or Private

### Step 2: Push Your Code

```bash
# Clone your space repository
git clone https://huggingface.co/spaces/YOUR_USERNAME/your-api-name
cd your-api-name

# Copy all files from this backend folder
cp /path/to/backend/* .

# Push to Hugging Face
git add .
git commit -m "Initial deployment"
git push
```

### Step 3: Set Environment Variables (REQUIRED!)

Go to your Space settings and add these **Secrets**:

```
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
EMAIL_ADDRESS=your-email@gmail.com
EMAIL_PASSWORD=your-gmail-app-password
JWT_SECRET=your-random-secret-key-min-32-chars
```

**Important Notes:**
- For Gmail, enable 2FA and generate an [App Password](https://myaccount.google.com/apppasswords)
- For MongoDB, use [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) free tier
- JWT_SECRET should be a long random string (32+ characters)

### Step 4: Wait for Build

Your Space will automatically build and deploy. Check the **Logs** tab for any errors.

## 🔗 Your API URL

Once deployed, your API will be available at:
```
https://YOUR_USERNAME-your-api-name.hf.space
```

Test it:
```bash
curl https://YOUR_USERNAME-your-api-name.hf.space/
```

## 📚 API Endpoints

### 🏠 Root
- `GET /` - API information and available endpoints
- `GET /health` - Health check

### 🔐 Authentication
- `POST /auth/signup` - Register with email and name (sends OTP)
- `POST /auth/verify-otp` - Verify OTP code
- `POST /auth/set-password` - Set password after OTP verification
- `POST /auth/login` - Login with email and password (returns JWT token)
- `POST /auth/forgot-password` - Request password reset OTP
- `POST /auth/verify-reset-otp` - Verify password reset OTP
- `POST /auth/reset-password` - Reset password with verified OTP

### 👤 User (Protected Routes - Requires Token)
- `GET /profile` - Get user profile

### 📚 Content
- `GET /levels` - Get all learning levels
- `GET /topics/<level>` - Get topics for a specific level

### 👨‍💼 Admin (Protected Routes - Requires Admin Role)
- `GET /admin/stats` - Dashboard statistics
- `GET /admin/users` - List all users
- `POST /topic` - Add new topic
- `PUT /admin/make-admin` - Promote user to admin
- `PUT /admin/remove-admin` - Remove admin role
- `DELETE /admin/delete-user` - Delete a user
- And more...

## 📝 Example Usage

### 1. Sign Up
```bash
curl -X POST https://YOUR-SPACE.hf.space/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","name":"John Doe"}'
```

### 2. Verify OTP (check your email)
```bash
curl -X POST https://YOUR-SPACE.hf.space/auth/verify-otp \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","otp":"123456"}'
```

### 3. Set Password
```bash
curl -X POST https://YOUR-SPACE.hf.space/auth/set-password \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"securepass123"}'
```

### 4. Login
```bash
curl -X POST https://YOUR-SPACE.hf.space/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"securepass123"}'
```

Response:
```json
{
  "message": "Login successful",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "name": "John Doe",
  "email": "user@example.com",
  "role": "user"
}
```

### 5. Access Protected Route
```bash
curl -X GET https://YOUR-SPACE.hf.space/profile \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## 🛠️ Troubleshooting

### "Not Found" Error
- Check if your Space is **running** (green status)
- Verify you're using the correct URL format: `https://USERNAME-SPACENAME.hf.space`
- Make sure the Space uses **Docker SDK** (not Gradio or Streamlit)
- Check the Space Logs for errors

### "Build Failed" Error
- Ensure all files are pushed to the repository
- Check if `requirements.txt` is present
- Verify `Dockerfile` syntax
- Check build logs for specific error messages

### "Internal Server Error"
- Verify all environment variables are set in Space Settings → Repository secrets
- Check MongoDB connection string is correct
- Verify Gmail App Password is valid
- Check Space logs for detailed error messages

### OTP Email Not Sending
- Use Gmail App Password (not regular password)
- Enable 2FA on Gmail account first
- Check email address and password in environment variables
- Some email providers may block automated emails

## 🔧 Local Development

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file with your credentials
cp .env.example .env  # Edit with your values

# Run locally
python app.py
```

Access at: `http://localhost:7860`

## 📦 Tech Stack
- **Flask** - Web framework
- **MongoDB Atlas** - Database
- **JWT** - Authentication
- **Gmail SMTP** - Email delivery
- **Gunicorn** - WSGI server
- **Docker** - Containerization

## 🔐 Security Notes
- Never commit `.env` file to git
- Use strong JWT_SECRET (32+ characters)
- Use Gmail App Passwords, not account password
- First user is automatically assigned admin role
- Tokens expire after 24 hours (configurable)

## 📄 License
Apache 2.0
