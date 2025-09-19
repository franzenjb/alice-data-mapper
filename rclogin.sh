#!/bin/bash

# Red Cross Quick Login
# Just type: ./rclogin.sh

echo "🔴 Red Cross Quick Login"
echo "========================"
echo ""

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed"
    exit 1
fi

# Check if Playwright is installed
if [ ! -d "node_modules/playwright" ]; then
    echo "📦 Installing Playwright..."
    npm install playwright
    npx playwright install chromium
fi

# Run the quick login script
node redcross-quicklogin-auto.js