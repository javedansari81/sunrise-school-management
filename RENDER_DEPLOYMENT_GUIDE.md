# 🚀 Complete Render.com Deployment Guide
## Sunrise School Management System - India Optimized

This guide provides step-by-step instructions to deploy your complete school management system on Render.com with proper naming conventions, India-optimized settings, and GitHub integration.

## 🌏 India-Optimized Configuration

**Recommended Region**: **Singapore** (closest to India for best performance)
- Latency: ~50-80ms from major Indian cities
- Alternative: Frankfurt (EU) if Singapore is unavailable

## 💰 Cost Breakdown

### Free Tier (Testing & Development)
- **Web Service**: Free (sleeps after 15min inactivity)
- **PostgreSQL**: Free (1GB storage, 1 month retention)
- **Static Site**: Free
- **Total**: **FREE**

### Production Tier (Recommended)
- **Backend Service**: $7/month (Starter plan)
- **PostgreSQL**: $7/month (10GB storage, 90-day retention)
- **Frontend**: Free (Static site)
- **Total**: $14/month (**$168/year**)

## 📋 Prerequisites

1. **GitHub Repository**: Ensure your code is pushed to GitHub
2. **Render Account**: Sign up at [render.com](https://render.com) with GitHub
3. **Repository Access**: Make sure Render can access your repository

## 🏗️ Step 1: Create Render Account & Connect GitHub

1. **Sign Up:**
   - Go to [render.com](https://render.com)
   - Click **"Get Started for Free"**
   - Select **"Sign up with GitHub"**

2. **Connect Repository:**
   - Authorize Render to access your GitHub account
   - Select your repository: `sunrise-school-management`
   - Grant necessary permissions

## 🗄️ Step 2: Deploy PostgreSQL Database

1. **Create Database:**
   - In Render Dashboard, click **"New +"**
   - Select **"PostgreSQL"**

2. **Database Configuration:**
   ```
   Name: sunrise-school-postgres-db
   Database: sunrise_school_db
   User: sunrise_admin
   PostgreSQL Version: 15 (recommended)
   Region: Singapore (recommended for India)
   Plan: Free (testing) or Starter ($7/month for production)
   ```

3. **Deploy Database:**
   - Click **"Create Database"**
   - Wait 2-3 minutes for provisioning
   - **Important**: Copy and save the connection details

4. **Get Database URL:**
   - Go to your database dashboard
   - Copy the **"External Database URL"**
   - Format: `postgresql://username:password@host:port/database`
   - **Save this URL** - you'll need it for the backend service

## 🚀 Step 3: Deploy Backend Service

1. **Create Web Service:**
   - In Render Dashboard, click **"New +"**
   - Select **"Web Service"**
   - Choose **"Build and deploy from a Git repository"**
   - Select your repository: `sunrise-school-management`

2. **Backend Service Configuration:**
   ```
   Name: sunrise-school-backend-api
   Region: Singapore (same as database)
   Branch: main
   Root Directory: sunrise-backend-fastapi
   Runtime: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: uvicorn main:app --host 0.0.0.0 --port 10000
   Plan: Free (testing) or Starter ($7/month for production)
   ```

3. **Environment Variables Setup:**
   Click **"Advanced"** → **"Add Environment Variable"**

   **Required Environment Variables:**
   | Key | Value | Notes |
   |-----|-------|-------|
   | `DATABASE_URL` | `[Your PostgreSQL URL from Step 2]` | Copy from database dashboard |
   | `SECRET_KEY` | `sunrise-school-secret-key-2024-production-india` | Change this for security |
   | `ENVIRONMENT` | `production` | Sets production mode |
   | `BACKEND_CORS_ORIGINS` | `https://sunrise-school-frontend-web.onrender.com` | Update after frontend deployment |

4. **Deploy Backend:**
   - Click **"Create Web Service"**
   - Wait 5-10 minutes for deployment
   - **Note the backend URL**: `https://sunrise-school-backend-api.onrender.com`

## 🎨 Step 4: Deploy Frontend Service

1. **Create Static Site:**
   - Click **"New +"** → **"Static Site"**
   - Choose **"Build and deploy from a Git repository"**
   - Select your repository: `sunrise-school-management`

2. **Frontend Configuration:**
   ```
   Name: sunrise-school-frontend-web
   Branch: main
   Root Directory: sunrise-school-frontend
   Build Command: npm ci && npm run build
   Publish Directory: build
   Auto-Deploy: Yes
   ```

3. **Environment Variables (Build Time):**
   | Key | Value | Notes |
   |-----|-------|-------|
   | `REACT_APP_API_URL` | `https://sunrise-school-backend-api.onrender.com/api/v1` | Your backend URL |
   | `REACT_APP_SCHOOL_NAME` | `Sunrise National Public School` | School branding |

4. **Deploy Frontend:**
   - Click **"Create Static Site"**
   - Wait 5-10 minutes for deployment
   - **Note the frontend URL**: `https://sunrise-school-frontend-web.onrender.com`

## � Step 5: Update Cross-Service URLs

1. **Update Backend CORS Settings:**
   - Go to backend service: `sunrise-school-backend-api`
   - Click **"Environment"** tab
   - Update `BACKEND_CORS_ORIGINS` with your actual frontend URL:
   ```
   https://sunrise-school-frontend-web.onrender.com
   ```
   - Click **"Save Changes"**

2. **Update Frontend API URL (if needed):**
   - Go to frontend service: `sunrise-school-frontend-web`
   - Click **"Environment"** tab
   - Verify `REACT_APP_API_URL` is correct:
   ```
   https://sunrise-school-backend-api.onrender.com/api/v1
   ```
   - Click **"Save Changes"** if modified

3. **Redeploy Services:**
   - Both services will automatically redeploy after environment changes
   - Wait for both deployments to complete

## �️ Step 6: Initialize Database with Sample Data

1. **Method 1: Using Backend Shell (Recommended):**
   - Go to your backend service dashboard: `sunrise-school-backend-api`
   - Click **"Shell"** tab
   - Run these commands:
   ```bash
   cd /opt/render/project/src
   python setup_database.py
   ```

2. **Method 2: Automatic Setup (Alternative):**
   - In your backend service settings
   - Go to **"Settings"** → **"Build & Deploy"**
   - Update **"Build Command"** to:
   ```bash
   pip install -r requirements.txt && python setup_database.py
   ```
   - This will run database setup on every deployment

## 🎯 Step 7: Test Your Deployment

1. **Access Your Application:**
   - **Frontend**: `https://sunrise-school-frontend-web.onrender.com`
   - **Backend API**: `https://sunrise-school-backend-api.onrender.com`
   - **API Documentation**: `https://sunrise-school-backend-api.onrender.com/docs`

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

4. **Performance Check:**
   - Test loading speed from India (should be ~50-80ms from Singapore region)
   - Verify all API endpoints work correctly
   - Check responsive design on mobile devices

## 🌐 Step 8: Custom Domain Setup (Optional)

### For Frontend (Static Site):
1. **Purchase Domain:**
   - Buy a domain from any registrar (GoDaddy, Namecheap, etc.)
   - Recommended: `yourschoolname.edu.in` or `yourschoolname.com`

2. **Add Custom Domain in Render:**
   - Go to frontend service: `sunrise-school-frontend-web`
   - Click **"Settings"** → **"Custom Domains"**
   - Click **"Add Custom Domain"**
   - Enter your domain: `school.yourdomain.com`

3. **Update DNS Records:**
   - In your domain registrar's DNS settings:
   ```
   Type: CNAME
   Name: school (or www)
   Value: sunrise-school-frontend-web.onrender.com
   TTL: 300 (or default)
   ```

4. **SSL Certificate:**
   - Render automatically provisions SSL certificates
   - Wait 5-10 minutes for certificate generation
   - Your site will be available at `https://school.yourdomain.com`

### For Backend API (Optional):
1. **Add API Subdomain:**
   - Add another custom domain: `api.yourdomain.com`
   - Point to: `sunrise-school-backend-api.onrender.com`

2. **Update Frontend Environment:**
   - Update `REACT_APP_API_URL` to use your custom domain
   - Redeploy frontend service

## 📊 Step 9: Monitoring & Performance

### Built-in Render Features:
- **Automatic HTTPS**: SSL certificates managed automatically
- **Health Checks**: Automatic service monitoring
- **Real-time Logs**: Access logs from service dashboards
- **Metrics**: Performance monitoring and usage statistics
- **Auto-scaling**: Handles traffic spikes (paid plans)

### India-Specific Optimizations:
- **CDN**: Automatic global CDN for faster static asset delivery
- **Singapore Region**: Optimal latency for Indian users
- **Compression**: Automatic gzip compression enabled

## 🚨 Troubleshooting Guide

### Common Issues & Solutions:

1. **Backend Service Not Starting:**
   ```bash
   # Check build logs in Render dashboard
   # Common fixes:
   - Verify requirements.txt includes all dependencies
   - Ensure main.py exists in sunrise-backend-fastapi/
   - Check Python version compatibility (3.11+)
   ```

2. **Database Connection Failed:**
   ```bash
   # Verify DATABASE_URL format:
   postgresql://username:password@host:port/database

   # Ensure both database and backend are in Singapore region
   # Check database status in Render dashboard
   ```

3. **Frontend Build Errors:**
   ```bash
   # Check build logs for npm errors
   # Common fixes:
   - Verify package.json is correct
   - Ensure Node.js version compatibility
   - Check for missing dependencies
   ```

4. **CORS Errors:**
   ```bash
   # Update BACKEND_CORS_ORIGINS in backend service
   # Must match exact frontend URL
   # Redeploy backend after changes
   ```

5. **Slow Loading from India:**
   ```bash
   # Verify services are in Singapore region
   # Check network latency using browser dev tools
   # Consider upgrading to paid plans for better performance
   ```

## 💡 Production Tips

### Free Tier Considerations:
- **Sleep Mode**: Services sleep after 15 minutes of inactivity
- **Cold Start**: First request after sleep takes 30+ seconds
- **Database**: 1GB storage limit, 1-month retention
- **Recommendation**: Upgrade to paid plans for production

### Security Best Practices:
- **Change SECRET_KEY**: Use a strong, unique secret key
- **Environment Variables**: Never commit secrets to GitHub
- **Database**: Use strong passwords and limit access
- **HTTPS**: Always use HTTPS URLs (automatic with Render)

### Backup Strategy:
- **Database**: Paid plans include automatic backups
- **Code**: Keep GitHub repository updated
- **Environment Variables**: Document all required variables

## 🎉 Deployment Complete!

### Your Live Application:
- **🌐 Frontend**: `https://sunrise-school-frontend-web.onrender.com`
- **🔧 Backend API**: `https://sunrise-school-backend-api.onrender.com`
- **📚 API Documentation**: `https://sunrise-school-backend-api.onrender.com/docs`
- **🗄️ Database**: `sunrise-school-postgres-db` (Singapore region)

### Next Steps:
1. ✅ **Test all functionality** with provided sample data
2. 🌐 **Set up custom domain** (optional but recommended)
3. 💰 **Upgrade to paid plans** for production use
4. 👥 **Add real student and teacher data**
5. 📊 **Monitor performance** and usage patterns
6. 🔒 **Implement additional security measures** as needed

### Support & Maintenance:
- **Render Dashboard**: Monitor service health and logs
- **GitHub Integration**: Automatic deployments on code changes
- **Scaling**: Upgrade plans as user base grows
- **Updates**: Keep dependencies updated regularly

**🏫 Your Sunrise School Management System is now live and optimized for Indian users! ✨**

---

**Need Help?**
- Check Render documentation: [render.com/docs](https://render.com/docs)
- Review application logs in service dashboards
- Test API endpoints using the built-in documentation
