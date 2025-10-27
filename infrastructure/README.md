# Infrastructure

This directory contains all infrastructure-related scripts, configurations, and deployment files for the AI sandbox home lab.

## Directory Structure

```
infrastructure/
├── proxmox/          # Proxmox VM creation scripts
├── scripts/          # Installation and utility scripts
├── docker/           # Docker Compose files and configs
└── README.md         # This file
```

---

## Proxmox VM Scripts

Location: `proxmox/`

These scripts automate the creation of VMs on Proxmox with predefined resource allocations.

### Available Scripts

| Script | VM ID | Purpose | Resources |
|--------|-------|---------|-----------|
| `create-vm-100-postgresql.sh` | 100 | PostgreSQL Server | 4 cores, 8GB RAM, 100GB disk |
| `create-vm-101-ollama.sh` | 101 | Ollama AI Server | 32 cores, 64GB RAM, 200GB disk |
| `create-vm-102-dev.sh` | 102 | DEV Apps Server | 16 cores, 32GB RAM, 100GB disk |

### Usage

1. **Upload Debian 12 ISO to Proxmox**
   ```bash
   cd /var/lib/vz/template/iso
   wget https://cdimage.debian.org/debian-cd/current/amd64/iso-cd/debian-12.4.0-amd64-netinst.iso
   ```

2. **Run the script on Proxmox host**
   ```bash
   ssh root@proxmox-host
   chmod +x create-vm-100-postgresql.sh
   bash create-vm-100-postgresql.sh
   ```

3. **Follow the on-screen instructions** to complete OS installation

### Features

- Automated VM creation with correct resource allocation
- Configured for HDDStorage
- QEMU guest agent enabled
- Network bridge configured (vmbr0)
- Color-coded output with next-step instructions
- Error checking (prevents duplicate VMs)

---

## Installation Scripts

Location: `scripts/`

These scripts are run on the VMs after OS installation to set up required services.

### Available Scripts

| Script | Purpose | Run On |
|--------|---------|--------|
| `install-docker.sh` | Install Docker Engine on Debian 12 | VM 100, VM 102 |
| `install-ollama.sh` | Install Ollama + Llama 3.1 8B | VM 101 |

### Usage

**Install Docker:**
```bash
# Copy script to target VM
scp install-docker.sh debian@192.168.1.100:~

# SSH to VM and run
ssh debian@192.168.1.100
sudo bash install-docker.sh

# Log out and back in for group changes
exit
ssh debian@192.168.1.100
```

**Install Ollama:**
```bash
# Copy script to VM 101
scp install-ollama.sh debian@192.168.1.101:~

# SSH to VM and run
ssh debian@192.168.1.101
sudo bash install-ollama.sh
```

### Features

- Comprehensive error checking
- Color-coded output
- Automatic service configuration
- Verification steps included
- User group management (Docker)
- Performance benchmarking (Ollama)

---

## Docker Configurations

Location: `docker/`

Docker Compose files and deployment scripts for containerized services.

### PostgreSQL Deployment

**Files:**
- `postgresql-docker-compose.yml` - Docker Compose configuration
- `postgresql.env.example` - Environment variables template
- `deploy-postgresql.sh` - Automated deployment script

**Features:**
- PostgreSQL 16 official image
- Persistent data volumes
- Health checks
- Resource limits (4 cores, 6GB RAM max)
- Optional pgAdmin web interface
- Network isolation

**Usage:**
```bash
# On VM 100
mkdir -p ~/postgresql
cd ~/postgresql

# Copy files
scp postgresql-docker-compose.yml debian@192.168.1.100:~/postgresql/
scp postgresql.env.example debian@192.168.1.100:~/postgresql/
scp deploy-postgresql.sh debian@192.168.1.100:~/postgresql/

# SSH to VM
ssh debian@192.168.1.100
cd ~/postgresql

# Configure
cp postgresql.env.example .env
nano .env  # Set secure passwords

# Deploy
bash deploy-postgresql.sh
```

**Access:**
- PostgreSQL: `192.168.1.100:5432`
- pgAdmin: `http://192.168.1.100:5050`

---

## Quick Start Guide

### Phase 1: Create VMs

```bash
# On Proxmox host
cd /tmp
# Copy VM creation scripts
bash create-vm-100-postgresql.sh
bash create-vm-101-ollama.sh
bash create-vm-102-dev.sh
```

