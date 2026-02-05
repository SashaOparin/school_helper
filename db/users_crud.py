import aiosqlite


async def create_user(id_tg: int, username: str = None):
    conn = await aiosqlite.connect("lead.db")
    await conn.execute(
        "INSERT INTO users (id_tg, username) VALUES (?,?)", (id_tg, username)
    )
    await conn.commit()
    await conn.close()


async def get_user(id_tg: int):
    async with  aiosqlite.connect("lead.db") as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM users WHERE id_tg = ?", (id_tg,))
        user = await cursor.fetchone()
        if user:
            return dict(user)

async def update_user(id_tg: int, class_num: int):
    async with  aiosqlite.connect("lead.db") as db:
        await db.execute("UPDATE users SET class = ? WHERE id_tg = ?", (class_num, id_tg))
        await db.commit()
        return True

# async def victorins(id_tg: int):
#     async with  aiosqlite.connect("lead.db") as db:
#         db.row_factory = aiosqlite.Row
#         cursor = await db.execute("SELECT * FROM users WHERE id_tg = ?", (victorins,))
#         user = await cursor.fetchone()
#         if user:
#             return dict(user)
        
async def create_victorina(id_tg: int, victorina: str, answer: str, topic: str):
    conn = await aiosqlite.connect("lead.db")
    await conn.execute(
        "INSERT INTO users (victorina, answer, topic) VALUES (?,?)", (victorina, answer, topic)
    )
    await conn.commit()
    await conn.close()

async def get_victorina(id_tg: int):
    async with  aiosqlite.connect("lead.db") as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM victorina WHERE id_tg = ?", (id_tg,))
        user = await cursor.fetchone()
        if user:
            return dict(user)
        
