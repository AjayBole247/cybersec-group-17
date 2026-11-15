"""
Database initialization and management module for:
IIIT Allahabad | Department of Information Technology
Cyber Security (IT-30001) | Assignment: Web Server Security
"""

import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'vulnerable_lab.db')

def get_db_connection():
    """Returns a SQLite database connection with row access by column name."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db(reset=False):
    """Initializes tables and seeds initial data."""
    if reset and os.path.exists(DB_PATH):
        try:
            os.remove(DB_PATH)
        except PermissionError:
            pass

    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Users table (Targets: SQLi Auth Bypass, UNION-based extraction, CSRF authentication)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL,
        email TEXT NOT NULL,
        secret_flag TEXT NOT NULL,
        balance REAL NOT NULL DEFAULT 10000.00
    )
    ''')

    # 2. Products table (Target: SQLi UNION-based extraction)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        price REAL NOT NULL,
        description TEXT NOT NULL
    )
    ''')

    # 3. Comments table (Target: Stored XSS)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS comments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        author TEXT NOT NULL,
        message TEXT NOT NULL,
        created_at TEXT NOT NULL
    )
    ''')

    # 4. Bank Transactions table (Target: CSRF)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender TEXT NOT NULL,
        recipient TEXT NOT NULL,
        amount REAL NOT NULL,
        status TEXT NOT NULL,
        timestamp TEXT NOT NULL
    )
    ''')

    # Seed Users if table is empty
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        seed_users = [
            ('admin', '123456', 'Administrator', 'admin@iiita.ac.in', 'FLAG{iiita_sql1_auth_byp4ss_m4st3r}', 500000.00),
            ('ajay_bole', 'Ajay@IIT2024088', 'Security Lead', 'iit2024088@iiita.ac.in', 'FLAG{ajay_auth_bypass_flag}', 75000.00),
            ('prince_kumar', 'Prince@IIT2024085', 'System Auditor', 'iit2024085@iiita.ac.in', 'FLAG{prince_cmd_inj_flag}', 80000.00),
            ('chandan_das', 'Chandan@IIT2024070', 'Web Penetester', 'iit2024070@iiita.ac.in', 'FLAG{chandan_stored_xss_flag}', 65000.00),
            ('raghvendra', 'Raghvendra@IIT2024062', 'Network Analyst', 'iit2024062@iiita.ac.in', 'FLAG{raghvendra_csrf_flag}', 70000.00),
            ('sayan_biswas', 'Sayan@IIT2024090', 'Database Admin', 'iit2024090@iiita.ac.in', 'FLAG{sayan_union_sqli_flag}', 90000.00),
            ('victim_user', 'VictimPass1234', 'Customer', 'victim@securebank.in', 'FLAG{victim_funds_depleted}', 25000.00),
            ('attacker_account', 'AttackerP@wned', 'Rogue', 'attacker@malicious.org', 'FLAG{stolen_funds_pool}', 500.00)
        ]
        cursor.executemany(
            "INSERT INTO users (username, password, role, email, secret_flag, balance) VALUES (?, ?, ?, ?, ?, ?)",
            seed_users
        )

    # Seed Products if table is empty
    cursor.execute("SELECT COUNT(*) FROM products")
    if cursor.fetchone()[0] == 0:
        seed_products = [
            ('Hardware Security Module (HSM)', 'Hardware', 1499.99, 'FIPS 140-2 Level 3 certified cryptographic processor.'),
            ('Wi-Fi Pineapple Mark VII', 'Hardware', 199.99, 'Rogue access point auditing and wireless network reconnaissance kit.'),
            ('Proxmark3 RDV4', 'Hardware', 349.50, 'RFID and NFC interrogation and cloning instrument.'),
            ('Rubber Ducky USB Keystroke Injector', 'Hardware', 79.99, 'Rapid automated HID keyboard injection payload platform.'),
            ('Burp Suite Enterprise License', 'Software', 3999.00, 'Automated enterprise dynamic web vulnerability scanner.'),
            ('Network Traffic Analyzer Pro', 'Software', 499.00, 'Deep packet inspection and zero-day signature detector.'),
            ('Applied Cryptography Handbook', 'Books', 64.95, 'Protocols, algorithms, and source code in C by Bruce Schneier.'),
            ('The Web Application Hacker Handbook', 'Books', 55.00, 'Discovering and exploiting security flaws in modern web systems.'),
            ('Silence on the Wire', 'Books', 42.00, 'A field guide to passive reconnaissance and traffic analysis.')
        ]
        cursor.executemany(
            "INSERT INTO products (name, category, price, description) VALUES (?, ?, ?, ?)",
            seed_products
        )

    # Seed Comments if table is empty
    cursor.execute("SELECT COUNT(*) FROM comments")
    if cursor.fetchone()[0] == 0:
        seed_comments = [
            ('Soumyadev Maity', 'Welcome to IT-30001 Cyber Security Lab. Please follow responsible disclosure and safe testing rules.', '2026-11-10 10:15:00'),
            ('Ajay Bole', 'Authentication bypass module ready for testing. Try inputting SQL metacharacters.', '2026-11-11 14:22:10'),
            ('Chandan Kumar Das', 'Stored XSS guestbook is live. Notice how unescaped HTML can trigger client-side JavaScript.', '2026-11-12 09:45:30')
        ]
        cursor.executemany(
            "INSERT INTO comments (author, message, created_at) VALUES (?, ?, ?)",
            seed_comments
        )

    # Seed Transactions if table is empty
    cursor.execute("SELECT COUNT(*) FROM transactions")
    if cursor.fetchone()[0] == 0:
        seed_tx = [
            ('victim_user', 'ajay_bole', 1500.00, 'Completed', '2026-11-12 11:30:00'),
            ('admin', 'raghvendra', 5000.00, 'Completed', '2026-11-12 12:45:00')
        ]
        cursor.executemany(
            "INSERT INTO transactions (sender, recipient, amount, status, timestamp) VALUES (?, ?, ?, ?, ?)",
            seed_tx
        )

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db(reset=True)
    print("Database initialized successfully at:", DB_PATH)
