#!/bin/bash

echo "Updating GitHub repository with current changes..."

# Check for GITHUB_TOKEN
if [ -z "$GITHUB_TOKEN" ]; then
  echo "Error: GITHUB_TOKEN is not set. Please set it in the Replit Secrets tab."
  exit 1
fi

# Configure Git with token authentication
git config --global credential.helper store
echo "https://oauth2:${GITHUB_TOKEN}@github.com" > ~/.git-credentials

# Stage all changes
echo "Adding all changes..."
git add .

# Get a timestamp for the commit message
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# Commit the changes
echo "Committing changes..."
git commit -m "Update from Replit - ${TIMESTAMP}"

# Push to GitHub
echo "Pushing to GitHub..."
git push origin main

# Clean up credentials for security
rm ~/.git-credentials

echo "Successfully updated GitHub repository!"
