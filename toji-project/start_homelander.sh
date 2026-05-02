#!/bin/bash
# HOMELANDER Bot Startup Script

echo "🔴 Starting HOMELANDER Backend..."
cd backend
python3 main.py &
BACKEND_PID=$!

echo "🔴 Starting HOMELANDER Telegram Bot..."
cd ../bot
python3 toji_bot.py &
BOT_PID=$!

echo "✅ Backend running (PID: $BACKEND_PID)"
echo "✅ Bot running (PID: $BOT_PID)"
echo ""
echo "Press Ctrl+C to stop all services"

wait
