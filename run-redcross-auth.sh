#!/bin/bash

# Red Cross ArcGIS Authentication Runner
# This script helps you run the authentication automation

echo "🔴 Red Cross ArcGIS Authentication Tool"
echo "======================================="
echo ""

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js first."
    exit 1
fi

# Check if Playwright is installed
if [ ! -d "node_modules/playwright" ]; then
    echo "📦 Installing Playwright..."
    npm install playwright
    npx playwright install chromium
fi

# Ask for credentials if not in environment
if [ -z "$REDCROSS_USERNAME" ]; then
    echo "Enter your Red Cross username (email):"
    read -r REDCROSS_USERNAME
    export REDCROSS_USERNAME
fi

if [ -z "$REDCROSS_PASSWORD" ]; then
    echo "Enter your Red Cross password:"
    read -rs REDCROSS_PASSWORD
    export REDCROSS_PASSWORD
    echo ""
fi

echo ""
echo "🚀 Starting authentication process..."
echo "📍 The browser will open and automate the login"
echo "🔐 If 2FA is required, please complete it in the browser"
echo ""

# Run the authentication script
node redcross-auth-automation.js

echo ""
echo "✅ Process completed"