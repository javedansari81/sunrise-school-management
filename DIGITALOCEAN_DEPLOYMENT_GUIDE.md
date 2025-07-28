# 🚀 Complete DigitalOcean Deployment Guide
## Sunrise School Management System

This guide will help you deploy your complete school management system on DigitalOcean with managed PostgreSQL database and sample data.

## 📋 Prerequisites

- DigitalOcean account (get $200 free credit)
- GitHub repository: `https://github.com/javedansari81/sunrise-school-management`
- Basic knowledge of Docker and environment variables

## 💰 Cost Breakdown (Basic Plan)

- **App Platform Basic**: $5/month ($60/year)
- **PostgreSQL Basic (1GB)**: $15.15/month ($181.80/year)
- **Total**: $20.15/month (**$241.80/year**)

## 🏗️ Step 1: Create DigitalOcean Account

1. Go to [digitalocean.com](https://digitalocean.com)
2. Sign up and get $200 free credit for 60 days
3. Verify your account and add payment method

## 🗄️ Step 2: Create Managed PostgreSQL Database

1. **Navigate to Databases**
   - Go to DigitalOcean dashboard
   - Click **"Databases"** in the left sidebar
   - Click **"Create Database"**

2. **Configure Database**
   - **Engine**: PostgreSQL 15
   - **Region**: Bangalore (BLR1) - for Indian users
   - **Size**: Basic (1GB RAM, 1 vCPU) - $15.15/month
   - **Database Name**: `sunrise_school`
   - **Cluster Name**: `sunrise-postgres`

3. **Create Database**
   - Click **"Create Database"**
   - Wait 3-5 minutes for provisioning

4. **Save Connection Details**
   - Copy the **Connection String** (DATABASE_URL)
   - Format: `postgresql://username:password@host:port/database`
   - Save this - you'll need it for environment variables

## 🚀 Step 3: Deploy Application

### Option A: Using App Platform (Recommended)

1. **Create App**
   - Go to **"Apps"** in DigitalOcean dashboard
   - Click **"Create App"**
   - Choose **"GitHub"** as source

2. **Connect Repository**
   - Select: `javedansari81/sunrise-school-management`
   - Branch: `main`
   - Enable **"Autodeploy on push"**

3. **Configure Services**
   - DigitalOcean will auto-detect your app structure
   - It should find both frontend and backend services
   - Choose **Bangalore (BLR1)** region

4. **Set Environment Variables**
   ```bash
   # Backend Environment Variables
   DATABASE_URL=postgresql://username:password@host:port/database
   SECRET_KEY=your-super-secret-key-here-make-it-long-and-random-at-least-32-characters
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ENVIRONMENT=production
   
   # Frontend Environment Variables (Build Time)
   REACT_APP_API_URL=https://your-app-name.ondigitalocean.app/api/v1
   REACT_APP_SCHOOL_NAME=Sunrise National Public School
   ```

5. **Review and Deploy**
   - Review the configuration
   - Click **"Create Resources"**
   - Wait 10-15 minutes for deployment

### Option B: Using Docker Compose (Alternative)

1. **Create Droplet**
   - Choose **Ubuntu 22.04 LTS**
   - Basic plan: $6/month (1GB RAM)
   - Bangalore datacenter

2. **Install Docker**
   ```bash
   # SSH into your droplet
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh
   sudo usermod -aG docker $USER
   ```

3. **Clone Repository**
   ```bash
   git clone https://github.com/javedansari81/sunrise-school-management.git
   cd sunrise-school-management
   ```

4. **Configure Environment**
   ```bash
   cp .env.digitalocean.example .env.digitalocean
   # Edit .env.digitalocean with your database URL and secrets
   ```

5. **Deploy with Docker Compose**
   ```bash
   docker-compose -f docker-compose.digitalocean.yml --env-file .env.digitalocean up -d
   ```

## 🗃️ Step 4: Initialize Database with Sample Data

1. **Access App Console** (App Platform method)
   - Go to your app in DigitalOcean dashboard
   - Click on **"Console"** tab
   - Run the following commands:

   ```bash
   cd /app
   python setup_database.py
   ```

2. **SSH Method** (Droplet method)
   ```bash
   # SSH into your droplet
   cd sunrise-school-management/sunrise-backend-fastapi
   docker exec -it sunrise-backend-do python setup_database.py
   ```

## 🎯 Step 5: Verify Deployment

1. **Check Application**
   - Visit your app URL: `https://your-app-name.ondigitalocean.app`
   - You should see the login page

2. **Test Login Credentials**
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

3. **Verify Sample Data**
   - Login as admin
   - Check Students section (15 students)
   - Check Teachers section (5 teachers)
   - Check Fee Management (fee structures and records)

## 🔧 Post-Deployment Configuration

### Custom Domain (Optional)
1. Go to **Settings** → **Domains**
2. Add your custom domain
3. Update DNS records as instructed
4. SSL certificate will be automatically provisioned

### Environment Variables Management
- Use DigitalOcean's secure environment variables
- Never commit secrets to GitHub
- Rotate secrets regularly

### Monitoring and Logs
- **Metrics**: Monitor CPU, Memory, Request count
- **Logs**: Real-time application logs in dashboard
- **Alerts**: Set up billing and performance alerts

## 🔒 Security Best Practices

1. **Database Security**
   - Database is only accessible from your app
   - Use strong passwords
   - Enable connection pooling

2. **Application Security**
   - HTTPS is automatically enabled
   - Use strong JWT secrets
   - Implement rate limiting

3. **Access Control**
   - Use DigitalOcean teams for access management
   - Enable 2FA on your account
   - Regular security updates

## 📊 Sample Data Included

Your deployment includes:
- **15 Students** across different classes (Class 2 to Class 7)
- **5 Teachers** with different subjects and departments
- **Fee Structures** for all classes with detailed breakdowns
- **Fee Records** with various payment statuses
- **Leave Requests** with different approval statuses
- **Expense Records** for school operations

## 🚨 Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Verify DATABASE_URL format
   - Check database is running
   - Ensure app and database are in same region

2. **Build Failed**
   - Check build logs in DigitalOcean dashboard
   - Verify all dependencies in requirements.txt
   - Check Dockerfile syntax

3. **Frontend Not Loading**
   - Verify REACT_APP_API_URL is correct
   - Check CORS settings
   - Ensure backend is running

### Getting Help
- **Documentation**: [docs.digitalocean.com](https://docs.digitalocean.com)
- **Community**: [community.digitalocean.com](https://community.digitalocean.com)
- **Support**: 24/7 support via ticket system

## 🎉 Success!

Your Sunrise School Management System is now live on DigitalOcean! 

**Next Steps:**
1. Test all functionality with sample data
2. Customize school information
3. Add real student and teacher data
4. Set up regular backups
5. Monitor performance and scale as needed

Your school management system is ready to serve students, teachers, and administrators efficiently! 🏫✨
