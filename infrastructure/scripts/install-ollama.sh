#!/bin/bash
#
# Install Ollama on Debian 12
#
# This script installs Ollama and downloads the Llama 3.1 8B model.
# Run this script on VM 101 after OS installation is complete.
#
# Usage:
#   Run with: curl -fsSL https://ollama.com/install.sh | sh
#   Or use this script: sudo bash install-ollama.sh
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Installing Ollama AI Server${NC}"
echo -e "${GREEN}========================================${NC}"

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}ERROR: Please run as root (use sudo)${NC}"
    exit 1
fi

# Check if Ollama is already installed
if command -v ollama &> /dev/null; then
    echo -e "${YELLOW}Ollama is already installed${NC}"
    ollama --version
    echo -e "${YELLOW}Continuing to model download...${NC}"
else
    echo -e "${GREEN}Step 1: Installing Ollama...${NC}"
    curl -fsSL https://ollama.com/install.sh | sh

    echo -e "${GREEN}Step 2: Starting Ollama service...${NC}"
    systemctl start ollama
    systemctl enable ollama

    # Wait for service to be ready
    echo -e "${YELLOW}Waiting for Ollama service to start...${NC}"
    sleep 5

    # Verify installation
    echo -e "${GREEN}Step 3: Verifying installation...${NC}"
    ollama --version
fi

# Check if Ollama service is running
if ! systemctl is-active --quiet ollama; then
    echo -e "${RED}ERROR: Ollama service is not running${NC}"
    echo -e "${YELLOW}Check status with: systemctl status ollama${NC}"
    exit 1
fi

echo -e "${GREEN}Step 4: Downloading Llama 3.1 8B model...${NC}"
echo -e "${YELLOW}This may take several minutes (model is ~4.7GB)${NC}"

# Pull the model
ollama pull llama3.1:8b

echo -e "${GREEN}Step 5: Testing model...${NC}"
echo -e "${YELLOW}Running a test query...${NC}"

# Test the model
ollama run llama3.1:8b "Hello! Please respond with a single sentence confirming you are working." --verbose

echo -e "${GREEN}Step 6: Checking system information...${NC}"
ollama list

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Ollama installation completed!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}Service status:${NC}"
systemctl status ollama --no-pager | head -n 10
echo ""
echo -e "${YELLOW}API endpoint:${NC}"
echo -e "  Local:  http://localhost:11434"
echo -e "  Remote: http://$(hostname -I | awk '{print $1}'):11434"
echo ""
echo -e "${YELLOW}Installed models:${NC}"
ollama list
echo ""
echo -e "${YELLOW}Useful commands:${NC}"
echo -e "  List models:        ${GREEN}ollama list${NC}"
echo -e "  Run model:          ${GREEN}ollama run llama3.1:8b${NC}"
echo -e "  Pull new model:     ${GREEN}ollama pull <model_name>${NC}"
echo -e "  Remove model:       ${GREEN}ollama rm <model_name>${NC}"
echo -e "  Service status:     ${GREEN}systemctl status ollama${NC}"
echo -e "  Service logs:       ${GREEN}journalctl -u ollama -f${NC}"
echo ""
echo -e "${YELLOW}Test the API:${NC}"
echo -e "  ${GREEN}curl http://localhost:11434/api/generate -d '{\"model\": \"llama3.1:8b\", \"prompt\": \"Hello!\"}'${NC}"
echo ""
echo -e "${YELLOW}Performance expectations:${NC}"
echo -e "  - Llama 3.1 8B: 15-25 tokens/sec on this hardware"
echo -e "  - Response time: 2-4 seconds for typical queries"
echo -e "  - Memory usage: ~8GB for model + overhead"
echo ""
echo -e "${YELLOW}Additional models (optional):${NC}"
echo -e "  - Llama 3.1 13B:   ${GREEN}ollama pull llama3.1:13b${NC} (~7.4GB)"
echo -e "  - Llama 3.1 70B:   ${GREEN}ollama pull llama3.1:70b${NC} (~39GB)"
echo -e "  - Mistral 7B:      ${GREEN}ollama pull mistral${NC} (~4.1GB)"
echo -e "  - Code Llama:      ${GREEN}ollama pull codellama${NC} (~3.8GB)"
echo ""
