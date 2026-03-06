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

A secure Flask-based authentication API with the following features:

## Features
- 🔒 User registration with OTP verification via email
- 🔑 JWT token-based authentication
- 📧 Gmail SMTP for OTP delivery
- 🗄️ MongoDB Atlas for data storage
- 👥 Role-based access control (admin/user)

## API Endpoints

### Authentication
- `POST /auth/signup` - Register with email and name
- `POST /auth/verify-otp` - Verify OTP sent to email
- `POST /auth/set-password` - Set password after OTP verification
- `POST /auth/login` - Login with email and password
- `POST /auth/forgot-password` - Request password reset
- `POST /auth/reset-password` - Reset password with OTP

## Environment Variables

Set these in your Hugging Face Space settings:

```
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
EMAIL_ADDRESS=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
JWT_SECRET=your-secret-key-here
```

## Usage

Base URL: `https://your-space-name.hf.space`

Example signup request:
```bash
curl -X POST https://your-space-name.hf.space/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","name":"John Doe"}'
```

## Tech Stack
- Flask 3.1.3
- PyMongo 4.16.0
- PyJWT 2.11.0
- Gunicorn 25.1.0
# api_login_auth
