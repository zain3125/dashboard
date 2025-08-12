import psycopg2
from psycopg2 import extras
from db import PG_PARAMS

def get_custody_by_user_id(user_id):
    conn = psycopg2.connect(**PG_PARAMS)
    cur = conn.cursor(cursor_factory=extras.RealDictCursor)
    cur.execute("SELECT * FROM custody WHERE user_id = %s ORDER BY date", (user_id,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows