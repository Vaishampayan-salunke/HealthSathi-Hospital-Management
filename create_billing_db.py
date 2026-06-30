import sqlite3
from datetime import datetime

# Create or connect to the billing database
conn = sqlite3.connect('billing.db')
cursor = conn.cursor()

# Create billing table
cursor.execute('''
CREATE TABLE IF NOT EXISTS billing (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id TEXT NOT NULL UNIQUE,
    patient_name TEXT NOT NULL,
    gender TEXT,
    age INTEGER,
    phone TEXT,
    email TEXT,
    appointment_date TEXT,
    department TEXT,
    doctor_name TEXT,
    pharmacy_items TEXT,
    lab_tests TEXT,
    pharmacy_total REAL DEFAULT 0,
    lab_total REAL DEFAULT 0,
    subtotal REAL DEFAULT 0,
    discount REAL DEFAULT 0,
    gst REAL DEFAULT 0,
    grand_total REAL DEFAULT 0,
    status TEXT DEFAULT 'Pending Payment',
    payment_method TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

# Create payment history table
cursor.execute('''
CREATE TABLE IF NOT EXISTS payment_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    billing_id INTEGER NOT NULL,
    amount_paid REAL NOT NULL,
    payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    payment_method TEXT,
    transaction_id TEXT UNIQUE,
    status TEXT DEFAULT 'Success',
    FOREIGN KEY(billing_id) REFERENCES billing(id)
)
''')

# Create pharmacy items table
cursor.execute('''
CREATE TABLE IF NOT EXISTS pharmacy_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    billing_id INTEGER NOT NULL,
    item_name TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price REAL NOT NULL,
    total_price REAL NOT NULL,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(billing_id) REFERENCES billing(id)
)
''')

# Create lab tests table
cursor.execute('''
CREATE TABLE IF NOT EXISTS lab_tests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    billing_id INTEGER NOT NULL,
    test_name TEXT NOT NULL,
    test_price REAL NOT NULL,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(billing_id) REFERENCES billing(id)
)
''')

conn.commit()
conn.close()

print("✅ Billing database created successfully!")
print("📁 File: billing.db")
print("📊 Tables created:")
print("   1. billing - Main billing records")
print("   2. payment_history - Payment transaction logs")
print("   3. pharmacy_items - Individual pharmacy items")
print("   4. lab_tests - Individual lab tests")
