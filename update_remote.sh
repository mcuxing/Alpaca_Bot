#!/bin/bash

# Configuration
KEY_FILE="aws_alpaca_huzhongxing.pem"
SERVER_IP="13.60.11.227"
USER="ubuntu"
PROJECT_DIR="Alpaca_Bot"

echo "--- Starting One-Click Update ---"

# 1. Local Commit & Push
echo "Step 1: Pushing local changes to GitHub..."
git add .
git commit -m "Auto-update from Trae"
git push origin main

if [ $? -ne 0 ]; then
    echo "❌ Git push failed. Please check your local git config."
    exit 1
fi

# 2. Remote Pull & Restart
echo "Step 2: Updating remote server..."
ssh -i $KEY_FILE -o StrictHostKeyChecking=no $USER@$SERVER_IP << EOF
    cd $PROJECT_DIR
    
    echo ">>> Pulling latest code..."
    git pull origin main
    
    echo ">>> Restarting background service..."
    sudo systemctl restart alpaca-bot
    
    echo ">>> Checking service status..."
    sudo systemctl status alpaca-bot --no-pager | grep "Active:"
EOF

if [ $? -eq 0 ]; then
    echo "✅ Update Complete! Your strategy is now live on AWS."
else
    echo "❌ Remote update failed. Please check SSH connection."
fi
