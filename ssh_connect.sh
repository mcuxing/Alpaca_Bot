#!/bin/bash

# Configuration
KEY_FILE="aws_alpaca_huzhongxing.pem"
# Use Public DNS instead of IP to avoid potential firewall issues
SERVER_HOST="ec2-13-60-11-227.eu-north-1.compute.amazonaws.com"
USER="ubuntu"

echo "--- Connecting to AWS Server ($SERVER_HOST) ---"
echo "Note: Type 'exit' to return to Trae terminal."

# Fix key permissions just in case
chmod 400 $KEY_FILE

# Connect
ssh -i $KEY_FILE $USER@$SERVER_HOST
