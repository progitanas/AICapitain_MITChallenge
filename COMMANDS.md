# AICaptain Development & Operations Commands

## Docker Commands

### Build & Start

```bash
# Build all images
docker-compose build

# Start all services
docker-compose up -d

# Start with logs
docker-compose up

# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

### Logs & Monitoring

```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f nginx

# Filter logs by level
docker-compose logs backend | grep ERROR
docker-compose logs backend | grep WARNING

# Export logs
docker-compose logs > logs.txt
```

### Service Management

```bash
# Check service status
docker-compose ps

# Restart service
docker-compose restart backend
docker-compose restart frontend
docker-compose restart nginx

# Restart all
docker-compose restart

# Rebuild specific service
docker-compose up -d --build backend

# View service stats
docker stats
```

### Container Access

```bash
# Access backend shell
docker-compose exec backend bash

# Access frontend shell
docker-compose exec frontend sh

# Run command in container
docker-compose exec backend python -c "import sys; print(sys.version)"

# Execute tests
docker-compose exec backend pytest tests/ -v
```

## Backend Development

### Local Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (macOS/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install dev dependencies
pip install -r requirements-dev.txt
```

### Running Backend

```bash
# Development with auto-reload
python -m uvicorn api.main:app --port 8000 --reload

# Production with Gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 api.main:app

# With environment variables
export DEBUG=True && python -m uvicorn api.main:app --port 8000 --reload
```

### Testing

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_ai_captain.py -v

# Run with coverage
pytest --cov=backend tests/

# Run specific test class
pytest tests/test_ai_captain.py::TestOptimizer -v

# Run specific test method
pytest tests/test_ai_captain.py::TestOptimizer::test_a_star_algorithm -v
```

### Code Quality

```bash
# Format code
black . --line-length 100

# Lint code
pylint backend/

# Type checking
mypy backend/

# Combined
black . && pylint backend/ && mypy backend/
```

### Database (Future)

```bash
# Create migrations
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback migrations
alembic downgrade -1

# View migration history
alembic history
```

## Frontend Development

### Local Setup

```bash
cd frontend

# Install dependencies
npm install

# Install specific dependency
npm install lodash-es
npm install -D @types/lodash-es

# Update dependencies
npm update

# Audit vulnerabilities
npm audit
npm audit fix
```

### Running Frontend

```bash
# Development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Type checking
npm run type-check
```

### Code Quality

```bash
# Lint
npm run lint

# Fix linting issues
npm run lint:fix

# Format code
npm run format

# Type checking
npm run type-check

# All checks
npm run lint && npm run type-check && npm run format
```

### Testing

```bash
# Run tests
npm run test

# Run tests with coverage
npm run test:coverage

# Run specific test file
npm run test -- Dashboard.test.tsx

# Watch mode
npm run test -- --watch
```

### Building

```bash
# Build for development
npm run build

# Build with source maps
npm run build -- --sourcemap

# Build for specific environment
VITE_ENV=production npm run build

# Analyze bundle
npm run build && npm run analyze
```

## API Testing

### Health Checks

```bash
# Backend health
curl http://localhost:8000/health

# Frontend health
curl http://localhost:3000

# Nginx health
curl http://localhost
```

### API Endpoints

```bash
# Get API documentation
curl http://localhost:8000/api/v1/docs

# Get health status
curl http://localhost:8000/health

# List routes
curl http://localhost:8000/api/v1/routes

# Create optimization
curl -X POST http://localhost:8000/api/v1/routes/optimize \
  -H "Content-Type: application/json" \
  -d '{
    "vessel_id": "vessel1",
    "origin_port": "Singapore",
    "destination_port": "Rotterdam",
    "constraints": "balanced"
  }'

# Get vessel position
curl http://localhost:8000/api/v1/vessels/636016829/position

# Get forecasts
curl -X POST http://localhost:8000/api/v1/forecast/congestion \
  -H "Content-Type: application/json" \
  -d '{"ports": ["Singapore", "Rotterdam"], "hours_ahead": 24}'
