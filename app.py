#!/usr/bin/env python3
"""
K2J ARMORY - FULL BACKEND (TEK DOSYA)
SQLite + Flask API + Visitor Tracking + Order System
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import hashlib
import time
import os

app = Flask(__name__)
CORS(app)

DB_PATH = "k2j_armory.db"

# ============================================================
# DATABASE INITIALIZATION
# ============================================================

def init_db():
    """Initialize database with all tables"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            created INTEGER,
            ip TEXT,
            fingerprint TEXT
        )
    ''')
    
    # Products table
    c.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT,
            price INTEGER,
            caliber TEXT,
            lethal_range TEXT,
            image TEXT,
            specs TEXT,
            extra TEXT
        )
    ''')
    
    # Visitors table
    c.execute('''
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
    ''')
    
    # Orders table
    c.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            items TEXT,
            total INTEGER,
            username TEXT,
            timestamp INTEGER,
            status TEXT DEFAULT 'pending'
        )
    ''')
    
    # Logs table
    c.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp INTEGER,
            action TEXT,
            username TEXT,
            detail TEXT,
            ip TEXT
        )
    ''')
    
    # Admin user (password: MES3WAHY4XG4)
    admin_pass = hashlib.sha256("MES3WAHY4XG4".encode()).hexdigest()
    c.execute("INSERT OR IGNORE INTO users (username, password, role, created) VALUES ('admin', ?, 'admin', ?)",
              (admin_pass, int(time.time())))
    
    # Default product: AK-47
    c.execute("INSERT OR IGNORE INTO products (id, name, category, price, caliber, lethal_range, image, specs, extra) VALUES (1, 'AK-47', 'HEAVY', 400, '7.62x39mm', '350m', 'https://upload.wikimedia.org/wikipedia/commons/thumb/5/53/AK-47_assault_rifle.jpg/800px-AK-47_assault_rifle.jpg', 'Legendary reliability, battle-proven', '2 x FULL 30-ROUND MAGAZINES INCLUDED')")
    
    conn.commit()
    conn.close()
    print("[DB] Database initialized - k2j_armory.db")
    print("[DB] Tables: users, products, visitors, orders, logs")

def get_db():
    return sqlite3.connect(DB_PATH)

def hash_pass(pwd):
    return hashlib.sha256(pwd.encode()).hexdigest()

# ============================================================
# API ENDPOINTS
# ============================================================

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'timestamp': time.time()})

@app.route('/api/test', methods=['GET'])
def test():
    return jsonify({'message': 'API is working!', 'success': True})

