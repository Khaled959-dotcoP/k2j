#!/bin/bash

echo "=============================================="
echo "K2J ARMORY - FULL MULTI-LANGUAGE SYSTEM"
echo "=============================================="

# Initialize database
echo "[1/6] Initializing SQLite database..."
sqlite3 k2j_armory.db < init_db.sql

# Install Python dependencies
echo "[2/6] Installing Python dependencies..."
pip3 install flask flask-cors

# Compile C++ integrator
echo "[3/6] Compiling C++ integrator..."
g++ -o k2j_integrator k2j_integrator.cpp -lpthread -lsqlite3 -ljsoncpp 2>/dev/null || g++ -o k2j_integrator k2j_integrator.cpp -lpthread -lsqlite3

# Compile C filter
echo "[4/6] Compiling C filter..."
gcc -o k2j_c_filter k2j_c_filter.c -lpthread

# Compile Java detector
echo "[5/6] Compiling Java detector..."
javac K2JDetector.java

# Start all services
echo "[6/6] Starting all services..."
echo ""

python3 app.py &
PID1=$!
echo "[Python] Started with PID: $PID1 (port 5000)"

./k2j_integrator &
PID2=$!
echo "[C++] Started with PID: $PID2 (port 9090)"

./k2j_c_filter &
PID3=$!
echo "[C] Started with PID: $PID3 (port 9092)"

java K2JDetector &
PID4=$!
echo "[Java] Started with PID: $PID4 (ports 9091, 9093)"

echo ""
echo "=============================================="
echo "ALL SERVICES RUNNING"
echo "=============================================="
echo "Frontend: Open index.html in browser"
echo "API: http://localhost:5000"
echo ""
echo "To stop all: pkill -f 'python3 app.py|k2j_integrator|k2j_c_filter|K2JDetector'"
echo "=============================================="

wait
