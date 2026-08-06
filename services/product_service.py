import sqlite3
import uuid
import bcrypt
from typing import List, Optional
from modules.product_models import ProductRequest

DB_FILE = 'inventory.sqlite'


def get_db_connection():
    """Helper to create a standard sync sqlite3 connection."""
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row  # Access columns by key (e.g., row["Price"])
    return conn


def calculate_discount(price: float, discount_percent: float) -> float:
    if discount_percent <= 0:
        return round(price, 2)
    return round(price - (price * (discount_percent / 100.0)), 2)


def format_product_data(row: sqlite3.Row) -> dict:
    product = dict(row)
    product["FinalPrice"] = calculate_discount(product.get("Price", 0.0), product.get("DiscountPercent", 0.0))
    return product


# ==============================
# READ METHODS
# ==============================

def get_products_paginated(limit: int = 20, offset: int = 0):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'SELECT * FROM products ORDER BY ID LIMIT ? OFFSET ?', (limit, offset)
        )
        rows = cursor.fetchall()
        return [format_product_data(row) for row in rows]


def get_product_by_id(product_id: int):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM products WHERE ID = ?', (product_id,))
        row = cursor.fetchone()
        return format_product_data(row) if row else None


def get_products_by_price_range(min_p: float, max_p: float):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'SELECT * FROM products WHERE Price BETWEEN ? AND ?', (min_p, max_p)
        )
        rows = cursor.fetchall()
        return [format_product_data(row) for row in rows]


def search_products(price: float, product_type: Optional[str] = None):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        if product_type:
            query = 'SELECT * FROM products WHERE Price = ? AND Type = ?'
            params = (price, product_type)
        else:
            query = 'SELECT * FROM products WHERE Price = ?'
            params = (price,)
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [format_product_data(row) for row in rows]


# ==============================
# WRITE / MODIFY METHODS
# ==============================

def add_new_product(product: ProductRequest):
    with get_db_connection() as conn:
        conn.execute(
            "INSERT INTO products (Name, Price, Type, DiscountPercent) VALUES (?, ?, ?, ?)",
            (product.Name, product.Price, product.Type, product.DiscountPercent)
        )
        conn.commit()


def update_existing_product(product: ProductRequest):
    with get_db_connection() as conn:
        conn.execute(
            "UPDATE products SET Name = ?, Price = ?, Type = ?, DiscountPercent = ? WHERE ID = ?",
            (product.Name, product.Price, product.Type, product.DiscountPercent, product.ID)
        )
        conn.commit()


def bulk_delete_products(product_ids: List[int]) -> int:
    if not product_ids:
        return 0
    with get_db_connection() as conn:
        placeholders = ', '.join('?' * len(product_ids))
        query = f"DELETE FROM products WHERE ID IN ({placeholders})"
        cursor = conn.execute(query, product_ids)
        conn.commit()
        return cursor.rowcount


def bulk_save_products(products: List[ProductRequest]):
    with get_db_connection() as conn:
        for item in products:
            if item.ID:
                conn.execute(
                    "UPDATE products SET Name = ?, Price = ?, Type = ?, DiscountPercent = ? WHERE ID = ?",
                    (item.Name, item.Price, item.Type, item.DiscountPercent, item.ID)
                )
            else:
                conn.execute(
                    "INSERT INTO products (Name, Price, Type, DiscountPercent) VALUES (?, ?, ?, ?)",
                    (item.Name, item.Price, item.Type, item.DiscountPercent)
                )
        conn.commit()


# ==============================
# AUTHENTICATION & TOKENS
# ==============================

def verify_token(token: str) -> bool:
    if not token:
        return False
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Tokens WHERE token = ?', (token,))
        row = cursor.fetchone()
        return row is not None


def authenticate_user(username: str, password: str) -> Optional[str]:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT ID, username, password FROM Users WHERE username = ?", (username,))
        row = cursor.fetchone()

        if not row:
            return None

        # Password check
        stored_password = row["password"]
        if stored_password.startswith("$2b$") or stored_password.startswith("$2a$"):
            is_valid = bcrypt.checkpw(
                password.encode("utf-8"), stored_password.encode("utf-8")
            )
        else:
            is_valid = (password == stored_password)

        if not is_valid:
            return None

        # Check for existing token (Indented 8 spaces)
        cursor.execute(
            "SELECT token FROM Tokens WHERE user_id = ?", (row["ID"],)
        )
        token_row = cursor.fetchone()

        if token_row:
            return token_row["token"]

        # Create one and save it if missing
        new_token = str(uuid.uuid4())
        cursor.execute(
            "INSERT INTO Tokens (user_id, token) VALUES (?, ?)",
            (row["ID"], new_token),
        )
        conn.commit()

        return new_token


""" Thanks for using SoftStack Studios! """