### Phase 2: Install OS

For each VM:
1. Start VM and open console in Proxmox UI
2. Install Debian 12 (minimal install + SSH)
3. Configure static IP
4. Install qemu-guest-agent

### Phase 3: Install Services

**VM 100 (PostgreSQL):**
```bash
scp scripts/install-docker.sh debian@192.168.1.100:~
ssh debian@192.168.1.100 'sudo bash install-docker.sh'

# Deploy PostgreSQL
# (copy docker files and run deploy-postgresql.sh)
```

**VM 101 (Ollama):**
```bash
scp scripts/install-ollama.sh debian@192.168.1.101:~
ssh debian@192.168.1.101 'sudo bash install-ollama.sh'
```

**VM 102 (DEV):**
```bash
scp scripts/install-docker.sh debian@192.168.1.102:~
ssh debian@192.168.1.102 'sudo bash install-docker.sh'
```

---

## Script Conventions

All scripts follow these conventions:

### Error Handling
- Set `-e` flag (exit on error)
- Set `-u` flag (exit on undefined variable)
- Comprehensive error checking
- Informative error messages

### Output
- Color-coded messages (green=success, yellow=warning, red=error)
- Clear section headers
- Progress indicators
- Next-step instructions

### Security
- Check for default passwords
- Verify prerequisites
- Prompt for confirmation on destructive operations
- Never hardcode credentials

### Documentation
- Header comment with description
- Usage instructions
- Required parameters documented
- Examples provided

---

## Customization

### Modifying VM Resources

Edit the scripts before running:

```bash
# In create-vm-100-postgresql.sh
CORES=4        # Change to desired core count
MEMORY=8192    # Change to desired RAM (in MB)
DISK_SIZE=100G # Change to desired disk size
```

### Changing IP Addresses

Update static IP configuration on each VM:

```bash
# /etc/network/interfaces
auto ens18
iface ens18 inet static
    address 192.168.1.100/24  # Change to your network
    gateway 192.168.1.1       # Change to your gateway
```

### Using Different Storage

```bash
# In VM creation scripts
STORAGE="HDDStorage"  # Change to your Proxmox storage name
```

---

## Troubleshooting

### VM Creation Fails

**Issue:** ISO not found
```bash
# Check available ISOs
pvesm list local --content iso

# Update ISO_FILE variable in script to match
ISO_FILE="your-actual-iso-name.iso"
```

**Issue:** VM ID already exists
```bash
# Remove existing VM
qm stop 100
qm destroy 100
```

### Docker Installation Fails

**Issue:** Old Docker installation conflicts
```bash
# Remove old Docker
sudo apt-get remove docker docker-engine docker.io containerd runc
sudo apt-get autoremove

# Re-run install script
```

### Ollama Won't Start

**Issue:** Service fails to start
```bash
# Check logs
journalctl -u ollama -n 50

# Common fix: restart service
sudo systemctl restart ollama
```

---

## Best Practices

1. **Version Control**
   - Keep scripts in git
   - Document any customizations
   - Track changes in DECISIONS.md

2. **Testing**
   - Test scripts on a single VM first
   - Verify each step before proceeding
   - Keep backups before making changes

3. **Security**
   - Always use strong passwords
   - Never commit .env files
   - Keep systems updated
   - Configure firewalls

4. **Documentation**
   - Update CURRENT_STATUS.md after changes
   - Log issues in LESSONS.md
   - Create session notes for major work

---

## Related Documentation

- [SETUP.md](../SETUP.md) - Complete setup guide
- [CURRENT_STATUS.md](../CURRENT_STATUS.md) - Current project status
- [AGENTS.md](../AGENTS.md) - AI assistant instructions
- [DECISIONS.md](../DECISIONS.md) - Decision log

---

## File Permissions

Make scripts executable before running:

```bash
chmod +x infrastructure/proxmox/*.sh
chmod +x infrastructure/scripts/*.sh
chmod +x infrastructure/docker/*.sh
```

---

## Support

For issues or questions:
1. Check [SETUP.md](../SETUP.md) troubleshooting section
2. Review [LESSONS.md](../LESSONS.md) for known issues
3. Create a session note in `logs/session_notes/`
