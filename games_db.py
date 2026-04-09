import sqlite3
conn = sqlite3.connect('games_inventory.sqlite')
cursor = conn.cursor()

cursor.execute('DROP TABLE IF EXISTS Products')
cursor.execute('''
    CREATE TABLE Products (
        ID INTEGER PRIMARY KEY,
        Name TEXT NOT NULL, 
        Price REAL NOT NULL,
        Type TEXT NOT NULL
    )
''')

game_data = [
    (0, 'Elden Ring', 59.99, 'FromSoftware'),
    (1, 'Dark Souls', 39.99, 'FromSoftware'),
    (2, 'Stardew Valley', 14.99, 'ConcernedApe'),
    (3, 'Minecraft', 26.95, 'Mojang'),
    (4, 'Supermarket Together', 0.00, 'Free-to-Play'),
    (5, 'The Sims 4', 0.00, 'EA'),
    (6, 'Red Dead Redemption 2', 59.99, 'Rockstar'),
    (7, 'Balatro', 14.99, 'LocalThunk'),
    (8, 'Untitled Goose Game', 19.99, 'House House'),
    (9, 'Hollow Knight', 15.00, 'Team Cherry'),
    (10, 'Among Us', 4.99, 'Innersloth'),
    (11, 'Lethal Company', 9.99, 'Zeekerss'),
    (12, 'Cyberpunk 2077', 89.99, 'CD Projekt Red'),
    (13, 'Dwarf Fortress', 29.99, 'Bay 12 Games'),
    (14, 'Project Zomboid', 19.99, 'The Indie Stone'),
    (15, 'Vampire Survivors', 4.99, 'poncle'),
    (16, 'Portal 2', 9.99, 'Valve'),
    (17, 'Half-Life 2', 9.99, 'Valve'),
    (18, 'Mystery Indie Game', 2.99, 'Anonymous'),
    (19, 'Lost Media Title', 0.00, 'Unknown')
]

cursor.executemany('INSERT INTO Products VALUES (?,?,?,?)', game_data
)
conn.commit()
conn.close()

print("Database created successfully! We did it!")
