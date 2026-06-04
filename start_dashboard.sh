#!/bin/bash
# Start local web server for INFA Contractors Dashboard

cd "$(dirname "$0")"

echo "========================================"
echo "INFA Contractors Dashboard"
echo "========================================"
echo ""
echo "Starting local web server..."
echo "Dashboard will open at: http://localhost:8000/infa_contractors_dashboard.html"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Open browser after a short delay
(sleep 2 && open "http://localhost:8000/infa_contractors_dashboard.html") &

# Start Python's built-in HTTP server
python3 -m http.server 8000
