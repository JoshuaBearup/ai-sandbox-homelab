# Setup Guide

This guide provides step-by-step instructions for setting up the AI sandbox home lab from scratch.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Phase 1: VM Creation](#phase-1-vm-creation)
3. [Phase 2: PostgreSQL Setup](#phase-2-postgresql-setup)
4. [Phase 3: Ollama AI Setup](#phase-3-ollama-ai-setup)
5. [Phase 4: Development Environment](#phase-4-development-environment)
6. [Verification](#verification)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Hardware Requirements
- Proxmox VE installed and configured
- Minimum 50GB available cores, 100GB RAM, 500GB storage
- Network access to Proxmox host

### Software Requirements
- Debian 12 ISO uploaded to Proxmox
  - Download: https://www.debian.org/distrib/netinst
  - Upload to Proxmox: Datacenter > Storage > local > ISO Images > Upload
- SSH access to Proxmox host
- Git installed on your local machine

### Knowledge Requirements
- Basic Linux command line
- SSH and networking basics
- Docker fundamentals (helpful but not required)

---

## Phase 1: VM Creation

### Overview
Create three VMs with specific resource allocations:
- VM 100: PostgreSQL Server (4 cores, 8GB RAM, 100GB disk)
- VM 101: Ollama AI Server (32 cores, 64GB RAM, 200GB disk)
- VM 102: DEV Apps Server (16 cores, 32GB RAM, 100GB disk)

### Step 1.1: Download Debian 12 ISO

```bash
# On Proxmox host, download Debian 12
cd /var/lib/vz/template/iso
wget https://cdimage.debian.org/debian-cd/current/amd64/iso-cd/debian-12.4.0-amd64-netinst.iso
```

Or upload via Proxmox web UI: Datacenter > local > ISO Images > Upload

### Step 1.2: Create VM 100 (PostgreSQL)

```bash
# SSH to Proxmox host
ssh root@your-proxmox-host

# Clone the repository or copy the script
cd /tmp
# Copy infrastructure/proxmox/create-vm-100-postgresql.sh to Proxmox host

# Make executable and run
chmod +x create-vm-100-postgresql.sh
bash create-vm-100-postgresql.sh
```

**Alternative: Manual creation via Proxmox UI**
1. Click "Create VM" in Proxmox UI
2. General: VM ID = 100, Name = postgresql-server
3. OS: Select Debian 12 ISO
4. System: Default (QEMU agent enabled)
5. Disks: 100GB on HDDStorage
6. CPU: 4 cores
7. Memory: 8192 MB
8. Network: Default (vmbr0)
9. Confirm and create

### Step 1.3: Install Debian on VM 100

1. Start VM 100 and open console
2. Select "Install" (not graphical install)
3. Follow installer:
   - Language: English
   - Location: Your location
   - Keyboard: Your keyboard layout
   - Hostname: `postgresql-server`
   - Domain: (leave blank)
   - Root password: Set a strong password
   - User: `debian` (or your preferred username)
   - Partitioning: Guided - use entire disk
   - Write changes: Yes
   - Package manager: Default mirror
   - Software selection: **SSH server** and **standard system utilities** ONLY
4. Install GRUB: Yes, to /dev/sda
5. Finish installation and reboot

### Step 1.4: Configure Static IP on VM 100

```bash
# SSH to VM 100 as root
ssh debian@vm-100-ip
sudo -i

# Edit network configuration
nano /etc/network/interfaces

# Change from DHCP to static:
# The primary network interface
auto ens18
iface ens18 inet static
    address 192.168.1.100/24
    gateway 192.168.1.1
    dns-nameservers 8.8.8.8 8.8.4.4

# Save and restart networking
systemctl restart networking

# Install QEMU guest agent
apt-get update
apt-get install -y qemu-guest-agent
systemctl start qemu-guest-agent
systemctl enable qemu-guest-agent
```

### Step 1.5: Create VM 101 (Ollama) and VM 102 (DEV)

Repeat steps 1.2-1.4 for VM 101 and VM 102:
- Use `create-vm-101-ollama.sh` and `create-vm-102-dev.sh`
- Hostnames: `ollama-ai-server`, `dev-apps-server`
- Static IPs: `192.168.1.101`, `192.168.1.102` (adjust to your network)

---

## Phase 2: PostgreSQL Setup

### Step 2.1: Install Docker on VM 100

```bash
# SSH to VM 100
ssh debian@192.168.1.100

# Copy install-docker.sh to VM 100 (or curl it from GitHub)
# Then run:
sudo bash install-docker.sh

# Log out and log back in for group changes
exit
ssh debian@192.168.1.100

# Verify Docker
docker ps
```

### Step 2.2: Deploy PostgreSQL Container

```bash
# Create directory for PostgreSQL
mkdir -p ~/postgresql
cd ~/postgresql

# Copy files to VM:
# - postgresql-docker-compose.yml
# - postgresql.env.example
# - deploy-postgresql.sh

# Create .env file from example
cp postgresql.env.example .env

# IMPORTANT: Edit .env and set secure passwords
nano .env

# Deploy PostgreSQL
bash deploy-postgresql.sh
```

### Step 2.3: Verify PostgreSQL

```bash
# Check container status
docker ps

# Test connection
docker exec postgresql pg_isready -U postgres

# Connect to database
docker exec -it postgresql psql -U postgres

# In psql:
\l              # List databases
\q              # Quit
```

### Step 2.4: Access pgAdmin (Optional)

Open browser: `http://192.168.1.100:5050`
- Email: From .env file
- Password: From .env file

Add server in pgAdmin:
- Host: postgresql (container name)
- Port: 5432
- Username: From .env file
- Password: From .env file

---

## Phase 3: Ollama AI Setup

### Step 3.1: Install Ollama on VM 101

```bash
# SSH to VM 101
ssh debian@192.168.1.101

# Copy install-ollama.sh or run directly
sudo bash install-ollama.sh

# This will:
# - Install Ollama
# - Download Llama 3.1 8B model (~4.7GB)
# - Test the model
```

### Step 3.2: Verify Ollama

```bash
# Check service status
systemctl status ollama

# List installed models
ollama list

# Test the model
ollama run llama3.1:8b "Hello! Respond in one sentence."

# Test API endpoint
curl http://localhost:11434/api/generate -d '{
  "model": "llama3.1:8b",
  "prompt": "Say hello in one sentence",
  "stream": false
}'
```

### Step 3.3: Performance Benchmarking

```bash
# Test response time
time ollama run llama3.1:8b "Write a 100-word paragraph about AI."

# Monitor resource usage
htop

# Check logs
journalctl -u ollama -f
```

**Expected Performance:**
- Tokens/sec: 15-25 tokens/sec
- Response time: 2-4 seconds for typical queries
- Memory usage: ~8GB for model + overhead

---

## Phase 4: Development Environment

### Step 4.1: Install Docker on VM 102

```bash
# SSH to VM 102
ssh debian@192.168.1.102

# Copy and run install-docker.sh
sudo bash install-docker.sh

# Log out and back in
exit
ssh debian@192.168.1.102

# Verify
docker ps
```

### Step 4.2: Clone Repository on VM 102

```bash
# Install git
sudo apt-get update
sudo apt-get install -y git

# Clone repository (adjust URL for your repo)
git clone https://github.com/yourusername/ai-sandbox-homelab.git
cd ai-sandbox-homelab
```

### Step 4.3: Future: Deploy Streamlit Apps

This will be covered in future sessions. Directory structure:
```
streamlit_apps/
├── shared/
│   ├── db.py          # Database utilities
│   ├── ai.py          # Ollama client
│   └── config.py      # Configuration
└── app1/
    ├── streamlit_main.py
    ├── environment.yml
    └── config.json
```

---

## Verification

### System Health Checklist

**VM 100 (PostgreSQL):**
```bash
ssh debian@192.168.1.100
docker ps | grep postgresql
docker exec postgresql pg_isready
```

**VM 101 (Ollama):**
```bash
ssh debian@192.168.1.101
systemctl status ollama
ollama list
curl http://localhost:11434/api/tags
```

**VM 102 (DEV Apps):**
```bash
ssh debian@192.168.1.102
docker ps
git status
```

### Network Connectivity

**From VM 102, test connectivity to other services:**
```bash
# Test PostgreSQL
nc -zv 192.168.1.100 5432

# Test Ollama
curl http://192.168.1.101:11434/api/tags
```

### Resource Usage

**On Proxmox host:**
```bash
qm status 100
qm status 101
qm status 102

# Detailed resource usage
pvesh get /nodes/localhost/qemu/100/status/current
```

---

## Troubleshooting

### VM Won't Start
```bash
# Check VM configuration
qm config <vmid>

# Check Proxmox logs
tail -f /var/log/pve/tasks/active

# Try to start with errors shown
qm start <vmid>
```

### Docker Installation Failed
```bash
# Remove old Docker installation
sudo apt-get remove docker docker-engine docker.io containerd runc

# Clean up
sudo apt-get autoremove
sudo apt-get autoclean

# Re-run install-docker.sh
```

### PostgreSQL Container Won't Start
```bash
# Check logs
docker logs postgresql

# Common issues:
# 1. Password not set in .env
# 2. Port 5432 already in use: netstat -tulpn | grep 5432
# 3. Permissions: ls -la ~/postgresql

# Remove and recreate
docker compose down -v
docker compose up -d
```

### Ollama Service Not Running
```bash
# Check status
systemctl status ollama

# View logs
journalctl -u ollama -n 50

# Restart service
sudo systemctl restart ollama

# Check if port is available
netstat -tulpn | grep 11434
```

### Network Connectivity Issues
```bash
# Check IP configuration
ip addr show

# Test connectivity
ping 192.168.1.1  # Gateway
ping 8.8.8.8      # Internet

# Check firewall
sudo iptables -L

# Check if services are listening
netstat -tulpn
```

### Out of Disk Space
```bash
# Check disk usage
df -h

# Docker cleanup
docker system prune -a

# Remove old kernels (Debian)
sudo apt-get autoremove
```

---

## Next Steps

After completing this setup:

1. **Document your configuration**
   - Update CURRENT_STATUS.md with actual IP addresses
   - Add any customizations to LESSONS.md

2. **Security hardening** (recommended)
   - Configure firewall (ufw)
   - Set up SSH key authentication
   - Disable root SSH login
   - Regular updates: `apt-get update && apt-get upgrade`

3. **Backup strategy**
   - Proxmox VM backups
   - Database dumps
   - Git for code

4. **Start building applications**
   - See [Architecture Documentation](docs/00_architecture.md)
   - See [Development Guide](docs/02_development.md)
   - Begin with a simple test app in `streamlit_apps/app1/`

---

## Quick Reference

### VM Details
| VM ID | Hostname | IP | Purpose | Resources |
|-------|----------|----|---------|-----------|
| 100 | postgresql-server | 192.168.1.100 | PostgreSQL 16 | 4 cores, 8GB RAM |
| 101 | ollama-ai-server | 192.168.1.101 | Ollama + Llama 3.1 8B | 32 cores, 64GB RAM |
| 102 | dev-apps-server | 192.168.1.102 | Streamlit apps | 16 cores, 32GB RAM |

### Key Services
- PostgreSQL: `192.168.1.100:5432`
- pgAdmin: `http://192.168.1.100:5050`
- Ollama API: `http://192.168.1.101:11434`

### Important Files
- VM creation scripts: `infrastructure/proxmox/`
- Installation scripts: `infrastructure/scripts/`
- Docker configs: `infrastructure/docker/`
- Application code: `streamlit_apps/`

---

**Questions or issues?** Check LESSONS.md or create a new session note in `logs/session_notes/`
