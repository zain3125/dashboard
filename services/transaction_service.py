import os
import pandas as pd
import psycopg2
from db import PG_PARAMS

SAVEING_PATH = "exports"

def export_transactions_to_excel(start, end):
    try:
        data = fetch_transactions_from_db(start, end)
        if not data:
            return None

        columns = ['date', 'bank_name', 'receiver', 'phone_number', 'amount', 'transaction_id', 'status']
        df = pd.DataFrame(data, columns=columns)

        os.makedirs(SAVEING_PATH, exist_ok=True)
        file_path = os.path.join(SAVEING_PATH, f"Transactions {start} to {end}.xlsx")
        df.to_excel(file_path, index=False)
        return file_path
    except Exception as e:
        print(f"Export error: {e}")
        return None

def fetch_transactions_from_db(start, end, limit=10, offset=0):
    try:
        conn = psycopg2.connect(**PG_PARAMS)
        cur = conn.cursor()
        query = """
        SELECT 
            t.date,
            b.bank_name,
            t.receiver,
            t.phone_number,
            t.amount,
            t.transaction_id,
            t.status
        FROM transactions t
        JOIN senders s ON t.sender = s.sender_id
        LEFT JOIN bank_name b ON s.sender_id = b.bank_id
        WHERE t.date BETWEEN %s AND %s
        ORDER BY t.date DESC
        LIMIT %s OFFSET %s;
        """
        cur.execute(query, (start, end, limit, offset))
        rows = cur.fetchall()
        conn.close()
        return rows
    except Exception as e:
        print(f"DB fetch error: {e}")
        return []