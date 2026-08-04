import sqlite3

DB_FILE = 'inventory.sqlite'


def init_db():
	conn = sqlite3.connect(DB_FILE)
	cursor = conn.cursor()

	# Drop tables if they exist to start fresh
	cursor.execute("DROP TABLE IF EXISTS Products")
	cursor.execute("DROP TABLE IF EXISTS Tokens")
	cursor.execute("DROP TABLE IF EXISTS Users")

	# Create Products Table
	cursor.execute("""
                   CREATE TABLE Products
                   (
                       ID    INTEGER PRIMARY KEY,
                       Name  TEXT NOT NULL,
                       Price REAL NOT NULL,
                       Type  TEXT NOT NULL,
                       DiscountPercent REAL DEFAULT 0.0
                   )
	            """)

	# Create Users Table
	cursor.execute("""
                   CREATE TABLE Users
                   (
                       id       INTEGER PRIMARY KEY AUTOINCREMENT,
                       username TEXT UNIQUE NOT NULL,
                       password TEXT        NOT NULL
                   )
	               """)

	# Create Tokens Table
	cursor.execute("""
                   CREATE TABLE Tokens
                   (
                       id          INTEGER PRIMARY KEY AUTOINCREMENT,
                       token_value TEXT UNIQUE NOT NULL,
                       user_id     INTEGER     NOT NULL,
                       FOREIGN KEY (user_id) REFERENCES Users (id)
                   )
	               """)

	# Seed Sample Products (SoftStack Stockroom / CodeLatte Cozy Theme)
	sample_products = [
			(
					1,
					"Cozy Cinnamon Latte",
					4.50,
					"Beverage"
					),
			(
					2,
					"CodeLatte Blend Beans (12oz)",
					16.50,
					"Coffee Beans"
					),
			(
					3,
					"Vanilla Bean Matchbox",
					3.00,
					"Merch"
					),
			(
					4,
					"SoftStack Ceramic Mug",
					14.00,
					"Merch"
					),
			(
					5,
					"Iced Salted Caramel Mocha",
					5.25,
					"Beverage"
					),
			(
					6,
					"Warm Almond Croissant",
					3.75,
					"Pastry"
					),
			(
					7,
					"Retro Espresso Dripper",
					24.99,
					"Equipment"
					)
			]

	cursor.executemany(
			"INSERT INTO Products (ID, Name, Price, Type) VALUES (?, ?, ?, ?)",
			sample_products
			)

	# Seed User & Authorization Token for Testing
	cursor.execute("INSERT INTO Users (id, username, password) VALUES (1, 'nicole', 'softstack123')")
	cursor.execute("INSERT INTO Tokens (token_value, user_id) VALUES ('mcc-student-2026', 1)")

	conn.commit()
	conn.close()
	print("✨ Database successfully initialized with cozy test data!")


if __name__ == "__main__":
	init_db()
