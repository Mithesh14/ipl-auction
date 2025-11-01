#!/bin/bash
# Script to start server with ngrok tunnel for global access

echo "🚀 Starting IPL Auction Server with ngrok..."
echo ""

# Start Flask server in background
cd "$(dirname "$0")"
source venv/bin/activate
python app.py > /tmp/flask_output.log 2>&1 &
FLASK_PID=$!

# Wait for server to start
sleep 3

# Check if ngrok is installed
if ! command -v ngrok &> /dev/null; then
    echo "⚠️  ngrok is not installed!"
    echo ""
    echo "📥 Install ngrok:"
    echo "   macOS: brew install ngrok/ngrok/ngrok"
    echo "   Or download from: https://ngrok.com/download"
    echo ""
    echo "📝 Alternative: Use this command manually:"
    echo "   ngrok http 8080"
    exit 1
fi

echo "✅ Starting ngrok tunnel..."
echo ""
echo "🌐 Your public URL will appear below:"
echo ""

# Start ngrok
ngrok http 8080

# Cleanup on exit
trap "kill $FLASK_PID 2>/dev/null" EXIT