```

## Deployment

### Docker Deployment

```bash
# Build images
docker-compose build

# Pull latest images
docker-compose pull

# Deploy
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

### Production Deployment

```bash
# Set production environment
export ENVIRONMENT=production

# Build with production settings
docker-compose -f docker-compose.yml -f docker-compose.prod.yml build

# Deploy
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Backup database before deploy
docker-compose exec database pg_dump -U admin aicaptain > backup-$(date +%Y%m%d).sql
```

### SSL/TLS Setup

```bash
# Generate Let's Encrypt certificate
docker-compose exec nginx certbot certonly --webroot -w /var/www/certbot -d yourdomain.com

# Renew certificate
docker-compose exec nginx certbot renew

# Check certificate status
docker-compose exec nginx certbot certificates
```

## Database Management

### Backup & Restore

```bash
# Backup database
docker-compose exec database pg_dump -U admin aicaptain > backup.sql

# Backup compressed
docker-compose exec database pg_dump -U admin aicaptain | gzip > backup-$(date +%Y%m%d).sql.gz

# Restore database
docker-compose exec -T database psql -U admin aicaptain < backup.sql

# Restore compressed
gunzip < backup.sql.gz | docker-compose exec -T database psql -U admin aicaptain
```

### Database Maintenance

```bash
# Cleanup old logs
docker-compose exec database psql -U admin aicaptain -c "DELETE FROM logs WHERE created_at < NOW() - INTERVAL '30 days';"

# Vacuum database
docker-compose exec database psql -U admin aicaptain -c "VACUUM ANALYZE;"

# Check database size
docker-compose exec database psql -U admin aicaptain -c "SELECT pg_size_pretty(pg_database_size('aicaptain'));"
```

## Troubleshooting

### Port Issues

```bash
# Find process on port
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill process
kill -9 <PID>  # macOS/Linux
taskkill /PID <PID> /F  # Windows
```

### Container Issues

```bash
# Remove stopped containers
docker-compose rm

# Prune unused resources
docker system prune

# Force rebuild
docker-compose build --no-cache

# Clean rebuild
docker-compose down -v && docker-compose up -d --build
```

### Log Issues

```bash
# Clear logs
truncate -s 0 /var/lib/docker/containers/*/*-json.log

# View daemon logs
docker logs <container-id>

# Follow container logs
docker logs -f <container-id>
```

## Performance Tuning

### Monitor Performance

```bash
# Docker stats
docker stats

# System resources
docker system df

# Top processes
docker top <container-name>

# Network stats
docker network inspect <network-name>
```

### Optimization

```bash
# Reduce image size
docker-compose build --compress

# Enable buildkit
DOCKER_BUILDKIT=1 docker-compose build

# Prune images
docker image prune -a
```

## Useful Aliases

```bash
# Add to ~/.bashrc or ~/.zshrc

alias dc='docker-compose'
alias dcup='docker-compose up -d'
alias dcdown='docker-compose down'
alias dclogs='docker-compose logs -f'
alias dcps='docker-compose ps'
alias dcexec='docker-compose exec'

# Backend
alias backend='docker-compose exec backend bash'
alias tests='docker-compose exec backend pytest tests/ -v'

# Frontend
alias frontend='docker-compose exec frontend sh'
alias npm-i='docker-compose exec frontend npm install'
alias npm-b='docker-compose exec frontend npm run build'

# Development
alias dev='docker-compose up -d && docker-compose logs -f'
alias prod='docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d'
```

## Resources

- Frontend Docs: http://localhost:3000
- Backend Docs: http://localhost:8000/api/v1/docs
- Docker Docs: https://docs.docker.com
- FastAPI Docs: https://fastapi.tiangolo.com
- React Docs: https://react.dev
- Tailwind Docs: https://tailwindcss.com

---

Last Updated: November 9, 2025
