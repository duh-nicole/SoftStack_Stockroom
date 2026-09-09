import os
from typing import List, Optional
import psycopg2
from psycopg2.extras import RealDictCursor
from modules.product_models import ProductRequest

DATABASE_URL = os.getenv("DATABASE_URL")

def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    conn.autocommit = False
    return conn

def calculate_discount(price: float, discount_percent: float) -> float:
    if not discount_percent or discount_percent <= 0:
        return round(float(price), 2)
    return round(float(price) - (float(price) * (float(discount_percent) / 100.0)), 2)

def format_product_data(row: dict) -> dict:
    if not row:
        return None
    product = dict(row)
    # Map lowercase DB columns to the response schema expected by FastAPI
    product["FinalPrice"] = calculate_discount(
        product.get("price", 0.0), 
        product.get("discount_percent", 0.0)
    )
    return product


# ==============================
# READ METHODS
# ==============================

def get_products_paginated(limit: int = 20, offset: int = 0):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            'SELECT * FROM products ORDER BY id LIMIT %s OFFSET %s;', 
            (limit, offset)
        )
        rows = cursor.fetchall()
        return [format_product_data(row) for row in rows]
    finally:
        cursor.close()
        conn.close()


def get_product_by_id(product_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT * FROM products WHERE id = %s;', (product_id,))
        row = cursor.fetchone()
        return format_product_data(row) if row else None
    finally:
        cursor.close()
        conn.close()


def get_products_by_price_range(min_p: float, max_p: float):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            'SELECT * FROM products WHERE price BETWEEN %s AND %s;', 
            (min_p, max_p)
        )
        rows = cursor.fetchall()
        return [format_product_data(row) for row in rows]
    finally:
        cursor.close()
        conn.close()


def search_products(price: float, product_type: Optional[str] = None):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        if product_type:
            query = 'SELECT * FROM products WHERE price = %s AND type = %s;'
            params = (price, product_type)
        else:
            query = 'SELECT * FROM products WHERE price = %s;'
            params = (price,)
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [format_product_data(row) for row in rows]
    finally:
        cursor.close()
        conn.close()


# ==============================
# WRITE / MODIFY METHODS
# ==============================

def add_new_product(product: ProductRequest):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO products (name, price, type, discount_percent) VALUES (%s, %s, %s, %s);",
            (product.Name, product.Price, product.Type, product.DiscountPercent)
        )
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()


def update_existing_product(product: ProductRequest):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE products SET name = %s, price = %s, type = %s, discount_percent = %s WHERE id = %s;",
            (product.Name, product.Price, product.Type, product.DiscountPercent, product.ID)
        )
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()


def bulk_delete_products(product_ids: List[int]) -> int:
    if not product_ids:
        return 0
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Construct PostgreSQL string tuple placeholders safely
        placeholders = ', '.join(['%s'] * len(product_ids))
        query = f"DELETE FROM products WHERE id IN ({placeholders});"
        cursor.execute(query, tuple(product_ids))
        deleted_count = cursor.rowcount
        conn.commit()
        return deleted_count
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()


def bulk_save_products(products: List[ProductRequest]):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        for item in products:
            if getattr(item, "ID", None):
                cursor.execute(
                    "UPDATE products SET name = %s, price = %s, type = %s, discount_percent = %s WHERE id = %s;",
                    (item.Name, item.Price, item.Type, item.DiscountPercent, item.ID)
                )
            else:
                cursor.execute(
                    "INSERT INTO products (name, price, type, discount_percent) VALUES (%s, %s, %s, %s);",
                    (item.Name, item.Price, item.Type, item.DiscountPercent)
                )
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()


# ==============================
# AUTHENTICATION & TOKENS
# ==============================

def verify_token(token: str) -> bool:
    if not token:
        return False
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT id FROM tokens WHERE token = %s;', (token,))
        row = cursor.fetchone()
        return row is not None
    finally:
        cursor.close()
        conn.close()


def authenticate_user(username, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT id, username, password FROM users WHERE username = %s;", 
            (username,)
        )
        user = cursor.fetchone()

        if user and user["password"] == password:
            token_str = "generated_token_value"
            cursor.execute(
                "INSERT INTO tokens (user_id, token) VALUES (%s, %s);",
                (user["id"], token_str)
            )
            conn.commit()
            return token_str
            
        return None
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()
