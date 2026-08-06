import sqlite3
import os

DB_FILE = "inventory.sqlite"

SAMPLE_PRODUCTS = [
    ("Vanilla Bean Latte", "Beverage", 4.50, 0),
    ("Iced Caramel Macchiato", "Beverage", 5.25, 10),
    ("Matcha Oat Latte", "Beverage", 5.00, 0),
    ("Almond Croissant", "Pastry", 3.75, 15),
    ("Blueberry Scone", "Pastry", 3.50, 0),
    ("SoftStack Ceramic Mug", "Merch", 14.99, 20),
    ("Cold Brew Coffee Beans (12oz)", "Merch", 16.50, 0),
]


def reset_database():
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
        print(f"Removed old {DB_FILE}")

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Enable WAL mode for concurrency
    cursor.execute("PRAGMA journal_mode=WAL;")

    # 1. Products Table
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS products
                   (
                       ID              INTEGER PRIMARY KEY AUTOINCREMENT,
                       Name            TEXT NOT NULL,
                       Type            TEXT NOT NULL,
                       Price           REAL NOT NULL,
                       DiscountPercent INTEGER DEFAULT 0
                   );
                   """)

    # 2. Users Table
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS Users(
                        ID INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE NOT NULL,
                        password TEXT NOT NULL
                   );
            """)

    # 3. Tokens
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Tokens(
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            token   TEXT    NOT NULL
        );
    """)

    # Seed data
    cursor.executemany("""
        INSERT INTO products (Name, Type, Price, DiscountPercent)
        VALUES (?, ?, ?, ?);
    """, SAMPLE_PRODUCTS)

    cursor.execute("""
        INSERT OR IGNORE INTO Users (username, password)
        VALUES (?, ?);
    """, ("nicole", "softstack123"))

    conn.commit()
    conn.close()
    print("Database initialized successfully! ☕")

if __name__ == "__main__":
    reset_database()

""" Thanks for using SoftStack Studios! """
