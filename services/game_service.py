import aiosqlite
from modules.product_models import ProductsRequest

DB_FILE = 'games_inventory.sqlite'

async def get_all_games():
    async with aiosqlite.connect(DB_FILE) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute('SELECT * FROM Products') as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

async def get_game_by_id(game_id: int):
    async with aiosqlite.connect(DB_FILE) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute('SELECT * FROM Products WHERE ID = ?', (game_id,)) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None


## POST Methods ##
async def add_new_game(game: ProductsRequest):
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute(
            "INSERT INTO Products (ID, Name, Price, Type) VALUES (?, ?, ?, ?)",
            (game.ID, game.Name, game.Price, game.Type)
        )
        await db.commit()

async def update_existing_game(game: ProductsRequest):
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute(
            "UPDATE Products SET Name = ?, Price = ?, Type = ? WHERE ID = ?",
            (game.Name, game.Price, game.Type, game.ID)
        )
        await db.commit()

## Functions for Module 5 ##

async def get_games_by_price_range(min_p: float, max_p: float):
    async with aiosqlite.connect(DB_FILE) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute('SELECT * FROM Products WHERE Price BETWEEN ? AND ?', (min_p, max_p)) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

async def search_games(price: float, g_type: str = None):
    async with aiosqlite.connect(DB_FILE) as db:
        db.row_factory = aiosqlite.Row
        if g_type:
            query = 'SELECT * FROM Products WHERE Price = ? AND Type = ?'
            params = (price, g_type)
        else:
            query = 'SELECT * FROM Products WHERE Price = ?'
            params = (price,)

        async with db.execute(query, params) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
