#!/bin/bash

# This script is meant to be run on the AWS Server
PROJECT_DIR="/home/ubuntu/Alpaca_Bot"

echo "--- Starting Remote Update ---"

# 1. Navigate to directory
cd $PROJECT_DIR

# 2. Pull latest code
echo "Step 1: Pulling latest code from GitHub..."
git pull origin main

if [ $? -ne 0 ]; then
    echo "❌ Git pull failed. Please check network connection."
    exit 1
fi

# 3. Restart Service
echo "Step 2: Restarting background bot..."
sudo systemctl restart alpaca-bot

# 4. Check Status
echo "Step 3: Checking status..."
sleep 2
sudo systemctl status alpaca-bot --no-pager | grep "Active:"

echo "✅ Remote update complete! Bot is running with new code."
