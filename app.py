#!/usr/bin/env python3
from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import hashlib
import time
import socket
import json
import threading
import os

app = Flask(__name__)
CORS(app)
DB_PATH = "k2j_armory.db"

def hash_password(pwd):
    return hashlib.sha256(pwd.encode()).hexdigest()

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT DEFAULT 'user',
        created INTEGER,
        ip TEXT,
        fingerprint TEXT,
        device TEXT
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category TEXT,
        price INTEGER,
        caliber TEXT,
        lethal_range TEXT,
        image TEXT,
        specs TEXT,
        extra TEXT,
        created_by TEXT
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS visitors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ip TEXT,
        user_agent TEXT,
        platform TEXT,
        language TEXT,
        screen TEXT,
        timezone TEXT,
        fingerprint TEXT,
        timestamp INTEGER
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        items TEXT,
        total INTEGER,
        username TEXT,
        timestamp INTEGER
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp INTEGER,
        action TEXT,
        username TEXT,
        detail TEXT,
        ip TEXT
    )""")
    admin_pass = hash_password("MES3WAHY4XG4")
    c.execute("INSERT OR IGNORE INTO users (username, password, role, created) VALUES (?, ?, 'admin', ?)",
              ("admin", admin_pass, int(time.time())))
    c.execute("INSERT OR IGNORE INTO products (id, name, category, price, caliber, lethal_range, image, specs, extra, created_by) VALUES (1, 'AK-47', 'HEAVY', 400, '7.62x39mm', '350m', 'https://upload.wikimedia.org/wikipedia/commons/thumb/5/53/AK-47_assault_rifle.jpg/800px-AK-47_assault_rifle.jpg', 'Legendary reliability', '2 x FULL 30-ROUND MAGAZINES', 'system')")
    conn.commit()
    conn.close()
    print("[Python] Database initialized")

def log_to_db(action, username, detail, ip="unknown"):
    conn = get_db()
    conn.execute("INSERT INTO logs (timestamp, action, username, detail, ip) VALUES (?, ?, ?, ?, ?)",
                 (int(time.time()), action, username, detail, ip))
    conn.commit()
    conn.close()

def send_to_cpp(data):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('localhost', 9090))
        sock.send(json.dumps(data).encode())
        sock.close()
    except:
        pass

def send_to_java(data):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('localhost', 9091))
        sock.send(json.dumps(data).encode())
        sock.close()
    except:
        pass

def send_to_c(data):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('localhost', 9092))
        sock.send(json.dumps(data).encode())
        sock.close()
    except:
        pass

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'timestamp': time.time()})

@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username', '').strip()
    password = hash_password(data.get('password', ''))
    ip = request.remote_addr
    fingerprint = request.headers.get('X-Fingerprint', 'unknown')
    ua = request.headers.get('User-Agent', 'unknown')
    
    if len(username) < 3 or len(data.get('password', '')) < 4:
        return jsonify({'success': False, 'error': 'Invalid input'}), 400
    
    conn = get_db()
    try:
        conn.execute("INSERT INTO users (username, password, role, created, ip, fingerprint, device) VALUES (?, ?, 'user', ?, ?, ?, ?)",
                     (username, password, int(time.time()), ip, fingerprint, ua))
        conn.commit()
        log_to_db("REGISTER", username, "Success", ip)
        send_to_cpp({"event": "register", "user": username, "ip": ip})
        send_to_java({"event": "register", "user": username})
        send_to_c({"event": "register", "user": username})
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
    ip = request.remote_addr
    
    conn = get_db()
    user = conn.execute("SELECT username, role FROM users WHERE username=? AND password=?", (username, password)).fetchone()
    conn.close()
    
    if user:
        log_to_db("LOGIN", username, "Success", ip)
        send_to_cpp({"event": "login", "user": username, "ip": ip})
        send_to_java({"event": "login", "user": username})
        send_to_c({"event": "login", "user": username})
        return jsonify({'success': True, 'user': {'username': user['username'], 'role': user['role']}})
    
    log_to_db("LOGIN_FAILED", username, "Invalid password", ip)
    return jsonify({'success': False, 'error': 'Invalid credentials'}), 401

@app.route('/api/visitor/track', methods=['POST'])
def track_visitor():
    data = request.json
    conn = get_db()
    conn.execute("INSERT INTO visitors (ip, user_agent, platform, language, screen, timezone, fingerprint, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                 (data.get('ip'), data.get('userAgent'), data.get('platform'), data.get('language'), data.get('screen'), data.get('timezone'), data.get('fingerprint'), int(time.time())))
    conn.commit()
    conn.close()
    send_to_cpp({"event": "visitor", "fingerprint": data.get('fingerprint')})
    return jsonify({'success': True})

@app.route('/api/log', methods=['POST'])
def add_log():
    data = request.json
    conn = get_db()
    conn.execute("INSERT INTO logs (timestamp, action, username, detail, ip) VALUES (?, ?, ?, ?, ?)",
                 (data.get('timestamp', int(time.time())), data.get('action'), data.get('username'), data.get('detail'), request.remote_addr))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/api/products/list', methods=['GET'])
def list_products():
    conn = get_db()
    products = conn.execute("SELECT * FROM products").fetchall()
    conn.close()
    return jsonify({'products': [dict(p) for p in products]})

if __name__ == '__main__':
    init_db()
    print("[Python] Flask server starting on port 5000")
    print("[Python] Connected to C++ on port 9090")
    print("[Python] Connected to Java on port 9091")
    print("[Python] Connected to C on port 9092")
    app.run(host='0.0.0.0', port=5000, debug=False)
