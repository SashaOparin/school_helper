import aiosqlite


async def create_tables(app):
    conn = await aiosqlite.connect("lead.db")
    await conn.execute("""CREATE TABLE IF NOT EXISTS users(
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            id_tg INTEGER UNIQUE, 
                            username TEXT NULL, 
                            class INTEGER NULL,
                            created_at DATETIME DEFAULT CURRENT_TIMESTAMP)""")

    await conn.commit()
    await conn.close()
