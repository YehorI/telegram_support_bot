import aiosqlite
from datetime import datetime

async def initialize_db():
    async with aiosqlite.connect('my_bot_database.db') as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS bonus_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER NOT NULL,
                screenshot_file_id INTEGER,
                coupon_file_id INTEGER,
                phone_number TEXT,
                status TEXT DEFAULT 'pending',
                request_date TEXT,     -- Adding date of the request
                username TEXT,          -- Adding username
                message_id INTEGER
            );
        """)

        await db.execute("""
            CREATE TABLE IF NOT EXISTS unique_users (
                 id INTEGER PRIMARY KEY,
                 user_id,
                 username TEXT,
                 date TEXT
            );
        """)

        await init_messages(db)

        await db.commit()


async def register_unique_user(user_id: int, username: str):
    date = datetime.now().isoformat()
    try:
        async with aiosqlite.connect('my_bot_database.db') as db:
            query = "INSERT OR IGNORE INTO unique_users(user_id, username, date) VALUES (?, ?, ?);"
            
            await db.execute(query, (user_id, username, date))
            await db.commit()
            
    except Exception as e:
        print(f"An error occurred: {e}")


async def db_save_bonus_request(
    chat_id,
    screenshot_file_id,
    coupon_file_id,
    phone_number,
    username,
    message_id,
) -> int:
    """ Returns saved bonus request id"""
    request_date = datetime.now().isoformat()  # ISO formatted current date and time
    async with aiosqlite.connect('my_bot_database.db') as db:
        cursor = await db.execute("""
            INSERT INTO bonus_requests 
            (chat_id, screenshot_file_id, coupon_file_id, phone_number, request_date, username, message_id) 
            VALUES (?, ?, ?, ?, ?, ?, ?);
        """,
        (
            chat_id,
            screenshot_file_id,
            coupon_file_id,
            phone_number,
            request_date,
            username,
            message_id,
        )
        )
        await db.commit()
        return cursor.lastrowid


async def db_accept_decline_bonus(message_id, new_status):
    async with aiosqlite.connect('my_bot_database.db') as db:

        await db.execute("""
            UPDATE bonus_requests
            SET status = ?
            WHERE message_id = ?;
        """, (new_status, message_id))

        await db.commit()


async def db_get_bonus_request_status(
    message_id
) -> str | None:

    async with aiosqlite.connect('my_bot_database.db') as db:

        async with db.execute(
            "SELECT status FROM bonus_requests WHERE message_id = ?",
            (message_id,)
        ) as cursor:
            row = await cursor.fetchone()
        
            if row:
                return row[0]
            else:
                return None


async def db_get_user_chatid_by_support_message_id(message_id):
    async with aiosqlite.connect('my_bot_database.db') as db:

        async with db.execute(
            "SELECT chat_id FROM bonus_requests WHERE message_id = ?",
            (message_id,)
        ) as cursor:
            row = await cursor.fetchone()
        
            if row:
                return row[0]
            else:
                return None


async def db_get_bonus_request_stats(
    start_date,
    end_date
):

    async with aiosqlite.connect('my_bot_database.db') as db:
        # Query to calculate the statistics for total requests, processed, accepted, declined, and pending
        stats_query = """
        SELECT 
            COUNT(*) as total_requests,
            SUM(CASE WHEN status IN ('accepted', 'declined') THEN 1 ELSE 0 END) as processed,
            SUM(CASE WHEN status = 'accepted' THEN 1 ELSE 0 END) as accepted,
            SUM(CASE WHEN status = 'declined' THEN 1 ELSE 0 END) as declined,
            SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending
        FROM 
            bonus_requests
        WHERE 
            DATE(request_date) BETWEEN DATE(?) AND DATE(?);
        """

        cursor_stats = await db.execute(stats_query, (start_date, end_date))
        row = await cursor_stats.fetchone()

        # Count total unique users
        unique_user_query = "SELECT COUNT(DISTINCT user_id) FROM unique_users WHERE DATE(date) BETWEEN DATE(?) AND DATE(?);"
        cursor_unique_users = await db.execute(unique_user_query, (start_date, end_date))
        total_unique_users = await cursor_unique_users.fetchone()

        # Count unique users who made bonus requests
        unique_bonus_requesters_query = """
        SELECT COUNT(DISTINCT chat_id) 
        FROM bonus_requests 
        WHERE DATE(request_date) BETWEEN DATE(?) AND DATE(?);
        """
        cursor_unique_requesters = await db.execute(unique_bonus_requesters_query, (start_date, end_date))
        total_unique_requesters = await cursor_unique_requesters.fetchone()

        # Calculate the ratio of unique bonus requesters to total unique users
        ratio = total_unique_requesters[0] / total_unique_users[0] if total_unique_users[0] > 0 else 0

        # Building the stats dictionary
        stats = {
            "total_unique_users": total_unique_users[0],
            "total_unique_requesters": total_unique_requesters[0],
            "unique_requester_user_ratio": int(ratio * 100),
            "total_requests": row[0],
            "pending": row[4],
            "processed": row[1],
            "accepted": row[2],
            "declined": row[3],
        }
        return stats


async def db_get_id_and_request_date():
    async with aiosqlite.connect('my_bot_database.db') as db:
        # Prepare the SQL query to fetch the id and request_date from the bonus_requests table.
        query = "SELECT id, request_date FROM bonus_requests WHERE status = 'pending'"

        # Execute the query and fetch all results.
        async with db.execute(query) as cursor:
            # Fetch all results as a list of tuples.
            results = await cursor.fetchall()

    # Return the list of tuples.
    return results


async def init_messages(db):
    await db.execute(
        """
        CREATE TABLE IF NOT EXISTS messages (
            user_message_id INTEGER PRIMARY KEY,
            user_id INTEGER,
            support_message_id
        )
        """
    )


async def db_add_message(user_message_id, user_id, support_message_id):
    async with aiosqlite.connect('my_bot_database.db') as db:
        await db.execute(
            "INSERT INTO messages (user_message_id, user_id, support_message_id) VALUES (?, ?, ?)",
            (user_message_id, user_id, support_message_id)
        )
        await db.commit()


async def db_get_message_user_id(support_message_id):
    async with aiosqlite.connect('my_bot_database.db') as db:
        cursor = await db.execute(
            "SELECT user_id FROM messages WHERE support_message_id = (?)",
            (support_message_id,)
        )
        row = await cursor.fetchone()
        return row[0]
