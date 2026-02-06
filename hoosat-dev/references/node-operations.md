# Node Operations Guide

Guide for setting up and operating Hoosat nodes.

## Overview

Hoosat nodes can be run using:
- **Docker** - Easiest setup method
- **Pre-built Binaries** - Download and run directly
- **Build from Source** - Compile from GitHub repository

## System Requirements

### Minimum Requirements
- **CPU**: 4 cores
- **RAM**: 8 GB
- **Storage**: 100 GB SSD
- **Network**: Stable internet connection, port 42420 open

### Recommended Requirements
- **CPU**: 8+ cores
- **RAM**: 16+ GB
- **Storage**: 500+ GB NVMe SSD
- **Network**: Dedicated connection, ports 42420 (P2P) and 42421 (RPC) open

## Docker Deployment

### Quick Start with Docker

```bash
# Pull the Hoosat node image
docker pull hoosatnetwork/hoosat-node:latest

# Run mainnet node
docker run -d \
  --name hoosat-node \
  -p 42420:42420 \
  -p 42421:42421 \
  -v hoosat-data:/data \
  hoosatnetwork/hoosat-node:latest \
  --mainnet \
  --rpclisten=0.0.0.0:42421 \
  --rpccorsdomain=*

# Check logs
docker logs -f hoosat-node
```

### Docker Compose Configuration

```yaml
# docker-compose.yml
version: '3.8'

services:
  hoosat-node:
    image: hoosatnetwork/hoosat-node:latest
    container_name: hoosat-node
    restart: unless-stopped
    ports:
      - "42420:42420"  # P2P
      - "42421:42421"  # RPC
    volumes:
      - ./data:/data
      - ./logs:/logs
    command:
      - --mainnet
      - --appdata=/data
      - --logdir=/logs
      - --rpclisten=0.0.0.0:42421
      - --rpccorsdomain=*
      - --utxoindex
    environment:
      - HOOSAT_NETWORK=mainnet
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:42421"]
      interval: 30s
      timeout: 10s
      retries: 3
```

```bash
# Start with docker-compose
docker-compose up -d

# View logs
docker-compose logs -f

# Stop node
docker-compose down
```

## Binary Installation

### Download Pre-built Binary

```bash
# Download latest release
wget https://github.com/hoosatnetwork/hoosat/releases/latest/download/hoosat-linux-amd64.tar.gz

# Extract
tar -xzf hoosat-linux-amd64.tar.gz
cd hoosat-linux-amd64

# Make executable
chmod +x hoosat

# Move to system path
sudo mv hoosat /usr/local/bin/
```

### Run Node

```bash
# Create data directory
mkdir -p ~/.hoosat

# Run mainnet node
hoosat --mainnet \
  --appdata=~/.hoosat \
  --rpclisten=0.0.0.0:42421 \
  --utxoindex

# Run as daemon (systemd)
sudo systemctl enable hoosat
sudo systemctl start hoosat
```

## Building from Source

### Prerequisites

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y \
  build-essential \
  git \
  wget \
  curl \
  libssl-dev \
  pkg-config

# Install Go (required for building)
wget https://go.dev/dl/go1.21.0.linux-amd64.tar.gz
sudo tar -C /usr/local -xzf go1.21.0.linux-amd64.tar.gz
export PATH=$PATH:/usr/local/go/bin
```

### Clone and Build

```bash
# Clone repository
git clone https://github.com/hoosatnetwork/hoosat.git
cd hoosat

# Build
go build -o hoosat ./cmd/hoosat

# Or use make
make build

# Install
sudo make install
```

## Configuration

### Configuration File

```bash
# Create config directory
mkdir -p ~/.hoosat

# Create config file
cat > ~/.hoosat/hoosat.conf << EOF
# Hoosat Node Configuration

# Network
mainnet=1
# testnet=1

# RPC Settings
rpclisten=0.0.0.0:42421
rpcuser=your_rpc_username
rpcpass=your_rpc_password
rpccorsdomain=*

# UTXO Indexing
utxoindex=1

# Data Directory
appdata=/var/lib/hoosat

# Logging
logdir=/var/log/hoosat
debuglevel=info

# Performance
maxpeers=125
EOF
```

### Environment Variables

```bash
# Set environment variables
export HOOSAT_NETWORK=mainnet
export HOOSAT_RPC_USER=your_rpc_username
export HOOSAT_RPC_PASS=your_rpc_password
export HOOSAT_DATA_DIR=/var/lib/hoosat
```

## Node Types

### Full Node (Default)

Stores complete blockchain history:

```bash
hoosat --mainnet --utxoindex
```

### Pruned Node

Stores only recent blocks (saves space):

```bash
hoosat --mainnet \
  --prune=550 \
  --utxoindex
```

### RPC Node

Optimized for API access:

```bash
hoosat --mainnet \
  --utxoindex \
  --rpclisten=0.0.0.0:42421 \
  --rpccorsdomain=* \
  --rpcmaxclients=100
