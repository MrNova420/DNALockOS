# 🚀 Quick Start Guide - All Platforms & Devices

## Start DNA-Key Authentication System on ANY Device

This guide shows you how to start and use the DNA-Key Authentication System on any device, operating system, or platform.

---

## 📱 Table of Contents

- [Windows](#-windows)
- [macOS](#-macos)
- [Linux](#-linux)
- [Docker](#-docker)
- [Cloud Platforms](#-cloud-platforms)
- [Mobile Devices](#-mobile-devices)
- [Embedded Systems](#-embedded-systems)
- [Web Browsers](#-web-browsers)

---

## 💻 Windows

### Method 1: Native Windows Installation

#### Prerequisites
```powershell
# Install Python 3.12+ from Microsoft Store or python.org
winget install Python.Python.3.12

# Install Node.js
winget install OpenJS.NodeJS.LTS

# Install Git
winget install Git.Git
```

#### Backend Setup
```powershell
# Open PowerShell as Administrator
cd C:\Users\YourName\Documents

# Clone repository
git clone https://github.com/MrNova420/DNALockOS.git
cd DNALockOS

# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Start backend server
python -m server.api.main
```

Backend runs at: `http://localhost:8000`

#### Frontend Setup
```powershell
# Open new PowerShell window
cd C:\Users\YourName\Documents\DNALockOS\web\frontend

# Install dependencies
npm install

# Start frontend
npm run dev
```

Frontend runs at: `http://localhost:3000`

### Method 2: Windows Subsystem for Linux (WSL)

```powershell
# Enable WSL
wsl --install

# Start Ubuntu
wsl

# Follow Linux instructions below
```

### Method 3: Windows with Chocolatey

```powershell
# Install Chocolatey first
Set-ExecutionPolicy Bypass -Scope Process -Force
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Install dependencies
choco install python nodejs git -y

# Follow standard Windows installation
```

---

## 🍎 macOS

### Method 1: Native macOS Installation

#### Prerequisites
```bash
# Install Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install dependencies
brew install python@3.12 node git
```

#### Backend Setup
```bash
# Clone repository
cd ~/Documents
git clone https://github.com/MrNova420/DNALockOS.git
cd DNALockOS

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start backend
python -m server.api.main
```

#### Frontend Setup
```bash
# Open new terminal
cd ~/Documents/DNALockOS/web/frontend

# Install dependencies
npm install

# Start frontend
npm run dev
```

### Method 2: Using MacPorts

```bash
# Install MacPorts first from macports.org
sudo port install python312 nodejs20 git

# Follow standard macOS installation
```

---

## 🐧 Linux

### Ubuntu / Debian

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install python3.12 python3.12-venv python3-pip nodejs npm git -y

# Clone repository
cd ~
git clone https://github.com/MrNova420/DNALockOS.git
cd DNALockOS

# Backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m server.api.main &

# Frontend
cd web/frontend
npm install
npm run dev &

# Access
xdg-open http://localhost:3000
```

### Fedora / RHEL / CentOS

```bash
# Install dependencies
sudo dnf install python3.12 python3-pip nodejs npm git -y

# Clone and setup (same as Ubuntu)
git clone https://github.com/MrNova420/DNALockOS.git
cd DNALockOS

# Follow Ubuntu instructions above
```

### Arch Linux

```bash
# Install dependencies
sudo pacman -S python python-pip nodejs npm git

# Clone and setup
git clone https://github.com/MrNova420/DNALockOS.git
cd DNALockOS

# Follow Ubuntu instructions above
```

### openSUSE

```bash
# Install dependencies
sudo zypper install python312 python3-pip nodejs npm git

# Follow Ubuntu instructions
```

---

## 🐳 Docker

### Method 1: Docker Compose (Easiest)

```bash
# Clone repository
git clone https://github.com/MrNova420/DNALockOS.git
cd DNALockOS

# Create docker-compose.yml
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - API_HOST=0.0.0.0
      - API_PORT=8000
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  web:
    build: ./web/frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
    depends_on:
      - api
    restart: unless-stopped

volumes:
  data:
EOF

# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Method 2: Standalone Docker

```bash
# Build and run backend
docker build -t dnakey-api .
docker run -d -p 8000:8000 --name dnakey-api dnakey-api

# Build and run frontend
cd web/frontend
docker build -t dnakey-web .
docker run -d -p 3000:3000 --name dnakey-web \
  -e NEXT_PUBLIC_API_URL=http://localhost:8000 \
  dnakey-web
```

### Method 3: Docker with Portainer

```bash
# Install Portainer
docker volume create portainer_data
docker run -d -p 9000:9000 --name portainer \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v portainer_data:/data \
  portainer/portainer-ce

# Access Portainer at http://localhost:9000
# Deploy DNALockOS through Portainer UI
```

---

## ☁️ Cloud Platforms

### AWS EC2

```bash
# Launch EC2 instance (Ubuntu 22.04)
# SSH into instance
ssh -i your-key.pem ubuntu@your-ec2-ip

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu

# Deploy with Docker Compose
git clone https://github.com/MrNova420/DNALockOS.git
cd DNALockOS
docker-compose up -d

# Configure security group to allow ports 3000 and 8000
# Access at http://your-ec2-ip:3000
```

### Google Cloud Platform (GCP)

```bash
# Create Compute Engine instance
gcloud compute instances create dnakey-server \
  --image-family=ubuntu-2204-lts \
  --image-project=ubuntu-os-cloud \
  --machine-type=e2-medium \
  --boot-disk-size=20GB

# SSH into instance
gcloud compute ssh dnakey-server

# Follow Ubuntu installation steps
```

### Microsoft Azure

```bash
# Create VM
az vm create \
  --resource-group DNAKeyRG \
  --name dnakey-vm \
  --image Ubuntu2204 \
  --size Standard_B2s \
  --admin-username azureuser

# SSH and install
ssh azureuser@your-vm-ip
# Follow Ubuntu installation steps
```

### DigitalOcean

```bash
# Create Droplet (Ubuntu 22.04)
doctl compute droplet create dnakey \
  --image ubuntu-22-04-x64 \
  --size s-2vcpu-2gb \
  --region nyc1

# SSH and install
ssh root@your-droplet-ip
# Follow Ubuntu installation steps
```

### Heroku

```bash
# Install Heroku CLI
curl https://cli-assets.heroku.com/install.sh | sh

# Create app
heroku create dnakey-app

# Deploy backend
git push heroku main

# Scale dynos
heroku ps:scale web=1

# View logs
heroku logs --tail
```

---

## 📱 Mobile Devices

### Android

#### Method 1: Termux (On-Device)

```bash
# Install Termux from F-Droid or Google Play
# Open Termux

# Update packages
pkg update && pkg upgrade

# Install dependencies
pkg install python nodejs git

# Clone and run
cd ~
git clone https://github.com/MrNova420/DNALockOS.git
cd DNALockOS

# Backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m server.api.main &

# Access from Android browser
# http://localhost:8000
```

#### Method 2: UserLAnd

```bash
# Install UserLAnd app
# Create Ubuntu session
# Follow Linux Ubuntu instructions
```

#### Method 3: Remote Access

```bash
# Install JuiceSSH
# Connect to your server
# Access web interface through Android browser
```

### iOS / iPadOS

#### Method 1: iSH Shell

```bash
# Install iSH from App Store
# Open iSH

# Install dependencies
apk add python3 nodejs npm git

# Clone and run
git clone https://github.com/MrNova420/DNALockOS.git
cd DNALockOS

# Follow Alpine Linux steps
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m server.api.main
```

#### Method 2: Remote Access

```bash
# Use any SSH client (Termius, Blink)
# Connect to remote server
# Access via Safari
```

---

## 🔌 Embedded Systems

### Raspberry Pi

```bash
# SSH into Raspberry Pi
ssh pi@raspberrypi.local

# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install python3.12 python3-pip nodejs npm git -y

# Clone repository
cd ~
git clone https://github.com/MrNova420/DNALockOS.git
cd DNALockOS

# Install and run
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m server.api.main &

cd web/frontend
npm install
npm run dev &

# Access from any device on network
# http://raspberrypi.local:3000
```

### NVIDIA Jetson

```bash
# SSH into Jetson
ssh nvidia@jetson.local

# Install Docker (optimized for Jetson)
sudo apt install docker.io -y
sudo usermod -aG docker $USER

# Deploy with Docker
git clone https://github.com/MrNova420/DNALockOS.git
cd DNALockOS
docker-compose up -d
```

### BeagleBone

```bash
# SSH into BeagleBone
ssh debian@beaglebone.local

# Follow Raspberry Pi instructions
```

---

## 🌐 Web Browsers

### Access Existing Instance

Simply open in any browser:
- **Local Development**: `http://localhost:3000`
- **Remote Server**: `http://your-server-ip:3000`
- **Domain**: `https://your-domain.com`

### Supported Browsers

✅ **Chrome / Chromium** - Full support  
✅ **Firefox** - Full support  
✅ **Safari** - Full support  
✅ **Edge** - Full support  
✅ **Opera** - Full support  
✅ **Brave** - Full support  

**Requirements:**
- WebGL 2.0 support (for 3D viewer)
- JavaScript enabled
- Cookies enabled
- Modern browser (last 2 years)

### Browser Extensions

#### Install as PWA (Progressive Web App)

**Chrome:**
1. Visit site
2. Click install icon in address bar
3. Click "Install"

**Firefox:**
1. Visit site
2. Click three dots menu
3. Select "Install"

**Safari (iOS):**
1. Visit site
2. Tap share button
3. Tap "Add to Home Screen"

---

## 🔧 Development Environments

### VS Code

```bash
# Install VS Code extensions
code --install-extension ms-python.python
code --install-extension dbaeumer.vscode-eslint
code --install-extension bradlc.vscode-tailwindcss

# Open project
code DNALockOS

# Run backend (Terminal 1)
python -m server.api.main

# Run frontend (Terminal 2)
cd web/frontend && npm run dev
```

### PyCharm

```bash
# Open DNALockOS folder in PyCharm
# Configure Python interpreter to use venv
# Run configurations:
#   - Backend: python -m server.api.main
#   - Tests: pytest

# Terminal for frontend
cd web/frontend && npm run dev
```

### JetBrains WebStorm

```bash
# Open web/frontend in WebStorm
# Configure npm run dev
# Built-in terminal for backend
python -m server.api.main
```

---

## 🎮 Gaming Consoles (Linux-based)

### Steam Deck

```bash
# Switch to Desktop Mode
# Open Konsole

# Install dependencies
sudo steamos-readonly disable
sudo pacman -S python nodejs npm git
sudo steamos-readonly enable

# Clone and run
git clone https://github.com/MrNova420/DNALockOS.git
cd DNALockOS

# Follow Arch Linux instructions
```

---

## 📟 Servers & Headless Systems

### Start as System Service

#### Linux Systemd Service

```bash
# Create service file
sudo nano /etc/systemd/system/dnakey-api.service
```

```ini
[Unit]
Description=DNA-Key Authentication API
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/DNALockOS
Environment="PATH=/opt/DNALockOS/venv/bin"
ExecStart=/opt/DNALockOS/venv/bin/python -m server.api.main
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start
sudo systemctl enable dnakey-api
sudo systemctl start dnakey-api
sudo systemctl status dnakey-api
```

#### Frontend Service

```bash
sudo nano /etc/systemd/system/dnakey-web.service
```

```ini
[Unit]
Description=DNA-Key Web Frontend
After=network.target dnakey-api.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/DNALockOS/web/frontend
ExecStart=/usr/bin/npm start
Restart=always
Environment="NEXT_PUBLIC_API_URL=http://localhost:8000"

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable dnakey-web
sudo systemctl start dnakey-web
```

---

## 🔐 Secure Remote Access

### SSH Tunneling

```bash
# Access remote instance securely
ssh -L 3000:localhost:3000 -L 8000:localhost:8000 user@remote-server

# Open in local browser
open http://localhost:3000
```

### VPN Access

```bash
# Connect to VPN
openvpn --config company.ovpn

# Access internal server
open http://internal-server:3000
```

### Reverse Proxy (Nginx)

```nginx
# /etc/nginx/sites-available/dnakey
server {
    listen 80;
    server_name dnakey.example.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

```bash
# Enable and restart
sudo ln -s /etc/nginx/sites-available/dnakey /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## 🚀 Quick Start Scripts

### All-in-One Start Script

Create `start.sh`:

```bash
#!/bin/bash

# DNA-Key Authentication System Start Script

echo "🔷 Starting DNA-Key Authentication System..."

# Check dependencies
command -v python3 >/dev/null 2>&1 || { echo "❌ Python not found"; exit 1; }
command -v node >/dev/null 2>&1 || { echo "❌ Node.js not found"; exit 1; }

# Start backend
echo "⚡ Starting backend..."
cd "$(dirname "$0")"
source venv/bin/activate 2>/dev/null || python3 -m venv venv && source venv/bin/activate
pip install -q -r requirements.txt
python -m server.api.main &
BACKEND_PID=$!

# Start frontend
echo "🌐 Starting frontend..."
cd web/frontend
npm install --silent
npm run dev &
FRONTEND_PID=$!

echo "✅ DNA-Key System Started!"
echo "📡 Backend: http://localhost:8000"
echo "🌐 Frontend: http://localhost:3000"
echo "📚 API Docs: http://localhost:8000/api/docs"
echo ""
echo "Press Ctrl+C to stop"

# Wait for interrupt
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait
```

```bash
# Make executable
chmod +x start.sh

# Run
./start.sh
```

### Windows Batch Script

Create `start.bat`:

```batch
@echo off
echo 🔷 Starting DNA-Key Authentication System...

REM Start backend
echo ⚡ Starting backend...
cd /d "%~dp0"
call venv\Scripts\activate.bat
pip install -q -r requirements.txt
start /B python -m server.api.main

REM Start frontend
echo 🌐 Starting frontend...
cd web\frontend
call npm install --silent
start /B npm run dev

echo ✅ DNA-Key System Started!
echo 📡 Backend: http://localhost:8000
echo 🌐 Frontend: http://localhost:3000
echo.
pause
```

---

## 📊 System Requirements

### Minimum Requirements
- **CPU**: 1 core, 1 GHz
- **RAM**: 512 MB
- **Storage**: 500 MB
- **Network**: Internet connection

### Recommended Requirements
- **CPU**: 2+ cores, 2+ GHz
- **RAM**: 2+ GB
- **Storage**: 2+ GB
- **Network**: Broadband connection

### Optimal Requirements
- **CPU**: 4+ cores, 3+ GHz
- **RAM**: 8+ GB
- **Storage**: 10+ GB SSD
- **Network**: High-speed connection

---

## ✅ Verification

After starting, verify everything works:

```bash
# Check backend
curl http://localhost:8000/health

# Expected response:
# {"status":"operational","version":"1.0.0", ...}

# Check frontend
curl http://localhost:3000

# Should return HTML
```

---

## 🆘 Troubleshooting

### Port Already in Use

```bash
# Find process using port
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill process
kill -9 <PID>  # macOS/Linux
taskkill /PID <PID> /F  # Windows

# Or use different port
python -m server.api.main --port 8080
```

### Permission Denied

```bash
# Linux/macOS
sudo chown -R $USER:$USER DNALockOS
chmod +x start.sh

# Windows
# Run as Administrator
```

### Module Not Found

```bash
# Reinstall dependencies
pip install --force-reinstall -r requirements.txt
npm install --force
```

---

**The DNA-Key Authentication System runs on EVERY platform and device!** 🚀
