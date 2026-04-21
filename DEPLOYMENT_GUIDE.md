# FarmersConnect Deployment Guide

This guide covers deploying FarmersConnect to various cloud platforms.

## Prerequisites

- Application code pushed to GitHub
- Pre-trained ML models in `models/` directory
- Environment variables configured

## 1. Deploy on Render.com (Recommended)

### Step 1: Prepare Repository
```bash
# Push code to GitHub
git add .
git commit -m "Initial commit"
git push origin main
```

### Step 2: Create Render Account
- Visit https://render.com
- Sign up with GitHub account
- Authorize Render to access your repositories

### Step 3: Create Render PostgreSQL Database
1. Dashboard → New → PostgreSQL
2. Name: `farmerconnect-db`
3. Region: Choose closest to your location
4. Copy Internal Database URL

### Step 4: Create Web Service
1. Dashboard → New → Web Service
2. Connect your GitHub repository
3. Service name: `farmerconnect`
4. Environment: `Python 3.11`
5. Build command: `pip install -r requirements.txt`
6. Start command: `gunicorn app:app`

### Step 5: Add Environment Variables
In Render Dashboard → Service → Environment:
```
FLASK_ENV=production
SECRET_KEY=<generate-strong-key>
DATABASE_URL=<postgresql-url-from-step-3>
SESSION_COOKIE_SECURE=true
```

### Step 6: Deploy
Click "Deploy" button and wait for deployment to complete.

**Live URL**: https://farmerconnect.onrender.com (example)

---

## 2. Deploy on Railway

### Step 1: Install Railway CLI
```bash
npm install -g @railway/cli
# OR
curl -fsSL railway.app/install.sh | sh
```

### Step 2: Login & Initialize
```bash
railway login
railway init
```

### Step 3: Add PostgreSQL
```bash
railway add
# Select PostgreSQL
```

### Step 4: Configure Environment
```bash
railway variables set FLASK_ENV=production
railway variables set SECRET_KEY=<strong-key>
railway variables set SESSION_COOKIE_SECURE=true
```

### Step 5: Deploy
```bash
railway up
```

**View logs**: `railway logs`
**View URL**: `railway open`

---

## 3. Deploy on AWS (EC2 + RDS)

### Architecture
```
┌─────────────────┐
│   Load Balancer │
└────────┬────────┘
         │
    ┌────┴────┐
    │  EC2    │
    │(Flask + │
    │Gunicorn)│
    └────┬────┘
         │
    ┌────┴────┐
    │   RDS   │
    │(PostgreSQL)
    └─────────┘
```

### Step 1: Create RDS PostgreSQL Database
1. AWS Console → RDS → Create Database
2. Engine: PostgreSQL 14+
3. DB instance identifier: `farmerconnect-db`
4. Master username: `postgres`
5. Create a strong password
6. Save endpoint URL

### Step 2: Create EC2 Instance
1. AWS Console → EC2 → Launch Instance
2. AMI: Ubuntu Server 22.04 LTS
3. Instance type: t2.micro (free tier)
4. Security group: Allow HTTP (80), HTTPS (443), SSH (22), Custom TCP 5000

### Step 3: SSH into EC2
```bash
ssh -i your-key-pair.pem ubuntu@your-instance-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install python3-pip python3-venv postgresql-client -y
```

### Step 4: Clone and Setup Application
```bash
cd /home/ubuntu
git clone https://github.com/yourusername/FarmersConnect.git
cd FarmersConnect

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install requirements
pip install -r requirements.txt

# Create .env file
nano .env
# Add:
# FLASK_ENV=production
# SECRET_KEY=<your-secret>
# DATABASE_URL=postgresql://postgres:password@your-rds-endpoint:5432/farmerconnect
```

### Step 5: Initialize Database
```bash
python app.py init-db
```

### Step 6: Setup Gunicorn Service
```bash
# Create systemd service
sudo nano /etc/systemd/system/farmerconnect.service

# Content:
[Unit]
Description=FarmersConnect Flask Application
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/FarmersConnect
ExecStart=/home/ubuntu/FarmersConnect/venv/bin/gunicorn --workers 4 --bind 0.0.0.0:5000 app:app
Restart=always

[Install]
WantedBy=multi-user.target

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable farmerconnect
sudo systemctl start farmerconnect
```

