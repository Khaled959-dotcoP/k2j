#!/bin/bash

echo "=============================================="
echo "K2J ARMORY - STARTING ALL SERVICES"
echo "=============================================="

# Python setup
pip3 install flask flask-cors

# Compile C++
echo "[1/4] Compiling C++ integrator..."
g++ -o k2j_integrator k2j_integrator.cpp -lpthread

# Compile C
echo "[2/4] Compiling C filter..."
gcc -o k2j_c_filter k2j_c_filter.c -lpthread

# Compile Java
echo "[3/4] Compiling Java detector..."
javac K2JDetector.java

# Start all
echo "[4/4] Starting services..."
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
echo "Python (Flask): PID $PID1 - http://localhost:5000"
echo "C++ Integrator: PID $PID2 - Port 9090"
echo "C Filter:       PID $PID3 - Port 9092"
echo "Java Detector:  PID $PID4 - Port 9091"
echo ""
echo "Open index.html in browser"
echo "To stop: pkill -f 'python3 app.py|k2j_integrator|k2j_c_filter|K2JDetector'"
echo "=============================================="

wait
