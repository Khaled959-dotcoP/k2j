-- K2J ARMORY DATABASE - NO EMAIL REQUIRED
-- Run: sqlite3 k2j_armory.db < k2j_database.sql

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT DEFAULT 'user',
    created INTEGER
);

CREATE TABLE IF NOT EXISTS inventory (
    id INTEGER PRIMARY KEY,
    year INTEGER,
    price INTEGER,
    caliber TEXT,
    type TEXT,
    img TEXT,
    seller TEXT,
    location TEXT
);

CREATE TABLE IF NOT EXISTS bans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fingerprint TEXT UNIQUE,
    ip TEXT,
    reason TEXT,
    banned_at INTEGER
);

CREATE TABLE IF NOT EXISTS logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp INTEGER,
    source TEXT,
    action TEXT,
    username TEXT,
    fingerprint TEXT
);

-- Default admin user (password: admin123)
INSERT OR IGNORE INTO users (username, password, role, created) 
VALUES ('admin', '8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918', 'admin', strftime('%s','now'));

-- Sample inventory
INSERT OR IGNORE INTO inventory VALUES 
(1, 2024, 1899, '7.62x39mm', 'rifle', 'https://images.unsplash.com/photo-1595590424283-b8f17842773f?w=350&h=220&fit=crop', 'black ops tactical', 'texas'),
(2, 2023, 2495, '5.56x45mm', 'rifle', 'https://images.unsplash.com/photo-1587369994872-6c5f2bd3b094?w=350&h=220&fit=crop', 'delta defense', 'arizona'),
(3, 2025, 899, '9x19mm', 'pistol', 'https://images.unsplash.com/photo-1587293852726-70cdc0c8f7ec?w=350&h=220&fit=crop', 'sidearm solutions', 'florida');