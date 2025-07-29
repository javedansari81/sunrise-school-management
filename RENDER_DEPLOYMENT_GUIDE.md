# 🚀 Complete Render.com Deployment Guide
## Sunrise School Management System

This guide will help you deploy your complete school management system on Render.com with PostgreSQL database and sample data.

## 💰 Cost Breakdown

### Free Tier (Great for Testing)
- **Web Service**: Free (with limitations)
- **PostgreSQL**: Free (1GB storage, 1 month retention)
- **Total**: **FREE** for testing

### Paid Tier (Production Ready)
- **Web Service**: $7/month per service
- **PostgreSQL**: $7/month (10GB storage, 90-day retention)
- **Total**: $21/month (**$252/year**)

## 🏗️ Step 1: Create Render Account

1. Go to [render.com](https://render.com)
2. Sign up with GitHub (recommended)
3. Connect your GitHub account

## 🗄️ Step 2: Deploy PostgreSQL Database

1. **In Render Dashboard:**
   - Click **"New +"**
   - Select **"PostgreSQL"**

2. **Configure Database:**
   ```
   Name: sunrise-postgres
   Database: sunrise_school
   User: sunrise_user
   Region: Oregon (US-West) or Frankfurt (EU) - closest to your users
   Plan: Free (for testing) or Starter ($7/month for production)
   ```

3. **Create Database**
   - Click **"Create Database"**
   - Wait 2-3 minutes for provisioning
   - **Save the connection details** - you'll need them!

4. **Get Connection String:**
   - Go to your database dashboard
   - Copy the **"External Database URL"**
   - Format: `postgresql://username:password@host:port/database`

## 🚀 Step 3: Deploy Backend Service

1. **Create Web Service:**
   - Click **"New +"** → **"Web Service"**
   - Connect to GitHub repository: `javedansari81/sunrise-school-management`

2. **Configure Backend:**
   ```
   Name: sunrise-backend
   Region: Same as your database
   Branch: main
   Root Directory: sunrise-backend-fastapi
   Runtime: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: uvicorn main:app --host 0.0.0.0 --port 10000
   Plan: Free (for testing) or Starter ($7/month)
   ```

3. **Environment Variables:**
   Click **"Advanced"** → **"Add Environment Variable"**
   
   | Key | Value |
   |-----|-------|
   | `DATABASE_URL` | `[Your PostgreSQL External URL from Step 2]` |
   | `SECRET_KEY` | `b8f2c9d4e6a1f3g5h7j9k2l4m6n8p0q2r4s6t8u0v2w4x6y8z0a2b4c6d8e0f2g4h6` |
   | `ENVIRONMENT` | `production` |
   | `BACKEND_CORS_ORIGINS` | `https://sunrise-school-frontend.onrender.com` |

4. **Deploy Backend:**
   - Click **"Create Web Service"**
   - Wait 5-10 minutes for deployment

## 🎨 Step 4: Deploy Frontend Service

1. **Create Static Site:**
   - Click **"New +"** → **"Static Site"**
   - Connect to same GitHub repository

2. **Configure Frontend:**
   ```
   Name: sunrise-frontend
   Branch: main
   Root Directory: sunrise-school-frontend
   Build Command: npm ci && npm run build
   Publish Directory: build
   ```

3. **Environment Variables:**
   | Key | Value |
   |-----|-------|
   | `REACT_APP_API_URL` | `https://your-backend-name.onrender.com/api/v1` |
   | `REACT_APP_SCHOOL_NAME` | `Sunrise National Public School` |

4. **Deploy Frontend:**
   - Click **"Create Static Site"**
   - Wait 5-10 minutes for deployment

## 🗃️ Step 5: Initialize Database with Sample Data

1. **Access Backend Service Console:**
   - Go to your backend service dashboard
   - Click **"Shell"** tab
   - Run these commands:

   ```bash
   cd /opt/render/project/src
   python setup_database.py
   ```

2. **Alternative - Use Database Migration:**
   - In your backend service settings
   - Add a **"Deploy Hook"** or **"Build Command"**:
   ```bash
   pip install -r requirements.txt && python setup_database.py
   ```

## 🔧 Step 6: Update CORS Settings

1. **Update Backend Environment Variables:**
   - Go to backend service → **"Environment"**
   - Update `BACKEND_CORS_ORIGINS` with your actual frontend URL:
   ```
   https://your-frontend-name.onrender.com
   ```

2. **Update Frontend API URL:**
   - Go to frontend service → **"Environment"**
   - Update `REACT_APP_API_URL` with your actual backend URL:
   ```
   https://your-backend-name.onrender.com/api/v1
   ```

## 🎯 Step 7: Test Your Deployment

1. **Visit your frontend URL:** `https://your-frontend-name.onrender.com`

2. **Test Login Credentials:**
   ```
   👨‍💼 Admin Login:
   Email: admin@sunriseschool.edu
   Password: admin123
   
   👨‍🏫 Teacher Login:
   Email: teacher@sunriseschool.edu
   Password: admin123
   
   👨‍🎓 Student Login:
   Email: student@sunriseschool.edu
   Password: admin123
   ```

3. **Verify Sample Data:**
   - 15 Students across different classes
   - 5 Teachers with subjects
   - Fee structures and payment records
   - Leave requests and expense tracking

## 🔒 Custom Domain (Optional)

1. **In Frontend Service:**
   - Go to **"Settings"** → **"Custom Domains"**
   - Add your domain (e.g., `school.yourdomain.com`)
   - Update DNS records as instructed
   - SSL certificate will be automatically provisioned

## 📊 Monitoring and Scaling

### Built-in Features:
- **Automatic HTTPS**: SSL certificates managed automatically
- **Auto-scaling**: Handles traffic spikes automatically
- **Health Checks**: Automatic service monitoring
- **Logs**: Real-time application logs
- **Metrics**: Performance monitoring dashboard

### Scaling Options:
- **Vertical**: Upgrade to higher plans for more resources
- **Database**: Upgrade PostgreSQL plan for more storage/performance
- **CDN**: Automatic global CDN for static assets

## 🚨 Troubleshooting

### Common Issues:

1. **Backend Not Starting:**
   - Check build logs for Python errors
   - Verify `requirements.txt` is correct
   - Ensure `main.py` exists in root directory

2. **Database Connection Failed:**
   - Verify DATABASE_URL is correct
   - Check database is running
   - Ensure database and backend are in same region

3. **Frontend Not Loading:**
   - Check build logs for npm errors
   - Verify `package.json` is correct
   - Ensure `build` directory is created

4. **CORS Errors:**
   - Update `BACKEND_CORS_ORIGINS` with correct frontend URL
   - Redeploy backend service after updating

## 💡 Pro Tips

1. **Free Tier Limitations:**
   - Services sleep after 15 minutes of inactivity
   - First request after sleep takes 30+ seconds
   - Upgrade to paid plan for production use

2. **Database Backups:**
   - Paid PostgreSQL plans include automatic backups
   - Free tier has limited backup retention

3. **Environment Variables:**
   - Use Render's secret management for sensitive data
   - Environment variables are encrypted at rest

## 🎉 Success!

Your Sunrise School Management System is now live on Render! 

**Your URLs:**
- **Frontend**: `https://your-frontend-name.onrender.com`
- **Backend API**: `https://your-backend-name.onrender.com`
- **API Docs**: `https://your-backend-name.onrender.com/docs`

**Next Steps:**
1. Test all functionality with sample data
2. Set up custom domain (optional)
3. Upgrade to paid plans for production
4. Add real student and teacher data
5. Monitor performance and usage

Your school management system is ready to serve students, teachers, and administrators! 🏫✨
