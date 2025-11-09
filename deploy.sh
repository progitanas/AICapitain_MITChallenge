#!/usr/bin/env bash

# AICaptain Full Stack Deployment Script
# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}═══════════════════════════════════════${NC}"
echo -e "${YELLOW}   AICaptain Full Stack Deployment${NC}"
echo -e "${YELLOW}═══════════════════════════════════════${NC}"

# Check Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}✗ Docker not installed${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Docker installed${NC}"

# Check Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}✗ Docker Compose not installed${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Docker Compose installed${NC}"

# Build images
echo -e "\n${YELLOW}Building Docker images...${NC}"
docker-compose build

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Images built successfully${NC}"
else
    echo -e "${RED}✗ Failed to build images${NC}"
    exit 1
fi

# Start services
echo -e "\n${YELLOW}Starting services...${NC}"
docker-compose up -d

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Services started successfully${NC}"
else
    echo -e "${RED}✗ Failed to start services${NC}"
    exit 1
fi

# Wait for services to be ready
echo -e "\n${YELLOW}Waiting for services to be ready...${NC}"
sleep 5

# Check health
echo -e "\n${YELLOW}Checking service health...${NC}"

# Backend health
BACKEND_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health)
if [ "$BACKEND_HEALTH" == "200" ]; then
    echo -e "${GREEN}✓ Backend API healthy${NC}"
else
    echo -e "${RED}✗ Backend API unhealthy (HTTP $BACKEND_HEALTH)${NC}"
fi

# Frontend health
FRONTEND_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000)
if [ "$FRONTEND_HEALTH" == "200" ] || [ "$FRONTEND_HEALTH" == "301" ]; then
    echo -e "${GREEN}✓ Frontend app healthy${NC}"
else
    echo -e "${RED}✗ Frontend app unhealthy (HTTP $FRONTEND_HEALTH)${NC}"
fi

echo -e "\n${YELLOW}═══════════════════════════════════════${NC}"
echo -e "${GREEN}Deployment Complete!${NC}"
echo -e "${YELLOW}═══════════════════════════════════════${NC}"
echo -e ""
echo -e "Access your application:"
echo -e "  Frontend:  ${GREEN}http://localhost:3000${NC}"
echo -e "  Backend:   ${GREEN}http://localhost:8000${NC}"
echo -e "  API Docs:  ${GREEN}http://localhost:8000/api/v1/docs${NC}"
echo -e ""
echo -e "Useful commands:"
echo -e "  Logs:      ${YELLOW}docker-compose logs -f${NC}"
echo -e "  Stop:      ${YELLOW}docker-compose down${NC}"
echo -e "  Status:    ${YELLOW}docker-compose ps${NC}"
