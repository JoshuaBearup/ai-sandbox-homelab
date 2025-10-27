#!/bin/bash
#
# Install Docker on Debian 12
#
# This script installs Docker Engine on a fresh Debian 12 installation.
# Run this script on the VM after OS installation is complete.
#
# Usage:
#   1. Copy this script to the target VM
#   2. Run with sudo: sudo bash install-docker.sh
#   3. Log out and log back in for group changes to take effect
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Installing Docker on Debian 12${NC}"
echo -e "${GREEN}========================================${NC}"

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}ERROR: Please run as root (use sudo)${NC}"
    exit 1
fi

# Check if Docker is already installed
if command -v docker &> /dev/null; then
    echo -e "${YELLOW}Docker is already installed${NC}"
    docker --version
    echo -e "${YELLOW}To reinstall, first remove Docker:${NC}"
    echo -e "  apt-get remove docker docker-engine docker.io containerd runc"
    exit 0
fi

echo -e "${GREEN}Step 1: Updating system packages...${NC}"
apt-get update
apt-get upgrade -y

echo -e "${GREEN}Step 2: Installing prerequisites...${NC}"
apt-get install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

echo -e "${GREEN}Step 3: Adding Docker's official GPG key...${NC}"
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
chmod a+r /etc/apt/keyrings/docker.gpg

echo -e "${GREEN}Step 4: Setting up Docker repository...${NC}"
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian \
  $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

echo -e "${GREEN}Step 5: Installing Docker Engine...${NC}"
apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

echo -e "${GREEN}Step 6: Starting and enabling Docker service...${NC}"
systemctl start docker
systemctl enable docker

echo -e "${GREEN}Step 7: Adding current user to docker group...${NC}"
# Get the actual user (not root) who invoked sudo
ACTUAL_USER="${SUDO_USER:-$USER}"
if [ "$ACTUAL_USER" != "root" ]; then
    usermod -aG docker "$ACTUAL_USER"
    echo -e "${YELLOW}User '$ACTUAL_USER' added to docker group${NC}"
    echo -e "${YELLOW}Log out and log back in for group changes to take effect${NC}"
else
    echo -e "${YELLOW}Running as root. Add users to docker group manually:${NC}"
    echo -e "  usermod -aG docker <username>"
fi

echo -e "${GREEN}Step 8: Verifying Docker installation...${NC}"
docker --version
docker compose version

echo -e "${GREEN}Step 9: Running test container...${NC}"
docker run --rm hello-world

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Docker installation completed!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo -e "  1. Log out and log back in (to apply docker group membership)"
echo -e "  2. Verify: ${GREEN}docker ps${NC}"
echo -e "  3. Test: ${GREEN}docker run --rm hello-world${NC}"
echo ""
echo -e "${YELLOW}Installed versions:${NC}"
docker --version
docker compose version
echo ""
