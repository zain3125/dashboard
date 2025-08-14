import psycopg2
from psycopg2 import extras
from db import PG_PARAMS

def get_user_by_username(username):
    conn = psycopg2.connect(**PG_PARAMS)
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE username = %s", (username,))
    row = cur.fetchone()
    conn.close()
    if row:
        return {
            "user_id": row[0],
            "username": row[1],
            "password_hash": row[2],
            "role": row[3]
        }
    return None

def update_user_password(user_id, new_password_hash):
    conn = psycopg2.connect(**PG_PARAMS)
    cur = conn.cursor()
    cur.execute(
        "UPDATE users SET password_hash = %s WHERE user_id = %s",
        (new_password_hash, user_id)
    )
    conn.commit()
    cur.close()
    conn.close()

def get_all_users(exclude_roles=None):
    conn = psycopg2.connect(**PG_PARAMS)
    cur = conn.cursor(cursor_factory=extras.RealDictCursor)

    if exclude_roles:
        placeholders = ",".join(["%s"] * len(exclude_roles))
        query = f"SELECT user_id, username, role FROM users WHERE role NOT IN ({placeholders}) ORDER BY username"
        cur.execute(query, exclude_roles)
    else:
        cur.execute("SELECT user_id, username, role FROM users ORDER BY username")

    users = cur.fetchall()
    cur.close()
    conn.close()
    return users