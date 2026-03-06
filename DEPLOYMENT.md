# 🚀 Hugging Face Deployment Guide

## Prerequisites

Before deploying, make sure you have:

1. ✅ **Hugging Face Account** - [Sign up here](https://huggingface.co/join)
2. ✅ **MongoDB Atlas Account** - [Free tier here](https://www.mongodb.com/cloud/atlas/register)
3. ✅ **Gmail Account** with App Password - [Generate here](https://myaccount.google.com/apppasswords)
4. ✅ **Git installed** on your machine

---

## 📋 Step-by-Step Deployment

### Step 1: Prepare MongoDB Atlas

1. Go to [MongoDB Atlas](https://cloud.mongodb.com/)
2. Create a new cluster (free M0 tier is fine)
3. Go to **Database Access** → Create a database user
4. Go to **Network Access** → Add IP Address → **Allow Access from Anywhere** (0.0.0.0/0)
5. Click **Connect** → **Connect your application**
6. Copy your connection string:
   ```
   mongodb+srv://username:<password>@cluster.mongodb.net/?retryWrites=true&w=majority
   ```
7. Replace `<password>` with your actual password

### Step 2: Setup Gmail App Password

1. Go to your [Google Account](https://myaccount.google.com/)
2. Enable **2-Step Verification** (if not already enabled)
3. Go to [App Passwords](https://myaccount.google.com/apppasswords)
4. Select **Mail** and **Other (Custom name)**
5. Name it "Hugging Face API" and click **Generate**
6. Copy the 16-character password (no spaces)

### Step 3: Create Hugging Face Space

1. Go to [Hugging Face Spaces](https://huggingface.co/spaces)
2. Click **"Create new Space"**
3. Fill in the details:
   - **Owner**: Your username
   - **Space name**: `api-login-auth` (or your preferred name)
   - **License**: Apache 2.0
   - **Select the Space SDK**: **Docker** ⚠️ IMPORTANT!
   - **Visibility**: Public (or Private if you prefer)
4. Click **Create Space**

### Step 4: Clone and Push Your Code

```bash
# Navigate to your backend folder
cd /home/premkumar/Downloads/vscode/full_stack/backend

# Initialize git if not already done
git init

# Add Hugging Face as remote (replace YOUR_USERNAME and SPACE_NAME)
git remote add hf https://huggingface.co/spaces/YOUR_USERNAME/SPACE_NAME

# Add all files
git add .

# Commit
git commit -m "Initial deployment to Hugging Face"

# Push to Hugging Face
git push hf main
```

**Alternative: Using Hugging Face CLI**
```bash
# Install Hugging Face CLI
pip install huggingface_hub

# Login
huggingface-cli login

# Clone your space
git clone https://huggingface.co/spaces/YOUR_USERNAME/SPACE_NAME
cd SPACE_NAME

# Copy files
cp -r /home/premkumar/Downloads/vscode/full_stack/backend/* .

# Push
git add .
git commit -m "Initial deployment"
git push
```

### Step 5: Configure Environment Variables

1. Go to your Space page on Hugging Face
2. Click **Settings** (⚙️ icon at the top)
3. Scroll down to **Repository secrets**
4. Click **"New secret"** and add each of these:

| Name | Value | Example |
|------|-------|---------|
| `MONGO_URI` | Your MongoDB connection string | `mongodb+srv://user:pass@cluster.mongodb.net/...` |
| `EMAIL_ADDRESS` | Your Gmail address | `your-email@gmail.com` |
| `EMAIL_PASSWORD` | Gmail App Password (16 chars) | `abcd efgh ijkl mnop` (no spaces) |
| `JWT_SECRET` | Random string (32+ characters) | `your-super-secret-jwt-key-here-min-32-chars` |

⚠️ **Important**: Click **"Add secret"** after each entry!

### Step 6: Wait for Build

1. Go to the **Logs** tab on your Space
2. Watch the build process
3. It should show:
   ```
   Building Docker image...
   Successfully built...
   Running on http://0.0.0.0:7860
   ```
4. Once you see "Running", your API is live! 🎉

---

## 🔗 Access Your API

Your API will be available at:
```
https://YOUR_USERNAME-SPACE_NAME.hf.space
```

Example:
```
https://premkumar499-api-login-auth.hf.space
```

### Test Your API

```bash
# Health Check
curl https://YOUR-SPACE-URL.hf.space/health

# Get API Info
curl https://YOUR-SPACE-URL.hf.space/

# Sign Up
curl -X POST https://YOUR-SPACE-URL.hf.space/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","name":"Test User"}'
```

---

## 🐛 Common Issues & Fixes

### Issue: Space shows "Building" forever
**Solution**: 
- Check Logs tab for errors
- Verify Dockerfile syntax
- Make sure all files are pushed

### Issue: "Internal Server Error"
**Solution**:
- Check if all 4 environment variables are set
- Verify MongoDB connection string (test it locally first)
- Check Gmail App Password is correct (16 characters, no spaces)
- Look at detailed logs in the Logs tab

### Issue: "Not Found" error
**Solution**:
- Make sure Space is **Running** (green status)
- Check you're using correct URL: `https://USERNAME-SPACENAME.hf.space`
- Verify SDK is set to **Docker** (not Gradio/Streamlit)
- Try accessing `/health` endpoint first

### Issue: OTP emails not sending
**Solution**:
- Use Gmail App Password, NOT your regular password
- Enable 2FA on Gmail first
- Remove spaces from App Password
- Check EMAIL_ADDRESS and EMAIL_PASSWORD secrets are correct
- Try sending a test email locally first

### Issue: MongoDB connection failed
**Solution**:
- Verify connection string format
- Check Network Access allows 0.0.0.0/0
- Verify database user has correct permissions
- Test connection string locally first

### Issue: Build fails with "requirements.txt not found"
**Solution**:
- Make sure all files are committed and pushed
- Check file names (case-sensitive)
- Verify files are in root directory of repo

---

## 🔄 Updating Your Deployed API

Whenever you make changes:

```bash
cd /home/premkumar/Downloads/vscode/full_stack/backend

# Make your changes
# ...

# Commit and push
git add .
git commit -m "Update: description of changes"
git push hf main
```

The Space will automatically rebuild and redeploy!

---

## 🔐 Security Best Practices

1. ✅ Never commit `.env` file to git
2. ✅ Use strong, unique JWT_SECRET (32+ characters)
3. ✅ Use Gmail App Passwords, not account password
4. ✅ Keep MongoDB credentials secure
5. ✅ Consider setting Space to Private if handling sensitive data
6. ✅ Regularly rotate your JWT_SECRET and passwords
7. ✅ Monitor your Space logs for unauthorized access

---

## 📊 Monitoring Your API

1. **Usage Stats**: Check your Space page for visitor stats
2. **Logs**: Monitor the Logs tab for errors and requests
3. **MongoDB Atlas**: Check database metrics and connections
4. **Gmail**: Monitor sent emails quota (2000/day for free Gmail)

---

## 🎯 Next Steps

- [ ] Test all API endpoints
- [ ] Set up a frontend to consume the API
- [ ] Add API documentation (Swagger/OpenAPI)
- [ ] Set up monitoring alerts
- [ ] Consider upgrading to Hugging Face Pro for better resources
- [ ] Implement rate limiting for production use

---

## 📞 Need Help?

- **Hugging Face Docs**: https://huggingface.co/docs/hub/spaces
- **MongoDB Docs**: https://docs.mongodb.com/
- **Flask Docs**: https://flask.palletsprojects.com/

---

## ✅ Deployment Checklist

Before going live, verify:

- [ ] All environment variables are set and correct
- [ ] MongoDB connection works
- [ ] Email sending works (test OTP)
- [ ] JWT token generation works
- [ ] All API endpoints respond correctly
- [ ] CORS is configured for your frontend domain
- [ ] Space build completes successfully
- [ ] Health check endpoint returns 200 OK
- [ ] Test signup → OTP → set password → login flow

---

**Your API is now live on Hugging Face! 🎉**
