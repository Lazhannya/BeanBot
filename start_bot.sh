#!/bin/bash
# BeanBot Startup Script

cd "$(dirname "$0")"

echo "🤖 Starting BeanBot Reminder System..."
echo "==============================================="

# Check if .env exists and has a token
if [ ! -f ".env" ]; then
    echo "❌ Error: .env file not found!"
    echo "Please create a .env file with your DISCORD_TOKEN"
    exit 1
fi

# Check if token is set
if grep -q "your_bot_token_here" .env; then
    echo "❌ Error: Please set your Discord bot token in the .env file"
    echo ""
    echo "Steps to get your token:"
    echo "1. Go to https://discord.com/developers/applications"
    echo "2. Create a new application or select existing"
    echo "3. Go to Bot section and copy the token"
    echo "4. Edit .env and replace 'your_bot_token_here' with your token"
    exit 1
fi

# Check if virtual environment exists
if [ ! -f ".venv/bin/python" ]; then
    echo "❌ Error: Virtual environment not found at .venv/"
    echo "Please run the Python environment configuration first"
    exit 1
fi

echo "✅ Environment checks passed"
echo "✅ Virtual environment: $(python3 --version)"
echo "✅ Starting bot..."
echo ""

# Run the bot
.venv/bin/python main.py