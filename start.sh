#!/bin/bash

echo "🚀 Starting AI Social Media Manager MVP..."
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate 2>/dev/null || . venv/Scripts/activate 2>/dev/null

# Install dependencies if needed
echo "📦 Checking dependencies..."
pip install -q -r requirements.txt 2>/dev/null

# Check for .env file
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found! Creating from .env.example..."
    cp .env.example .env
    echo "✅ Please edit .env with your API keys"
fi

# Start Flask backend in background
echo "🔧 Starting Flask backend on port 5000..."
python3 app.py &
FLASK_PID=$!

# Wait a moment for Flask to start
sleep 2

# Start Streamlit dashboard
echo "🎨 Starting Streamlit dashboard on port 8501..."
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🌟 Application is ready!"
echo ""
echo "📊 Dashboard: http://localhost:8501"
echo "🔧 API: http://localhost:5000"
echo ""
echo "Press Ctrl+C to stop all services"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Start Streamlit (this will block)
streamlit run dashboard.py

# Cleanup on exit
echo ""
echo "🛑 Shutting down services..."
kill $FLASK_PID 2>/dev/null
echo "✅ All services stopped"