-- K2J ARMORY - DATABASE SCHEMA

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT DEFAULT 'user',
    created INTEGER,
    ip TEXT,
    fingerprint TEXT,
    device TEXT
);

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
    created_by TEXT
);

CREATE TABLE IF NOT EXISTS visitors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ip TEXT,
    user_agent TEXT,
    platform TEXT,
    language TEXT,
    screen TEXT,
    timezone TEXT,
    fingerprint TEXT,
    timestamp INTEGER
);

CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    items TEXT,
    total INTEGER,
    username TEXT,
    timestamp INTEGER
);

CREATE TABLE IF NOT EXISTS logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp INTEGER,
    action TEXT,
    username TEXT,
    detail TEXT,
    ip TEXT
);

-- Default admin user (password: MES3WAHY4XG4)
INSERT OR IGNORE INTO users (username, password, role, created) 
VALUES ('admin', '8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918', 'admin', strftime('%s','now'));

-- Default AK-47 product
INSERT OR IGNORE INTO products (id, name, category, price, caliber, lethal_range, image, specs, extra, created_by) 
VALUES (1, 'AK-47', 'HEAVY', 400, '7.62x39mm', '350m', 'https://upload.wikimedia.org/wikipedia/commons/thumb/5/53/AK-47_assault_rifle.jpg/800px-AK-47_assault_rifle.jpg', 'Legendary reliability, battle-proven', '2 x FULL 30-ROUND MAGAZINES INCLUDED', 'system');