```

## Command Line Options

### Network Options

```bash
--mainnet                    # Connect to mainnet (default)
--testnet                    # Connect to testnet
--devnet                     # Connect to devnet
--connect=IP:PORT            # Connect to specific peer
--noconnect                  # Disable automatic peer connections
--maxpeers=N                 # Maximum number of peers (default: 125)
```

### RPC Options

```bash
--rpclisten=IP:PORT          # RPC listen address (default: localhost:42421)
--rpcuser=USERNAME           # RPC username
--rpcpass=PASSWORD           # RPC password
--rpccorsdomain=DOMAIN       # Allowed CORS domains
--rpcmaxclients=N            # Maximum RPC clients (default: 10)
--rpcquirks                  # Enable RPC quirks for compatibility
```

### Indexing Options

```bash
--utxoindex                  # Enable UTXO index (required for balance queries)
--addrindex                  # Enable address index
--txindex                    # Enable transaction index
```

### Performance Options

```bash
--dbcache=N                  # Database cache size in MB (default: 450)
--maxorphantx=N              # Max orphan transactions (default: 100)
--blocksonly                 # Do not accept transactions from network
```

### Logging Options

```bash
--logdir=PATH                # Log directory
--debuglevel=LEVEL           # Debug level: trace, debug, info, warn, error, critical
--logtimestamps              # Add timestamps to logs
```

## Monitoring

### Node Status

```bash
# Check if node is running
curl -X POST http://localhost:42421 \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"getBlockCount","params":[],"id":1}'

# Get network info
curl -X POST http://localhost:42421 \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "getBlockDagInfo",
    "params": [],
    "id": 1
  }'
```

### Health Check Script

```bash
#!/bin/bash
# health-check.sh

NODE_URL="http://localhost:42421"

response=$(curl -s -X POST "$NODE_URL" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"getBlockCount","params":[],"id":1}')

if [ $? -eq 0 ]; then
  block_count=$(echo "$response" | jq -r '.result')
  echo "Node is healthy. Block count: $block_count"
  exit 0
else
  echo "Node is not responding"
  exit 1
fi
```

### Prometheus Metrics

Enable metrics endpoint:

```bash
hoosat --mainnet --prometheus=0.0.0.0:2112
```

Metrics available at `http://localhost:2112/metrics`:
- `hoosat_blocks_total`
- `hoosat_peers_connected`
- `hoosat_mempool_size`
- `hoosat_utxos_indexed`

### Grafana Dashboard

```bash
# Download dashboard JSON
wget https://raw.githubusercontent.com/hoosatnetwork/hoosat/main/grafana-dashboard.json

# Import to Grafana
# 1. Go to Create > Import
# 2. Upload dashboard JSON
# 3. Select Prometheus data source
```

## Backup and Recovery

### Backup

```bash
# Stop node
sudo systemctl stop hoosat

# Backup data directory
tar -czf hoosat-backup-$(date +%Y%m%d).tar.gz ~/.hoosat

# Backup wallet (if applicable)
cp ~/.hoosat/wallet.db hoosat-wallet-$(date +%Y%m%d).backup

# Start node
sudo systemctl start hoosat
```

### Restore

```bash
# Stop node
sudo systemctl stop hoosat

# Remove old data
rm -rf ~/.hoosat

# Restore from backup
tar -xzf hoosat-backup-20240101.tar.gz -C ~

# Start node
sudo systemctl start hoosat
```

## Security

### Firewall Configuration

```bash
# UFW (Ubuntu)
sudo ufw allow 42420/tcp  # P2P
sudo ufw allow 42421/tcp  # RPC (restrict to localhost if possible)
sudo ufw enable

# iptables
sudo iptables -A INPUT -p tcp --dport 42420 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 42421 -s 127.0.0.1 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 42421 -j DROP
```

### RPC Security

```bash
# Never expose RPC to internet without authentication
# Use reverse proxy with SSL

# Nginx configuration
server {
    listen 443 ssl;
    server_name hoosat-rpc.yourdomain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        auth_basic "Hoosat RPC";
        auth_basic_user_file /etc/nginx/.htpasswd;
        
        proxy_pass http://localhost:42421;
        proxy_http_version 1.1;
    }
}
```

## Troubleshooting

### Common Issues

#### Node Not Syncing

```bash
# Check peer connections
curl -X POST http://localhost:42421 \
  -d '{"jsonrpc":"2.0","method":"getPeerInfo","params":[],"id":1}'

# Add bootstrap nodes
hoosat --mainnet --connect=54.38.176.95:42420
```

#### High Memory Usage

```bash
# Reduce cache size
hoosat --mainnet --dbcache=256

# Enable pruning
hoosat --mainnet --prune=550
```

#### Disk Space Issues

```bash
# Check data directory size
du -sh ~/.hoosat

# Enable pruning to save space
hoosat --mainnet --prune=550

# Or use pruned Docker image
docker run hoosatnetwork/hoosat-node:pruned
```

### Logs

```bash
# View logs
journalctl -u hoosat -f

# Or Docker logs
docker logs -f hoosat-node

# Debug level logs
hoosat --mainnet --debuglevel=debug
```

## Maintenance

### Update Node

```bash
# Docker
docker pull hoosatnetwork/hoosat-node:latest
docker-compose up -d

# Binary
# 1. Download new version
# 2. Stop node
# 3. Replace binary
# 4. Start node

# Systemd
sudo systemctl stop hoosat
sudo mv hoosat-new /usr/local/bin/hoosat
sudo systemctl start hoosat
```

### Database Maintenance

```bash
# Compact database (may take a while)
hoosat --mainnet --dbcompact

# Rebuild indexes
hoosat --mainnet --reindex
```

## Links

- **GitHub**: https://github.com/hoosatnetwork/hoosat
- **Docker Hub**: https://hub.docker.com/r/hoosatnetwork/hoosat-node
- **Documentation**: https://hub.hoosat.net/docs/
- **Discord**: https://discord.gg/mFBfNpNA
