#!/bin/bash

# Configuration
KEY_FILE="aws_alpaca_huzhongxing.pem"
SERVER_HOST="ec2-13-60-11-227.eu-north-1.compute.amazonaws.com"
USER="ubuntu"
REMOTE_DIR="/home/ubuntu/Alpaca_Bot"
REMOTE_IMG="live_performance.png"
LOCAL_IMG="live_performance.png"

echo "--- Downloading Performance Report ---"

# Fix permissions
chmod 400 $KEY_FILE

# 1. Generate latest chart on server
echo "Step 1: Generating latest chart on server..."
ssh -i $KEY_FILE $USER@$SERVER_HOST "cd $REMOTE_DIR && python3 track_performance.py"

if [ $? -ne 0 ]; then
    echo "⚠️ Failed to generate chart (maybe no data yet?). Trying to download anyway..."
fi

# 2. Download image
echo "Step 2: Downloading $REMOTE_IMG..."
scp -i $KEY_FILE $USER@$SERVER_HOST:$REMOTE_DIR/$REMOTE_IMG ./$LOCAL_IMG

if [ $? -eq 0 ]; then
    echo "✅ Download successful! Check $LOCAL_IMG in your current directory."
    # Try to open it (macOS)
    open $LOCAL_IMG
else
    echo "❌ Download failed. Check SSH connection or if file exists."
fi
