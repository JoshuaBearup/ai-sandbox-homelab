#!/bin/bash
#
# Deploy PostgreSQL 16 using Docker Compose
#
# This script deploys PostgreSQL 16 on VM 100 using Docker Compose.
# Run this script after Docker is installed.
#
# Usage:
#   1. Copy docker-compose.yml and this script to VM 100
#   2. Create .env file with credentials (see postgresql.env.example)
#   3. Run: bash deploy-postgresql.sh
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Deploying PostgreSQL 16${NC}"
echo -e "${GREEN}========================================${NC}"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}ERROR: Docker is not installed${NC}"
    echo -e "${YELLOW}Run the install-docker.sh script first${NC}"
    exit 1
fi

# Check if docker-compose.yml exists
if [ ! -f "$SCRIPT_DIR/postgresql-docker-compose.yml" ]; then
    echo -e "${RED}ERROR: postgresql-docker-compose.yml not found${NC}"
    echo -e "${YELLOW}Make sure you're in the correct directory${NC}"
    exit 1
fi

# Check if .env file exists
if [ ! -f "$SCRIPT_DIR/.env" ]; then
    echo -e "${YELLOW}WARNING: .env file not found${NC}"
    echo -e "${YELLOW}Creating .env from example...${NC}"

    if [ -f "$SCRIPT_DIR/postgresql.env.example" ]; then
        cp "$SCRIPT_DIR/postgresql.env.example" "$SCRIPT_DIR/.env"
        echo -e "${RED}IMPORTANT: Edit .env file and set secure passwords!${NC}"
        echo -e "${YELLOW}File location: $SCRIPT_DIR/.env${NC}"
        echo -e ""
        echo -e "${YELLOW}Press Enter after you've updated the passwords, or Ctrl+C to exit${NC}"
        read -r
    else
        echo -e "${RED}ERROR: postgresql.env.example not found${NC}"
        exit 1
    fi
fi

# Source the .env file to check for default passwords
source "$SCRIPT_DIR/.env"

# Check for default/weak passwords
if [ "$POSTGRES_PASSWORD" = "changeme" ] || [ "$POSTGRES_PASSWORD" = "your_secure_password_here" ]; then
    echo -e "${RED}ERROR: Default password detected!${NC}"
    echo -e "${YELLOW}Please update POSTGRES_PASSWORD in .env file${NC}"
    exit 1
fi

echo -e "${GREEN}Step 1: Pulling PostgreSQL 16 image...${NC}"
docker compose -f "$SCRIPT_DIR/postgresql-docker-compose.yml" pull

echo -e "${GREEN}Step 2: Creating and starting containers...${NC}"
docker compose -f "$SCRIPT_DIR/postgresql-docker-compose.yml" up -d

echo -e "${GREEN}Step 3: Waiting for PostgreSQL to be ready...${NC}"
sleep 5

# Check if container is running
if docker ps | grep -q postgresql; then
    echo -e "${GREEN}PostgreSQL container is running!${NC}"
else
    echo -e "${RED}ERROR: PostgreSQL container failed to start${NC}"
    echo -e "${YELLOW}Check logs with: docker logs postgresql${NC}"
    exit 1
fi

# Wait for health check
echo -e "${YELLOW}Waiting for health check to pass...${NC}"
for i in {1..30}; do
    if docker inspect --format='{{.State.Health.Status}}' postgresql 2>/dev/null | grep -q "healthy"; then
        echo -e "${GREEN}PostgreSQL is healthy!${NC}"
        break
    fi
    echo -n "."
    sleep 2
done
echo ""

echo -e "${GREEN}Step 4: Testing connection...${NC}"
docker exec postgresql pg_isready -U "$POSTGRES_USER"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}PostgreSQL deployment completed!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}Connection details:${NC}"
echo -e "  Host:     $(hostname -I | awk '{print $1}')"
echo -e "  Port:     5432"
echo -e "  Database: $POSTGRES_DB"
echo -e "  User:     $POSTGRES_USER"
echo -e "  Password: (from .env file)"
echo ""
echo -e "${YELLOW}pgAdmin (web interface):${NC}"
echo -e "  URL:      http://$(hostname -I | awk '{print $1}'):5050"
echo -e "  Email:    $PGADMIN_EMAIL"
echo -e "  Password: (from .env file)"
echo ""
echo -e "${YELLOW}Useful commands:${NC}"
echo -e "  View logs:      ${GREEN}docker logs postgresql${NC}"
echo -e "  View logs live: ${GREEN}docker logs -f postgresql${NC}"
echo -e "  Stop:           ${GREEN}docker compose -f $SCRIPT_DIR/postgresql-docker-compose.yml stop${NC}"
echo -e "  Start:          ${GREEN}docker compose -f $SCRIPT_DIR/postgresql-docker-compose.yml start${NC}"
echo -e "  Restart:        ${GREEN}docker compose -f $SCRIPT_DIR/postgresql-docker-compose.yml restart${NC}"
echo -e "  Shell access:   ${GREEN}docker exec -it postgresql psql -U $POSTGRES_USER -d $POSTGRES_DB${NC}"
echo ""
