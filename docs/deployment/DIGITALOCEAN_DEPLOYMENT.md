# DigitalOcean Deployment Guide

## 🇮🇳 Why DigitalOcean for India?

- **Bangalore Datacenter (BLR1)**: Lowest latency for Indian users
- **Managed PostgreSQL**: Available in Bangalore region
- **Cost-effective**: Starting at $241.80/year
- **Easy deployment**: App Platform with GitHub integration

## 💰 Pricing Breakdown

### Basic Setup (Recommended for Start)
- **App Platform Basic**: $5/month ($60/year)
- **PostgreSQL Basic**: $15.15/month ($181.80/year)
- **Total**: $20.15/month (**$241.80/year**)

### Production Setup (For Higher Traffic)
- **App Platform Professional**: $12/month ($144/year)
- **PostgreSQL 2GB**: $30.45/month ($365.40/year)
- **Total**: $42.45/month (**$509.40/year**)

## 🚀 Step-by-Step Deployment

### Step 1: Create DigitalOcean Account
1. Go to [digitalocean.com](https://digitalocean.com)
2. Sign up (get $200 free credit for 60 days)
3. Verify your account

### Step 2: Create Managed PostgreSQL Database
1. Go to **Databases** in DO dashboard
2. Click **Create Database**
3. Choose:
   - **Engine**: PostgreSQL 15
   - **Region**: Bangalore (BLR1)
   - **Size**: Basic (1GB RAM, 1 vCPU) - $15.15/month
   - **Name**: `sunrise-postgres`
4. Click **Create Database**
5. **Save the connection details** (you'll need them)

### Step 3: Deploy App Platform
1. Go to **Apps** in DO dashboard
2. Click **Create App**
3. Choose **GitHub** as source
4. Select your repository: `sunrise-school-management`
5. Configure:
   - **Branch**: main
   - **Autodeploy**: Enable
   - **Region**: Bangalore (BLR1)

### Step 4: Configure Environment Variables
In the App Platform settings, add these environment variables:

```bash
DATABASE_URL=postgresql://username:password@host:port/database
SECRET_KEY=your-super-secret-key-here-make-it-long-and-random
ENVIRONMENT=production
```

### Step 5: Configure Build Settings

**Backend Service:**
- **Source Directory**: `/sunrise-backend-fastapi`
- **Build Command**: `pip install -r requirements.txt`
- **Run Command**: `uvicorn main:app --host 0.0.0.0 --port 8080`
- **Instance Size**: Basic ($5/month)

**Frontend Service:**
- **Source Directory**: `/sunrise-school-frontend`
- **Build Command**: `npm ci && npm run build`
- **Output Directory**: `/build`
- **Type**: Static Site

### Step 6: Deploy
1. Click **Create Resources**
2. Wait for deployment (5-10 minutes)
3. Your app will be available at: `https://your-app-name.ondigitalocean.app`

## 🔧 Post-Deployment Setup

### Database Migration
1. Go to your app's **Console** tab
2. Run: `python setup_database.py`
3. This will create all necessary tables

### Custom Domain (Optional)
1. Go to **Settings** → **Domains**
2. Add your custom domain
3. Update DNS records as instructed

## 📊 Monitoring & Scaling

### Built-in Monitoring
- **Metrics**: CPU, Memory, Request count
- **Logs**: Real-time application logs
- **Alerts**: Set up billing and performance alerts

### Scaling Options
- **Vertical**: Upgrade instance size
- **Horizontal**: Add more instances (Professional plan)
- **Database**: Upgrade to higher tiers as needed

## 🔒 Security Features

- **Automatic HTTPS**: SSL certificates managed automatically
- **DDoS Protection**: Built-in protection
- **Private Networking**: Database accessible only from your app
- **Firewall**: Configure access rules

## 💡 Cost Optimization Tips

1. **Start Small**: Begin with Basic plan, scale as needed
2. **Monitor Usage**: Use DO's billing alerts
3. **Database Sizing**: Start with 1GB, upgrade when needed
4. **Static Assets**: Use DO Spaces for large files (optional)

## 🆚 Comparison with Render

| Feature | DigitalOcean | Render |
|---------|-------------|--------|
| **India Presence** | ✅ Bangalore DC | ❌ Singapore (higher latency) |
| **Yearly Cost** | $241.80 | $756 |
| **Managed DB** | ✅ PostgreSQL | ✅ PostgreSQL |
| **Free Tier** | ✅ $200 credit | ✅ Limited free |
| **Scaling** | ✅ Easy | ✅ Easy |

## 🎯 Why Choose DigitalOcean for Your School System

1. **Cost-effective**: 68% cheaper than Render
2. **India-optimized**: Bangalore datacenter
3. **Comprehensive**: Full-stack hosting
4. **Reliable**: 99.99% uptime SLA
5. **Support**: 24/7 support available

## 🚨 Important Notes

- **Database Backups**: Automatic daily backups included
- **SSL Certificates**: Automatically managed
- **GitHub Integration**: Auto-deploy on push
- **Environment Variables**: Securely managed
- **Logs**: 7-day retention on basic plan

## 📞 Need Help?

- **Documentation**: [docs.digitalocean.com](https://docs.digitalocean.com)
- **Community**: [community.digitalocean.com](https://community.digitalocean.com)
- **Support**: Available 24/7 via ticket system
- **Sales**: Contact for enterprise needs

Your school management system will be running smoothly on DigitalOcean's Bangalore infrastructure! 🎉
