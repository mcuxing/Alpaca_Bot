#!/bin/bash

# This script is meant to be run on the AWS Server
PROJECT_DIR="/home/ubuntu/Alpaca_Bot"

echo "--- Starting Remote Update ---"

# 1. Navigate to directory
cd $PROJECT_DIR

# 2. Pull latest code
echo "Step 1: Pulling latest code from GitHub..."
# Stash local changes (like the script itself) to avoid conflicts
git stash
git pull origin main

if [ $? -ne 0 ]; then
    echo "❌ Git pull failed. Please check network connection."
    exit 1
fi

# 3. Restart Service
echo "Step 2: Restarting background bot..."

# Check if service exists, if not create it
if [ ! -f /etc/systemd/system/alpaca-bot.service ]; then
    echo "⚠️ Service not found. Creating alpaca-bot.service..."
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
    sudo systemctl daemon-reload
    sudo systemctl enable alpaca-bot
fi

sudo systemctl restart alpaca-bot

# 4. Check Status
echo "Step 3: Checking status..."
sleep 2
sudo systemctl status alpaca-bot --no-pager | grep "Active:"

echo "✅ Remote update complete! Bot is running with new code."