@app.route('/api/auth/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        if len(username) < 3:
            return jsonify({'success': False, 'error': 'Username min 3 chars'}), 400
        if len(password) < 4:
            return jsonify({'success': False, 'error': 'Password min 4 chars'}), 400
        
        conn = get_db()
        conn.execute("INSERT INTO users (username, password, role, created, ip) VALUES (?, ?, 'user', ?, ?)",
                     (username, hash_pass(password), int(time.time()), request.remote_addr))
        conn.commit()
        conn.close()
        
        print(f"[AUTH] New user registered: {username}")
        return jsonify({'success': True})
    except sqlite3.IntegrityError:
        return jsonify({'success': False, 'error': 'Username exists'}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        conn = get_db()
        user = conn.execute("SELECT username, role FROM users WHERE username=? AND password=?",
                            (username, hash_pass(password))).fetchone()
        conn.close()
        
        if user:
            print(f"[AUTH] User logged in: {username}")
            return jsonify({'success': True, 'user': {'username': user[0], 'role': user[1]}})
        else:
            return jsonify({'success': False, 'error': 'Invalid credentials'}), 401
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/visitor/track', methods=['POST'])
def track_visitor():
    try:
        data = request.get_json()
        conn = get_db()
        conn.execute("""INSERT INTO visitors (ip, user_agent, platform, language, screen, timezone, fingerprint, timestamp, page) 
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                     (data.get('ip'), data.get('userAgent'), data.get('platform'), data.get('language'),
                      data.get('screen'), data.get('timezone'), data.get('fingerprint'), int(time.time()), data.get('page')))
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False}), 500

@app.route('/api/products/list', methods=['GET'])
def list_products():
    try:
        conn = get_db()
        products = conn.execute("SELECT * FROM products ORDER BY id").fetchall()
        conn.close()
        
        result = []
        for p in products:
            result.append({
                'id': p[0], 'name': p[1], 'category': p[2], 'price': p[3],
                'caliber': p[4], 'range': p[5], 'image': p[6], 'specs': p[7], 'extra': p[8]
            })
        return jsonify({'products': result})
    except Exception as e:
        return jsonify({'products': []}), 500

@app.route('/api/orders/create', methods=['POST'])
def create_order():
    try:
        data = request.get_json()
        conn = get_db()
        conn.execute("INSERT INTO orders (items, total, username, timestamp) VALUES (?, ?, ?, ?)",
                     (data.get('items'), data.get('total'), data.get('username', 'guest'), int(time.time())))
        conn.commit()
        conn.close()
        print(f"[ORDER] Created: {data.get('items')} - Total: ${data.get('total')}")
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False}), 500

@app.route('/api/admin/stats', methods=['GET'])
def admin_stats():
    try:
        conn = get_db()
        user_count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        visitor_count = conn.execute("SELECT COUNT(*) FROM visitors").fetchone()[0]
        product_count = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
        order_count = conn.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
        conn.close()
        return jsonify({'users': user_count, 'visitors': visitor_count, 'products': product_count, 'orders': order_count})
    except:
        return jsonify({'users': 0, 'visitors': 0, 'products': 0, 'orders': 0})

@app.route('/api/admin/users', methods=['GET'])
def admin_users():
    try:
        conn = get_db()
        users = conn.execute("SELECT id, username, role, created FROM users").fetchall()
        conn.close()
        return jsonify({'users': [{'id': u[0], 'username': u[1], 'role': u[2], 'created': u[3]} for u in users]})
    except:
        return jsonify({'users': []})

@app.route('/api/admin/visitors', methods=['GET'])
def admin_visitors():
    try:
        conn = get_db()
        visitors = conn.execute("SELECT ip, user_agent, timestamp, fingerprint FROM visitors ORDER BY timestamp DESC LIMIT 50").fetchall()
        conn.close()
        return jsonify({'visitors': [{'ip': v[0], 'user_agent': v[1], 'timestamp': v[2], 'fingerprint': v[3]} for v in visitors]})
    except:
        return jsonify({'visitors': []})

@app.route('/api/admin/add_product', methods=['POST'])
def add_product():
    try:
        data = request.get_json()
        conn = get_db()
        conn.execute("""INSERT INTO products (name, category, price, caliber, lethal_range, image, specs, extra) 
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                     (data.get('name'), data.get('category'), data.get('price'), data.get('caliber', 'N/A'),
                      data.get('range', 'N/A'), data.get('image', ''), data.get('specs', ''), data.get('extra', '')))
        conn.commit()
        conn.close()
        print(f"[ADMIN] Product added: {data.get('name')}")
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/delete_product/<int:pid>', methods=['DELETE'])
def delete_product(pid):
    try:
        conn = get_db()
        conn.execute("DELETE FROM products WHERE id = ?", (pid,))
        conn.commit()
        conn.close()
        print(f"[ADMIN] Product deleted: ID {pid}")
        return jsonify({'success': True})
    except:
        return jsonify({'success': False}), 500

# ============================================================
# MAIN
# ============================================================
if __name__ == '__main__':
    print("=" * 50)
    print("K2J ARMORY - BACKEND SERVER")
    print("=" * 50)
    
    init_db()
    
    print("\n[API] Available endpoints:")
    print("  GET  /api/health")
    print("  GET  /api/test")
    print("  POST /api/auth/register")
    print("  POST /api/auth/login")
    print("  POST /api/visitor/track")
    print("  GET  /api/products/list")
    print("  POST /api/orders/create")
    print("  GET  /api/admin/stats")
    print("  GET  /api/admin/users")
    print("  GET  /api/admin/visitors")
    print("  POST /api/admin/add_product")
    print("  DELETE /api/admin/delete_product/<id>")
    
    print("\n[Server] Starting on http://localhost:5000")
    print("=" * 50)
    
    app.run(host='0.0.0.0', port=5000, debug=False)
