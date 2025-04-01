#!/bin/bash

echo "Fetching latest changes from GitHub..."
git fetch origin

# Check if there are changes to pull
if git status | grep -q "Your branch is behind"; then
  echo "New changes found on GitHub! Pulling changes..."
  git pull origin main
  echo "Repository updated successfully!"
else
  echo "Your repository is already up to date with GitHub."
fi