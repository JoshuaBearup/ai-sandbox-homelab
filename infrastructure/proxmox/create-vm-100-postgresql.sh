#!/bin/bash
#
# Create VM 100: PostgreSQL Server
#
# This script creates a Proxmox VM for PostgreSQL with the following specs:
# - VM ID: 100
# - CPU: 4 cores
# - RAM: 8GB
# - Disk: 100GB on HDDStorage
# - OS: Debian 12
#
# Usage:
#   1. Upload Debian 12 ISO to Proxmox
#   2. Run this script on the Proxmox host
#   3. Start the VM and complete OS installation
#

set -e  # Exit on error
set -u  # Exit on undefined variable

# Configuration
VM_ID=100
VM_NAME="postgresql-server"
CORES=4
MEMORY=8192  # 8GB in MB
DISK_SIZE=100G
STORAGE="HDDStorage"
ISO_STORAGE="local"
ISO_FILE="debian-12.4.0-amd64-netinst.iso"  # Update this to match your ISO filename

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Creating VM $VM_ID: $VM_NAME${NC}"
echo -e "${GREEN}========================================${NC}"

# Check if VM already exists
if qm status $VM_ID &> /dev/null; then
    echo -e "${RED}ERROR: VM $VM_ID already exists!${NC}"
    echo -e "${YELLOW}To destroy and recreate, run:${NC}"
    echo -e "  qm stop $VM_ID"
    echo -e "  qm destroy $VM_ID"
    exit 1
fi

# Check if ISO exists
if ! pvesm list $ISO_STORAGE | grep -q "$ISO_FILE"; then
    echo -e "${YELLOW}WARNING: ISO file '$ISO_FILE' not found in storage '$ISO_STORAGE'${NC}"
    echo -e "${YELLOW}Available ISOs:${NC}"
    pvesm list $ISO_STORAGE --content iso
    echo -e "${YELLOW}Please upload the Debian 12 ISO or update the ISO_FILE variable${NC}"
    exit 1
fi

echo -e "${GREEN}Creating VM...${NC}"

# Create the VM
qm create $VM_ID \
    --name $VM_NAME \
    --memory $MEMORY \
    --cores $CORES \
    --net0 virtio,bridge=vmbr0 \
    --scsihw virtio-scsi-pci

echo -e "${GREEN}Configuring storage...${NC}"

# Import and attach the ISO
qm set $VM_ID --ide2 $ISO_STORAGE:iso/$ISO_FILE,media=cdrom

# Create and attach the main disk
qm set $VM_ID --scsi0 $STORAGE:$DISK_SIZE

# Set boot order
qm set $VM_ID --boot order=scsi0

# Enable QEMU guest agent (install after OS setup)
qm set $VM_ID --agent enabled=1

# Set VGA to std (better compatibility during install)
qm set $VM_ID --vga std

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}VM $VM_ID created successfully!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo -e "  1. Start the VM: ${GREEN}qm start $VM_ID${NC}"
echo -e "  2. Open console: ${GREEN}In Proxmox web UI, click on VM $VM_ID > Console${NC}"
echo -e "  3. Install Debian 12:"
echo -e "     - Hostname: postgresql-server"
echo -e "     - Domain: (leave blank or use local)"
echo -e "     - Root password: (set a strong password)"
echo -e "     - User: debian"
echo -e "     - Partitioning: Guided - use entire disk"
echo -e "     - Software selection: SSH server, standard system utilities"
echo -e "  4. After install, configure static IP in /etc/network/interfaces"
echo -e "  5. Install QEMU guest agent: ${GREEN}apt-get install qemu-guest-agent${NC}"
echo -e "  6. Run the Docker installation script"
echo ""
echo -e "${YELLOW}Configuration summary:${NC}"
echo -e "  VM ID:     $VM_ID"
echo -e "  Name:      $VM_NAME"
echo -e "  CPU:       $CORES cores"
echo -e "  RAM:       $(($MEMORY / 1024))GB"
echo -e "  Disk:      $DISK_SIZE on $STORAGE"
echo -e "  Network:   virtio on vmbr0"
echo ""