### Step 7: Setup Nginx Reverse Proxy
```bash
sudo apt install nginx -y

# Create nginx config
sudo nano /etc/nginx/sites-available/farmerconnect

# Content:
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static {
        alias /home/ubuntu/FarmersConnect/static;
    }
}

# Enable site
sudo ln -s /etc/nginx/sites-available/farmerconnect /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Step 8: SSL Certificate (Let's Encrypt)
```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com
```

---

## 4. Deploy on PythonAnywhere

### Step 1: Create Account
- Visit https://www.pythonanywhere.com
- Sign up (free account available)

### Step 2: Upload Code
1. Web tab → Add a new web app
2. Choose Python 3.11 + Flask
3. Upload code via Git or file browser

### Step 3: Set Virtual Environment
1. Web tab → Virtualenv section
2. Create: `/home/yourusername/.virtualenvs/farmerconnect`
3. Activate and install: `pip install -r requirements.txt`

### Step 4: Configure WSGI
Web tab → WSGI configuration file:

```python
import sys
path = '/home/yourusername/FarmersConnect'
if path not in sys.path:
    sys.path.append(path)

from app import create_app
app = create_app()
```

### Step 5: Set Environment Variables
Web tab → Environment variables:
```
FLASK_ENV=production
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://...
```

### Step 6: Reload Web App
Click "Reload yourusername.pythonanywhere.com" button.

---

## 5. Deploy on Heroku (Deprecated Platform)

**Note**: Heroku's free tier is no longer available (Nov 2022). Use alternatives above.

If using Heroku paid:
```bash
heroku login
heroku create farmerconnect
heroku addons:create heroku-postgresql:standard-0
git push heroku main
heroku config:set FLASK_ENV=production
```

---

## Database Migration for Production

### Create PostgreSQL Database
```bash
# Local development
export DATABASE_URL="postgresql://user:password@localhost:5432/farmerconnect_dev"
python app.py init-db

# Production (via deployment platform)
# Database URL automatically set in environment variables
```

### Backup Data
```bash
# From PostgreSQL
pg_dump -U username -h host -d database > backup.sql

# Restore
psql -U username -h host -d database < backup.sql
```

---

## Performance Optimization for Production

### 1. Enable Caching
```python
# In config.py
SEND_FILE_MAX_AGE_DEFAULT = 31536000  # 1 year
```

### 2. Database Connection Pooling
```python
# In config.py
SQLALCHEMY_ENGINE_OPTIONS = {
    "pool_size": 10,
    "pool_recycle": 3600,
    "pool_pre_ping": True,
}
```

### 3. Compress Static Assets
```bash
pip install flask-compress
```

### 4. Enable GZIP Compression in Nginx
```nginx
gzip on;
gzip_types text/plain text/css text/javascript application/json;
```

---

## Monitoring & Logging

### 1. Application Logs
```bash
# On Render
render logs farmerconnect

# On Railway
railway logs

# On EC2
sudo journalctl -u farmerconnect -f
```

### 2. Database Monitoring
- Render: Dashboard → Database → Metrics
- Railway: Dashboard → Logs
- AWS RDS: CloudWatch metrics

### 3. Application Monitoring
- Sentry for error tracking
- New Relic for performance monitoring
- CloudWatch for AWS metrics

---

## CI/CD Pipeline with GitHub Actions

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Render

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to Render
        env:
          RENDER_DEPLOY_HOOK: ${{ secrets.RENDER_DEPLOY_HOOK }}
        run: curl $RENDER_DEPLOY_HOOK
```

---

## Troubleshooting Deployment Issues

### Issue: Database connection refused
**Solution**: Check DATABASE_URL format and ensure database server is running
```
postgresql://user:password@host:5432/dbname
```

### Issue: Static files not found
**Solution**: Ensure FLASK_ENV=production and run:
```bash
python app.py init-db
```

### Issue: Module not found errors
**Solution**: Ensure all dependencies installed:
```bash
pip install -r requirements.txt
```

### Issue: Secret key not set
**Solution**: Generate and set strong SECRET_KEY:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## Cost Estimation

| Platform | Free Tier | Entry Prod | Recommended |
|----------|-----------|-----------|------------|
| Render | Yes* | $7/mo | $50/mo |
| Railway | Yes* | Usage-based | $50+/mo |
| AWS | 12 months | $10+/mo | $100+/mo |
| PythonAnywhere | Yes | $5/mo | $50/mo |

*Free tier limited to 750 hours/month

---

## Next Steps

1. Test application locally: `python app.py`
2. Push to GitHub
3. Follow platform-specific deployment steps
4. Monitor application logs
5. Setup automated backups
6. Configure domain name
7. Enable SSL/TLS certificate

For more help, refer to specific platform documentation or GitHub Issues.
