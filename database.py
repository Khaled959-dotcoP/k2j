#!/usr/bin/env python3
import sqlite3
import time
import json
import os

DB_PATH = "k2j_armory.db"

class K2JDatabase:
    def __init__(self):
        self.conn = None
        self.connect()
    
    def connect(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.conn.row_factory = sqlite3.Row
    
    def close(self):
        if self.conn:
            self.conn.close()
    
    def get_user(self, username):
        cursor = self.conn.execute("SELECT * FROM users WHERE username = ?", (username,))
        return cursor.fetchone()
    
    def get_all_users(self):
        cursor = self.conn.execute("SELECT id, username, role, created, ip, fingerprint, device FROM users")
        return cursor.fetchall()
    
    def get_all_visitors(self, limit=100):
        cursor = self.conn.execute("SELECT * FROM visitors ORDER BY timestamp DESC LIMIT ?", (limit,))
        return cursor.fetchall()
    
    def get_all_products(self):
        cursor = self.conn.execute("SELECT * FROM products")
        return cursor.fetchall()
    
    def add_product(self, name, category, price, caliber, lethal_range, image, specs, extra, created_by):
        cursor = self.conn.execute("""INSERT INTO products (name, category, price, caliber, lethal_range, image, specs, extra, created_by)
                                      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                                   (name, category, price, caliber, lethal_range, image, specs, extra, created_by))
        self.conn.commit()
        return cursor.lastrowid
    
    def delete_product(self, product_id):
        self.conn.execute("DELETE FROM products WHERE id = ?", (product_id,))
        self.conn.commit()
    
    def add_log(self, action, username, detail, ip):
        self.conn.execute("INSERT INTO logs (timestamp, action, username, detail, ip) VALUES (?, ?, ?, ?, ?)",
                         (int(time.time()), action, username, detail, ip))
        self.conn.commit()
    
    def get_stats(self):
        stats = {}
        cursor = self.conn.execute("SELECT COUNT(*) FROM users")
        stats['users'] = cursor.fetchone()[0]
        cursor = self.conn.execute("SELECT COUNT(*) FROM visitors")
        stats['visitors'] = cursor.fetchone()[0]
        cursor = self.conn.execute("SELECT COUNT(*) FROM orders")
        stats['orders'] = cursor.fetchone()[0]
        cursor = self.conn.execute("SELECT COUNT(*) FROM products")
        stats['products'] = cursor.fetchone()[0]
        return stats

if __name__ == "__main__":
    db = K2JDatabase()
    print("[SQLite] Database connected")
    print(f"[SQLite] Stats: {db.get_stats()}")
    db.close()
