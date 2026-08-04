import aiosqlite
from modules.product_models import ProductsRequest

DB_FILE = 'inventory.sqlite'


# ==============================
# READ METHODS
# ==============================

async def get_all_products():
	"""Fetch all products from the database."""
	async with aiosqlite.connect(DB_FILE) as db:
		db.row_factory = aiosqlite.Row
		async with db.execute('SELECT * FROM Products') as cursor:
			rows = await cursor.fetchall()
			return [dict(row) for row in rows]


async def get_product_by_id(product_id: int):
	"""Fetch a single product by its unique ID."""
	async with aiosqlite.connect(DB_FILE) as db:
		db.row_factory = aiosqlite.Row
		async with db.execute('SELECT * FROM Products WHERE ID = ?',
		                      (product_id,)) as cursor:
			row = await cursor.fetchone()
			return dict(row) if row else None


async def get_products_by_price_range(min_p: float,
                                      max_p: float):
	"""Fetch all products falling within a specific price range."""
	async with aiosqlite.connect(DB_FILE) as db:
		db.row_factory = aiosqlite.Row
		async with db.execute('SELECT * FROM Products WHERE Price BETWEEN ? AND ?',
                              (min_p, max_p)) as cursor:
			rows = await cursor.fetchall()
			return [dict(row) for row in rows]


async def search_products(price: float,
                          product_type: str = None):
	"""Search products by target price and optional product category."""
	async with aiosqlite.connect(DB_FILE) as db:
		db.row_factory = aiosqlite.Row
		if product_type:
			query = 'SELECT * FROM Products WHERE Price = ? AND Type = ?'
			params = (price, product_type)
		else:
			query = 'SELECT * FROM Products WHERE Price = ?'
			params = (price,)

		async with db.execute(query, params) as cursor:
			rows = await cursor.fetchall()
			return [dict(row) for row in rows]


# ==============================
# WRITE / MODIFY METHODS
# ==============================

async def add_new_product(product: ProductsRequest):
	"""Insert a new product entry into the database."""
	async with aiosqlite.connect(DB_FILE) as db:
		await db.execute("INSERT INTO Products (ID, Name, Price, Type) VALUES (?, ?, ?, ?)",
				(product.ID,
				product.Name,
				product.Price,
				product.Type
				)
		    )
		await db.commit()


async def update_existing_product(product: ProductsRequest):
	"""Update details for an existing product entry."""
	async with aiosqlite.connect(DB_FILE) as db:
		await db.execute("UPDATE Products SET Name = ?, Price = ?, Type = ? WHERE ID = ?",
				(product.Name,
				product.Price,
				product.Type,
				product.ID
				)
			)
		await db.commit()

def calculate_discount(price: float, discount_percent: float) -> float:
    """Calculates final price based on discount percentage."""
    if discount_percent <= 0:
        return price
    discount_amount = price * (discount_percent / 100.0)
    return round(price - discount_amount, 2)

async def format_product_data(row: dict) -> dict:
    """Helper to attach FinalPrice calculation to database records."""
    product = dict(row)
    price = product.get("Price", 0.0)
    discount = product.get("DiscountPercent", 0.0)
    product["FinalPrice"] = calculate_discount(price, discount)
    return product

# Bulk Delete Logic
async def bulk_delete_products(product_ids: List[int]) -> int:
    async with aiosqlite.connect(DB_FILE) as db:
        placeholders = ', '.join('?' * len(product_ids))
        query = f"DELETE FROM Products WHERE ID IN ({placeholders})"
        cursor = await db.execute(query, product_ids)
        await db.commit()
        return cursor.rowcount  # Returns total count of deleted records

# Bulk Upsert (Save/Modify Multiple)
async def bulk_save_products(products: List[ProductRequest]):
    async with aiosqlite.connect(DB_FILE) as db:
        for item in products:
            if item.ID:
                await db.execute(
                    "UPDATE Products SET Name = ?, Price = ?, Type = ?, DiscountPercent = ? WHERE ID = ?",
                    (item.Name, item.Price, item.Type, item.DiscountPercent, item.ID)
                )
            else:
                await db.execute(
                    "INSERT INTO Products (Name, Price, Type, DiscountPercent) VALUES (?, ?, ?, ?)",
                    (item.Name, item.Price, item.Type, item.DiscountPercent)
                )
        await db.commit()

# ==============================
# AUTHENTICATION & TOKENS
# ==============================

async def verify_token(token_value: str) -> bool:
	"""Verify if a provided Bearer token exists in the database."""
	if not token_value:
		return False

	async with aiosqlite.connect(DB_FILE) as db:
		db.row_factory = aiosqlite.Row
		async with db.execute('SELECT * FROM Tokens WHERE token_value = ?',
		                      (token_value,)) as cursor:
			row = await cursor.fetchone()
			return row is not None


async def authenticate_user(username: str,
                            password: str) -> str:
	"""
    Validates user credentials against the database and returns a token if valid.
    Returns None if credentials do not match.
    """
	async with aiosqlite.connect(DB_FILE) as db:
		db.row_factory = aiosqlite.Row
		async with db.execute('SELECT token_value FROM Users INNER JOIN Tokens ON Users.id = Tokens.user_id WHERE username = ? AND password = ?',
				(username,
				password)) as cursor:
			row = await cursor.fetchone()
			return row["token_value"] if row else None
