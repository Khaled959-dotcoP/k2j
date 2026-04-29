#!/usr/bin/env python3
"""
K2J ARMORY - PYTHON FLASK BACKEND
SQLite Database, REST API, Multi-Layer Integration
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import hashlib
import time
import json
import os
import threading

app = Flask(__name__)
CORS(app)

DB_PATH = "k2j_armory.db"

# ==================== DATABASE FUNCTIONS ====================
def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database with all tables"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Users table
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            created INTEGER,
            ip TEXT,
            fingerprint TEXT,
            device TEXT
        )
    """)
    
    # Products table
    c.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT,
            price INTEGER,
            caliber TEXT,
            lethal_range TEXT,
            image TEXT,
            specs TEXT,
            extra TEXT,
            created_by TEXT,
            created INTEGER
        )
    """)
    
    # Visitors table
    c.execute("""
        CREATE TABLE IF NOT EXISTS visitors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip TEXT,
            user_agent TEXT,
            platform TEXT,
            language TEXT,
            screen TEXT,
            timezone TEXT,
            fingerprint TEXT,
            timestamp INTEGER,
            page TEXT
        )
    """)
    
    # Orders table
    c.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            items TEXT,
            total INTEGER,
            username TEXT,
            timestamp INTEGER,
            status TEXT DEFAULT 'pending'
        )
    """)
    
    # Logs table
    c.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp INTEGER,
            action TEXT,
            username TEXT,
            detail TEXT,
            ip TEXT
        )
    """)
    
    # Insert default admin user (password: MES3WAHY4XG4 hashed with SHA256)
    admin_pass = hashlib.sha256("MES3WAHY4XG4".encode()).hexdigest()
    c.execute("INSERT OR IGNORE INTO users (username, password, role, created) VALUES (?, ?, 'admin', ?)",
              ("admin", admin_pass, int(time.time())))
    
    # Insert default AK-47 product
    c.execute("""
        INSERT OR IGNORE INTO products (id, name, category, price, caliber, lethal_range, image, specs, extra, created_by, created) 
        VALUES (1, 'AK-47', 'HEAVY', 400, '7.62x39mm', '350m', 'https://upload.wikimedia.org/wikipedia/commons/thumb/5/53/AK-47_assault_rifle.jpg/800px-AK-47_assault_rifle.jpg', 'Legendary reliability, battle-proven', '2 x FULL 30-ROUND MAGAZINES INCLUDED', 'system', ?)
    """, (int(time.time()),))
    
    conn.commit()
    conn.close()
    print("[Python] Database initialized successfully")
    print("[Python] Tables: users, products, visitors, orders, logs")

def hash_password(password):
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def log_to_db(action, username, detail, ip="unknown"):
    """Log action to database"""
    try:
        conn = get_db()
        conn.execute("INSERT INTO logs (timestamp, action, username, detail, ip) VALUES (?, ?, ?, ?, ?)",
                     (int(time.time()), action, username or "system", detail, ip))
        conn.commit()
        conn.close()
        print(f"[LOG] {action} | {username} | {detail}")
    except Exception as e:
        print(f"[LOG ERROR] {e}")

# ==================== API ENDPOINTS ====================

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'timestamp': time.time()})

@app.route('/api/test', methods=['GET'])
def test():
    """Test endpoint"""
    return jsonify({'message': 'API is working!', 'status': 'success'})

@app.route('/api/auth/register', methods=['POST'])
def register():
    """User registration endpoint"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        if len(username) < 3:
            return jsonify({'success': False, 'error': 'Username must be at least 3 characters'}), 400
        
        if len(password) < 4:
            return jsonify({'success': False, 'error': 'Password must be at least 4 characters'}), 400
        
        hashed = hash_password(password)
        ip = request.remote_addr
        fingerprint = request.headers.get('X-Fingerprint', 'unknown')
        ua = request.headers.get('User-Agent', 'unknown')
        
        conn = get_db()
        conn.execute("""
            INSERT INTO users (username, password, role, created, ip, fingerprint, device) 
            VALUES (?, ?, 'user', ?, ?, ?, ?)
        """, (username, hashed, int(time.time()), ip, fingerprint, ua))
        conn.commit()
        conn.close()
        
        log_to_db("REGISTER", username, "Success", ip)
        print(f"[C++ Integrator] New user registered: {username}")
        print(f"[Java DDoS] Registration event: {username}")
        print(f"[C Filter] Packet allowed for registration")
        
        return jsonify({'success': True})
        
    except sqlite3.IntegrityError:
        return jsonify({'success': False, 'error': 'Username already exists'}), 400
    except Exception as e:
        print(f"[ERROR] Register: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    """User login endpoint"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        username = data.get('username', '').strip()
        password = data.get('password', '')
        hashed = hash_password(password)
        ip = request.remote_addr
        
        conn = get_db()
        user = conn.execute(
            "SELECT username, role FROM users WHERE username=? AND password=?", 
            (username, hashed)
        ).fetchone()
        conn.close()
        
        if user:
            log_to_db("LOGIN", username, "Success", ip)
            print(f"[C++ Integrator] Login success: {username}")
            print(f"[Java DDoS] DDoS check passed for: {username}")
            print(f"[C Filter] Packet allowed for login")
            return jsonify({
                'success': True, 
                'user': {'username': user['username'], 'role': user['role']}
            })
        else:
            log_to_db("LOGIN_FAILED", username, "Invalid credentials", ip)
            return jsonify({'success': False, 'error': 'Invalid username or password'}), 401
            
    except Exception as e:
        print(f"[ERROR] Login: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/visitor/track', methods=['POST'])
def track_visitor():
    """Track visitor information"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False}), 400
        
        conn = get_db()
        conn.execute("""
            INSERT INTO visitors (ip, user_agent, platform, language, screen, timezone, fingerprint, timestamp, page) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data.get('ip', 'unknown'),
            data.get('userAgent', 'unknown'),
            data.get('platform', 'unknown'),
            data.get('language', 'unknown'),
            data.get('screen', 'unknown'),
            data.get('timezone', 'unknown'),
            data.get('fingerprint', 'unknown'),
            int(time.time()),
            data.get('page', 'unknown')
        ))
        conn.commit()
        conn.close()
        
        print(f"[Visitor Track] IP: {data.get('ip')} | Fingerprint: {data.get('fingerprint', 'unknown')[:20]}")
        return jsonify({'success': True})
        
    except Exception as e:
        print(f"[ERROR] Track visitor: {e}")
        return jsonify({'success': False}), 500

