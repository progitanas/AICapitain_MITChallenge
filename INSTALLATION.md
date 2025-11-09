# Installation & Setup Guide

## System Requirements

### Minimum

- CPU: 2 cores
- RAM: 4GB
- Disk: 10GB
- OS: Linux, macOS, or Windows 10+

### Recommended (Production)

- CPU: 8+ cores
- RAM: 16GB
- Disk: 50GB SSD
- OS: Ubuntu 22.04 LTS or similar

## Installation Steps

### 1. Install Dependencies

#### Windows

```powershell
# Install Docker Desktop
# Download from: https://www.docker.com/products/docker-desktop
# Follow installation wizard

# Verify installation
docker --version
docker-compose --version
```

#### macOS

```bash
# Using Homebrew
brew install docker docker-compose

# Or download Docker Desktop from:
# https://www.docker.com/products/docker-desktop
```

#### Linux (Ubuntu/Debian)

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify
docker --version
docker-compose --version
```

### 2. Clone Repository

```bash
git clone https://github.com/AICapitain/mitchallenge.git
cd AICapitain_MITChallenge
```

### 3. Configure Environment

```bash
# Backend configuration
cp backend/.env.example backend/.env
# Edit backend/.env as needed

# Frontend configuration
cp frontend/.env.example frontend/.env
# Edit frontend/.env as needed
```

### 4. Deploy Application

#### Using Docker Compose (Recommended)

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Access applications
# Frontend:  http://localhost:3000
# Backend:   http://localhost:8000
# API Docs:  http://localhost:8000/api/v1/docs
```

#### Local Development (Backend)

```bash
cd backend

# Create Python virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run migrations (if applicable)
alembic upgrade head

# Start development server
python -m uvicorn api.main:app --port 8000 --reload

# Run tests
pytest tests/ -v
```

#### Local Development (Frontend)

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Post-Installation

### Verify Installation

```bash
# Check backend health
curl http://localhost:8000/health

# Check frontend
curl http://localhost:3000

# Check API documentation
curl http://localhost:8000/api/v1/docs
```

### Load Sample Data

```bash
# Backend automatically loads AIS data on startup
# Check logs: docker-compose logs backend | grep -i "ais"
```

### Create Admin User (Optional)

```bash
# Connect to backend container
docker-compose exec backend bash

# Create admin user
python -c "from api.auth import create_admin; create_admin()"
```

## Troubleshooting

### Port Already in Use

```bash
# Find process using port 8000
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill process
kill -9 <PID>
# Or use docker-compose to change ports
```

### Docker Build Failures

```bash
# Clear Docker cache
docker system prune -a

# Rebuild from scratch
docker-compose build --no-cache
docker-compose up -d
```

### Database Connection Issues

```bash
# Verify database is running
docker-compose ps

# Check database logs
docker-compose logs database

# Restart database
docker-compose restart database
```

### Frontend Build Issues

```bash
# Clear node_modules and reinstall
rm -rf frontend/node_modules
rm frontend/package-lock.json
npm install

# Rebuild
npm run build
```

## Upgrading

### Backup Data

```bash
# Backup database
docker-compose exec database pg_dump -U admin aicaptain > backup.sql
```

### Update Code

```bash
git pull origin main
docker-compose build --no-cache
docker-compose up -d
```

### Apply Migrations

```bash
# Connect to backend
docker-compose exec backend bash

# Run migrations
alembic upgrade head
```

## Production Deployment

### Using Docker Compose

```bash
# Set environment to production
export ENVIRONMENT=production

# Build with production settings
docker-compose -f docker-compose.yml -f docker-compose.prod.yml build

# Start services
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### SSL/TLS Setup

```bash
# Using Certbot for Let's Encrypt
docker-compose exec nginx certbot certonly --webroot -w /var/www/certbot -d yourdomain.com

# Update nginx configuration
# Point to /etc/letsencrypt/live/yourdomain.com
```

### Monitoring & Logging

```bash
# View real-time logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Export logs
docker-compose logs > logs.txt
```

## Performance Tuning

### Backend

```bash
# Increase workers in production
# In docker-compose.yml:
# command: gunicorn -w 4 -b 0.0.0.0:8000 api.main:app

# Enable caching
# Configure Redis for session storage
```

### Frontend

```bash
# Enable gzip compression in nginx
# Add to nginx.conf:
# gzip on;
# gzip_types text/plain text/css application/json;

# Enable browser caching
# Add cache headers to nginx config
```

## Maintenance

### Regular Tasks

- **Daily**: Monitor logs and health checks
- **Weekly**: Backup database
- **Monthly**: Update dependencies (security patches)
- **Quarterly**: Full system backup and disaster recovery test

### Database Maintenance

```bash
# Backup
docker-compose exec database pg_dump -U admin aicaptain | gzip > backup-$(date +%Y%m%d).sql.gz

# Restore
docker-compose exec -T database psql -U admin aicaptain < backup.sql

# Cleanup old logs
docker-compose exec database psql -U admin aicaptain -c "DELETE FROM logs WHERE created_at < NOW() - INTERVAL '30 days';"
```

## Support

For issues or questions:

1. Check troubleshooting section above
2. Review logs: `docker-compose logs`
3. Visit documentation: https://docs.aicaptain.com
4. Contact support: support@aicaptain.com

---

**Last Updated**: November 9, 2025
