#!/bin/bash

echo "=============================================="
echo "K2J ARMORY - FULL SYSTEM START"
echo "=============================================="

# Create database
sqlite3 k2j_armory.db < k2j_database.sql
echo "[OK] Database ready"

# Compile C++
g++ -o k2j_integrator k2j_integrator.cpp -lpthread -ljsoncpp 2>/dev/null || g++ -o k2j_integrator k2j_integrator.cpp -lpthread
echo "[OK] C++ integrator compiled"

# Compile C
gcc -o k2j_c_filter k2j_c_filter.c -lpthread
echo "[OK] C filter compiled"

# Compile Java
javac K2JDetector.java
echo "[OK] Java detector compiled"

# Start all services
echo ""
echo "Starting services..."

python3 app.py &
PID1=$!

./k2j_integrator &
PID2=$!

./k2j_c_filter &
PID3=$!

java K2JDetector &
PID4=$!

echo ""
echo "=============================================="
echo "ALL SERVICES RUNNING"
echo "=============================================="
echo "Python (API):      PID $PID1 - http://localhost:5000"
echo "C++ (Integrator):  PID $PID2"
echo "C (Filter):        PID $PID3"
echo "Java (DDoS):       PID $PID4"
echo ""
echo "Open Firefox/Edge: http://localhost:5000"
echo "Chrome is BLOCKED"
echo ""
echo "Stop all: pkill -f 'python3 app.py|k2j_integrator|k2j_c_filter|K2JDetector'"
echo "=============================================="

wait