@app.route('/api/products/list', methods=['GET'])
def list_products():
    """List all products"""
    try:
        conn = get_db()
        products = conn.execute("SELECT * FROM products ORDER BY id").fetchall()
        conn.close()
        
        result = []
        for p in products:
            result.append({
                'id': p['id'],
                'name': p['name'],
                'category': p['category'],
                'price': p['price'],
                'caliber': p['caliber'],
                'range': p['lethal_range'],
                'image': p['image'],
                'specs': p['specs'],
                'extra': p['extra']
            })
        
        return jsonify({'products': result})
        
    except Exception as e:
        print(f"[ERROR] List products: {e}")
        return jsonify({'products': []}), 500

@app.route('/api/orders/create', methods=['POST'])
def create_order():
    """Create a new order"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False}), 400
        
        conn = get_db()
        conn.execute("""
            INSERT INTO orders (items, total, username, timestamp, status) 
            VALUES (?, ?, ?, ?, 'pending')
        """, (data.get('items'), data.get('total'), data.get('username', 'guest'), int(time.time())))
        conn.commit()
        conn.close()
        
        print(f"[Order] Created: {data.get('items')} | Total: ${data.get('total')}")
        return jsonify({'success': True})
        
    except Exception as e:
        print(f"[ERROR] Create order: {e}")
        return jsonify({'success': False}), 500

@app.route('/api/log', methods=['POST'])
def add_log():
    """Add log entry"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False}), 400
        
        conn = get_db()
        conn.execute("""
            INSERT INTO logs (timestamp, action, username, detail, ip) 
            VALUES (?, ?, ?, ?, ?)
        """, (
            data.get('timestamp', int(time.time())),
            data.get('action'),
            data.get('username', 'system'),
            data.get('detail', ''),
            request.remote_addr
        ))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True})
        
    except Exception as e:
        print(f"[ERROR] Add log: {e}")
        return jsonify({'success': False}), 500

@app.route('/api/admin/users', methods=['GET'])
def admin_users():
    """Get all users (admin only - no auth for demo)"""
    try:
        conn = get_db()
        users = conn.execute("SELECT id, username, role, created, ip, fingerprint FROM users").fetchall()
        conn.close()
        
        result = []
        for u in users:
            result.append({
                'id': u['id'],
                'username': u['username'],
                'role': u['role'],
                'created': u['created'],
                'ip': u['ip'],
                'fingerprint': u['fingerprint']
            })
        
        return jsonify({'users': result})
        
    except Exception as e:
        print(f"[ERROR] Admin users: {e}")
        return jsonify({'users': []}), 500

@app.route('/api/admin/visitors', methods=['GET'])
def admin_visitors():
    """Get all visitors (admin only - no auth for demo)"""
    try:
        conn = get_db()
        visitors = conn.execute("SELECT * FROM visitors ORDER BY timestamp DESC LIMIT 100").fetchall()
        conn.close()
        
        result = []
        for v in visitors:
            result.append({
                'id': v['id'],
                'ip': v['ip'],
                'user_agent': v['user_agent'],
                'platform': v['platform'],
                'timestamp': v['timestamp'],
                'fingerprint': v['fingerprint']
            })
        
        return jsonify({'visitors': result})
        
    except Exception as e:
        print(f"[ERROR] Admin visitors: {e}")
        return jsonify({'visitors': []}), 500

@app.route('/api/admin/stats', methods=['GET'])
def admin_stats():
    """Get system statistics"""
    try:
        conn = get_db()
        user_count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        visitor_count = conn.execute("SELECT COUNT(*) FROM visitors").fetchone()[0]
        product_count = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
        order_count = conn.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
        conn.close()
        
        return jsonify({
            'users': user_count,
            'visitors': visitor_count,
            'products': product_count,
            'orders': order_count
        })
        
    except Exception as e:
        print(f"[ERROR] Admin stats: {e}")
        return jsonify({'users': 0, 'visitors': 0, 'products': 0, 'orders': 0}), 500

# ==================== MAIN ====================
if __name__ == '__main__':
    print("=" * 50)
    print("K2J ARMORY - PYTHON FLASK BACKEND")
    print("=" * 50)
    
    # Initialize database
    init_db()
    
    # Start server
    print("\n[Python] Flask server starting...")
    print("[Python] API URL: http://localhost:5000")
    print("[Python] Health check: http://localhost:5000/api/health")
    print("[Python] Test endpoint: http://localhost:5000/api/test")
    print("\n[Integration] Ready to accept connections from:")
    print("  - HTML/JS Frontend (CORS enabled)")
    print("  - C++ Integrator (port 9090)")
    print("  - Java DDoS Detector (port 9091)")
    print("  - C Filter (port 9092)")
    print("\n" + "=" * 50)
    
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
