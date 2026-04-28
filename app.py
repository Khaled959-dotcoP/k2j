#!/usr/bin/env python3
# K2J ARMORY - PYTHON BACKEND
# Full English, No email required, SQLite database

from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import hashlib
import time
import socket
import json
import threading

app = Flask(__name__)
CORS(app)
DB_PATH = 'k2j_armory.db'

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# Send message to C++ integrator
def send_to_cpp(action, username, fingerprint):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('localhost', 8081))
        data = json.dumps({'action': action, 'username': username, 'fp': fingerprint, 'timestamp': time.time()})
        sock.send(data.encode())
        sock.close()
    except:
        pass

# Send to Java detector
def send_to_java(action, username, fingerprint):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('localhost', 8082))
        data = json.dumps({'action': action, 'username': username, 'fp': fingerprint})
        sock.send(data.encode())
        sock.close()
    except:
        pass

# Log to database
def log_to_db(source, action, username, fingerprint):
    conn = get_db()
    conn.execute("INSERT INTO logs (timestamp, source, action, username, fingerprint) VALUES (?, ?, ?, ?, ?)",
                 (int(time.time()), source, action, username, fingerprint))
    conn.commit()
    conn.close()

# ==================== API ENDPOINTS ====================

@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username', '').strip()
    password = data.get('password', '')
    fingerprint = request.headers.get('X-Fingerprint', 'unknown')
    
    if len(username) < 3 or len(password) < 4:
        return jsonify({'success': False, 'error': 'Invalid input'}), 400
    
    hashed = hash_password(password)
    conn = get_db()
    try:
        conn.execute("INSERT INTO users (username, password, role, created) VALUES (?, ?, 'user', ?)",
                     (username, hashed, int(time.time())))
        conn.commit()
        log_to_db("PYTHON", "REGISTER", username, fingerprint)
        send_to_cpp("REGISTER", username, fingerprint)
        send_to_java("REGISTER", username, fingerprint)
        return jsonify({'success': True})
    except sqlite3.IntegrityError:
        return jsonify({'success': False, 'error': 'Username exists'}), 400
    finally:
        conn.close()

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username', '').strip()
    password = hash_password(data.get('password', ''))
    fingerprint = request.headers.get('X-Fingerprint', 'unknown')
    
    conn = get_db()
    user = conn.execute("SELECT id, username, role FROM users WHERE username=? AND password=?", 
                        (username, password)).fetchone()
    conn.close()
    
    if user:
        log_to_db("PYTHON", "LOGIN_SUCCESS", username, fingerprint)
        send_to_cpp("LOGIN", username, fingerprint)
        send_to_java("LOGIN", username, fingerprint)
        return jsonify({'success': True, 'user': {'username': user['username'], 'role': user['role']}})
    
    log_to_db("PYTHON", "LOGIN_FAILED", username, fingerprint)
    return jsonify({'success': False}), 401

@app.route('/api/inventory/list', methods=['POST'])
def list_inventory():
    data = request.json
    item_type = data.get('type', 'all')
    sort = data.get('sort', 'default')
    search = data.get('search', '')
    fingerprint = request.headers.get('X-Fingerprint', 'unknown')
    
    conn = get_db()
    query = "SELECT * FROM inventory WHERE 1=1"
    params = []
    
    if item_type != 'all':
        query += " AND type = ?"
        params.append(item_type)
    
    if search:
        query += " AND (seller LIKE ? OR caliber LIKE ?)"
        params.extend([f'%{search}%', f'%{search}%'])
    
    if sort == 'priceAsc':
        query += " ORDER BY price ASC"
    elif sort == 'priceDesc':
        query += " ORDER BY price DESC"
    else:
        query += " ORDER BY id DESC"
    
    items = conn.execute(query, params).fetchall()
    conn.close()
    
    log_to_db("PYTHON", "INVENTORY_VIEW", fingerprint, fingerprint)
    
    return jsonify({
        'items': [{
            'id': i['id'],
            'year': i['year'],
            'price': i['price'],
            'caliber': i['caliber'],
            'type': i['type'],
            'img': i['img'],
            'seller': i['seller'],
            'location': i['location']
        } for i in items]
    })

if __name__ == '__main__':
    print("[K2J Python] Starting Flask server...")
    print("[Python] Connected to C++ on port 8081")
    print("[Python] Connected to Java on port 8082")
    app.run(host='0.0.0.0', port=5000, debug=False)