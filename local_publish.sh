#!/bin/bash

echo "--- Starting Local Publish ---"

# 1. Add all changes
echo "Step 1: Staging changes..."
git add .

# 2. Commit with timestamp
TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")
echo "Step 2: Committing with timestamp: $TIMESTAMP"
git commit -m "Update strategy: $TIMESTAMP"

# 3. Push to GitHub
echo "Step 3: Pushing to GitHub..."
git push origin main

if [ $? -eq 0 ]; then
    echo "✅ Local publish successful! Code is now on GitHub."
    echo "👉 Now log in to your AWS server and run './remote_update.sh'"
else
    echo "❌ Publish failed. Please check git status."
fi
