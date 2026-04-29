#!/usr/bin/env python3
"""
K2J ARMORY - DATABASE MODULE
Independent database operations for all layers
"""

import sqlite3
import time
import hashlib
import json
import os

DB_PATH = "k2j_armory.db"

class K2JDatabase:
    """Database handler for K2J Armory"""
    
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self.conn = None
        self._init_db()
    
    def _get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    def _init_db(self):
        """Initialize all tables"""
        conn = self._get_connection()
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
        
        # Bans table
        c.execute("""
            CREATE TABLE IF NOT EXISTS bans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fingerprint TEXT UNIQUE,
                ip TEXT,
                reason TEXT,
                banned_at INTEGER,
                expires_at INTEGER
            )
        """)
        
        # Insert default admin if not exists
        admin_pass = hashlib.sha256("MES3WAHY4XG4".encode()).hexdigest()
        c.execute("SELECT COUNT(*) FROM users WHERE username = 'admin'")
        if c.fetchone()[0] == 0:
            c.execute("""
                INSERT INTO users (username, password, role, created) 
                VALUES (?, ?, 'admin', ?)
            """, ("admin", admin_pass, int(time.time())))
            print("[Database] Default admin user created")
        
        # Insert default AK-47 product if not exists
        c.execute("SELECT COUNT(*) FROM products WHERE name = 'AK-47'")
        if c.fetchone()[0] == 0:
            c.execute("""
                INSERT INTO products (id, name, category, price, caliber, lethal_range, image, specs, extra, created_by, created) 
                VALUES (1, 'AK-47', 'HEAVY', 400, '7.62x39mm', '350m', 'https://upload.wikimedia.org/wikipedia/commons/thumb/5/53/AK-47_assault_rifle.jpg/800px-AK-47_assault_rifle.jpg', 'Legendary reliability, battle-proven', '2 x FULL 30-ROUND MAGAZINES INCLUDED', 'system', ?)
            """, (int(time.time()),))
            print("[Database] Default AK-47 product created")
        
        conn.commit()
        conn.close()
        print("[Database] Initialization complete")
    
    # ==================== USER OPERATIONS ====================
    
    def create_user(self, username, password, ip="unknown", fingerprint="unknown", device="unknown"):
        """Create a new user"""
        try:
            conn = self._get_connection()
            hashed = hashlib.sha256(password.encode()).hexdigest()
            conn.execute("""
                INSERT INTO users (username, password, role, created, ip, fingerprint, device) 
                VALUES (?, ?, 'user', ?, ?, ?, ?)
            """, (username, hashed, int(time.time()), ip, fingerprint, device))
            conn.commit()
            conn.close()
            return True, "User created"
        except sqlite3.IntegrityError:
            return False, "Username already exists"
        except Exception as e:
            return False, str(e)
    
    def verify_user(self, username, password):
        """Verify user credentials"""
        try:
            conn = self._get_connection()
            hashed = hashlib.sha256(password.encode()).hexdigest()
            user = conn.execute(
                "SELECT username, role FROM users WHERE username=? AND password=?", 
                (username, hashed)
            ).fetchone()
            conn.close()
            
            if user:
                return True, user[0], user[1]
            return False, None, None
        except Exception as e:
            print(f"[Database Error] Verify user: {e}")
            return False, None, None
    
    def get_all_users(self):
        """Get all users"""
        try:
            conn = self._get_connection()
            users = conn.execute(
                "SELECT id, username, role, created, ip, fingerprint FROM users"
            ).fetchall()
            conn.close()
            return [{'id': u[0], 'username': u[1], 'role': u[2], 'created': u[3], 'ip': u[4], 'fingerprint': u[5]} for u in users]
        except Exception as e:
            print(f"[Database Error] Get users: {e}")
            return []
    
    # ==================== VISITOR OPERATIONS ====================
    
    def add_visitor(self, visitor_data):
        """Add visitor record"""
        try:
            conn = self._get_connection()
            conn.execute("""
                INSERT INTO visitors (ip, user_agent, platform, language, screen, timezone, fingerprint, timestamp, page) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                visitor_data.get('ip', 'unknown'),
                visitor_data.get('userAgent', 'unknown'),
                visitor_data.get('platform', 'unknown'),
                visitor_data.get('language', 'unknown'),
                visitor_data.get('screen', 'unknown'),
                visitor_data.get('timezone', 'unknown'),
                visitor_data.get('fingerprint', 'unknown'),
                int(time.time()),
                visitor_data.get('page', 'unknown')
            ))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"[Database Error] Add visitor: {e}")
            return False
    
    def get_recent_visitors(self, limit=100):
        """Get recent visitors"""
        try:
            conn = self._get_connection()
            visitors = conn.execute(
                "SELECT ip, user_agent, platform, timestamp, fingerprint FROM visitors ORDER BY timestamp DESC LIMIT ?",
                (limit,)
            ).fetchall()
            conn.close()
            return [{'ip': v[0], 'user_agent': v[1], 'platform': v[2], 'timestamp': v[3], 'fingerprint': v[4]} for v in visitors]
        except Exception as e:
            print(f"[Database Error] Get visitors: {e}")
            return []
    
    # ==================== PRODUCT OPERATIONS ====================
    
    def get_all_products(self):
        """Get all products"""
        try:
            conn = self._get_connection()
            products = conn.execute("SELECT * FROM products ORDER BY id").fetchall()
            conn.close()
            return [{'id': p[0], 'name': p[1], 'category': p[2], 'price': p[3], 'caliber': p[4], 'range': p[5], 'image': p[6], 'specs': p[7], 'extra': p[8]} for p in products]
        except Exception as e:
            print(f"[Database Error] Get products: {e}")
            return []
    
    def add_product(self, product_data):
        """Add new product"""
        try:
            conn = self._get_connection()
            conn.execute("""
                INSERT INTO products (name, category, price, caliber, lethal_range, image, specs, extra, created_by, created) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                product_data.get('name'),
                product_data.get('category', 'HEAVY'),
                product_data.get('price'),
                product_data.get('caliber', 'N/A'),
                product_data.get('range', 'N/A'),
                product_data.get('image', ''),
                product_data.get('specs', ''),
                product_data.get('extra', ''),
                product_data.get('created_by', 'admin'),
                int(time.time())
            ))
            conn.commit()
            product_id = conn.lastrowid
            conn.close()
            return True, product_id
        except Exception as e:
            print(f"[Database Error] Add product: {e}")
            return False, None
    
    def delete_product(self, product_id):
        """Delete product by ID"""
        try:
            conn = self._get_connection()
            conn.execute("DELETE FROM products WHERE id = ?", (product_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"[Database Error] Delete product: {e}")
            return False
    
    # ==================== ORDER OPERATIONS ====================
    
    def add_order(self, items, total, username):
        """Add new order"""
        try:
            conn = self._get_connection()
            conn.execute("""
                INSERT INTO orders (items, total, username, timestamp, status) 
                VALUES (?, ?, ?, ?, 'pending')
            """, (items, total, username, int(time.time())))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"[Database Error] Add order: {e}")
            return False
    
    def get_orders(self, limit=50):
        """Get recent orders"""
        try:
            conn = self._get_connection()
            orders = conn.execute(
                "SELECT items, total, username, timestamp, status FROM orders ORDER BY timestamp DESC LIMIT ?",
                (limit,)
            ).fetchall()
            conn.close()
            return [{'items': o[0], 'total': o[1], 'username': o[2], 'timestamp': o[3], 'status': o[4]} for o in orders]
        except Exception as e:
            print(f"[Database Error] Get orders: {e}")
            return []
    
    # ==================== LOG OPERATIONS ====================
    
    def add_log(self, action, username, detail, ip="unknown"):
        """Add log entry"""
        try:
            conn = self._get_connection()
            conn.execute("""
                INSERT INTO logs (timestamp, action, username, detail, ip) 
                VALUES (?, ?, ?, ?, ?)
            """, (int(time.time()), action, username or "system", detail, ip))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"[Database Error] Add log: {e}")
            return False
    
    def get_logs(self, limit=100):
        """Get recent logs"""
        try:
            conn = self._get_connection()
            logs = conn.execute(
                "SELECT timestamp, action, username, detail, ip FROM logs ORDER BY timestamp DESC LIMIT ?",
                (limit,)
            ).fetchall()
            conn.close()
            return [{'timestamp': l[0], 'action': l[1], 'username': l[2], 'detail': l[3], 'ip': l[4]} for l in logs]
        except Exception as e:
            print(f"[Database Error] Get logs: {e}")
            return []
    
    # ==================== STATISTICS ====================
    
    def get_stats(self):
        """Get system statistics"""
        try:
            conn = self._get_connection()
            user_count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
            visitor_count = conn.execute("SELECT COUNT(*) FROM visitors").fetchone()[0]
            product_count = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
            order_count = conn.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
            log_count = conn.execute("SELECT COUNT(*) FROM logs").fetchone()[0]
            conn.close()
            return {
                'users': user_count,
                'visitors': visitor_count,
                'products': product_count,
                'orders': order_count,
                'logs': log_count
            }
        except Exception as e:
            print(f"[Database Error] Get stats: {e}")
            return {'users': 0, 'visitors': 0, 'products': 0, 'orders': 0, 'logs': 0}

# ==================== TEST / MAIN ====================
if __name__ == "__main__":
    print("=" * 50)
    print("K2J ARMORY - DATABASE TEST")
    print("=" * 50)
    
    db = K2JDatabase()
    
    # Test statistics
    stats = db.get_stats()
    print(f"\n[Statistics]")
    print(f"  - Users: {stats['users']}")
    print(f"  - Visitors: {stats['visitors']}")
    print(f"  - Products: {stats['products']}")
    print(f"  - Orders: {stats['orders']}")
    print(f"  - Logs: {stats['logs']}")
    
    # Test products
    products = db.get_all_products()
    print(f"\n[Products] ({len(products)} items)")
    for p in products:
        print(f"  - {p['name']}: ${p['price']} ({p['category']})")
    
    # Test add visitor
    db.add_visitor({
        'ip': '127.0.0.1',
        'userAgent': 'Test Browser',
        'platform': 'Test OS',
        'language': 'en',
        'screen': '1920x1080',
        'timezone': 'UTC',
        'fingerprint': 'TEST_FP_123',
        'page': '/test'
    })
    print("\n[Test] Visitor added")
    
    print("\n[Database] All tests completed successfully!")
