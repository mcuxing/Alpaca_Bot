#!/bin/bash

# Configuration
KEY_FILE="aws_alpaca_huzhongxing.pem"
SERVER_IP="13.60.11.227"
USER="ubuntu"
API_KEY_FILE="paper_account_api_key.txt"

echo "--- Starting Deployment to $SERVER_IP ---"

# 1. Fix Key Permissions
chmod 400 $KEY_FILE

# 2. Upload API Key
echo "Step 1: Uploading API Key..."
scp -i $KEY_FILE -o StrictHostKeyChecking=no $API_KEY_FILE $USER@$SERVER_IP:~/
if [ $? -ne 0 ]; then
    echo "❌ Upload failed. Please check if the server is reachable."
    exit 1
fi

# 3. Remote Execution
echo "Step 2: Configuring Server & Deploying Code..."
ssh -i $KEY_FILE -o StrictHostKeyChecking=no $USER@$SERVER_IP << 'EOF'

# A. Update System & Install Deps
echo ">>> Updating system..."
sudo apt update -qq
sudo apt install python3-pip git -y -qq

# B. Clone Repository
echo ">>> Cloning repository..."
if [ -d "Alpaca_Bot" ]; then
    echo "Repository already exists, pulling latest..."
    cd Alpaca_Bot
    git pull
else
    git clone https://github.com/mcuxing/Alpaca_Bot.git
    cd Alpaca_Bot
fi

# C. Install Python Dependencies
echo ">>> Installing Python dependencies..."
pip3 install -r requirements.txt

# D. Setup API Key
echo ">>> Setting up API Key..."
mv ~/paper_account_api_key.txt .

# E. Configure Timezone
sudo timedatectl set-timezone America/New_York

# F. Setup Systemd Service
echo ">>> Configuring background service..."
sudo bash -c 'cat > /etc/systemd/system/alpaca-bot.service << EOL
[Unit]
Description=Alpaca Trading Bot Scheduler
After=network.target

[Service]
Type=simple
WorkingDirectory=/home/ubuntu/Alpaca_Bot
ExecStart=/usr/bin/python3 scheduler.py
Restart=always
RestartSec=10
User=ubuntu

[Install]
WantedBy=multi-user.target
EOL'

# G. Start Service
echo ">>> Starting service..."
sudo systemctl daemon-reload
sudo systemctl enable alpaca-bot
sudo systemctl restart alpaca-bot

echo "✅ Deployment Complete! Service status:"
sudo systemctl status alpaca-bot --no-pager
EOF
