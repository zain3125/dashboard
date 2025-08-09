import os
import pandas as pd
import psycopg2
import math
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
        JOIN senders s ON t.sender = s.id
        LEFT JOIN bank_name b ON s.id = b.id
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

def insert_truck_owner(truck_number, truck_owner, phone_number):
    try:
        conn = psycopg2.connect(**PG_PARAMS)
        cur = conn.cursor()

        # تحقق إذا كان المالك موجود مسبقًا
        cur.execute("""
            SELECT owner_id FROM truck_owners
            WHERE owner_name = %s AND phone = %s
        """, (truck_owner, phone_number))
        owner_result = cur.fetchone()

        if owner_result:
            owner_id = owner_result[0]
        else:
            # إدخال مالك جديد
            cur.execute("""
                INSERT INTO truck_owners (owner_name, phone)
                VALUES (%s, %s)
                RETURNING owner_id
            """, (truck_owner, phone_number))
            owner_id = cur.fetchone()[0]

        # تحقق إذا كان رقم الشاحنة موجود مسبقًا
        cur.execute("""
            SELECT truck_num FROM trucks
            WHERE truck_num = %s
        """, (truck_number,))
        truck_exists = cur.fetchone()

        if truck_exists:
            raise Exception(f"🚫 رقم الشاحنة '{truck_number}' موجود بالفعل في قاعدة البيانات.")

        # إدخال الشاحنة وربطها بالمالك
        cur.execute("""
            INSERT INTO trucks (truck_num, owner_id)
            VALUES (%s, %s)
        """, (truck_number, owner_id))

        conn.commit()
        cur.close()
        conn.close()

    except Exception as e:
        print(f"Error inserting truck owner and truck: {e}")
        raise

def fetch_all_truck_owners(limit=10, offset=0):
    try:
        conn = psycopg2.connect(**PG_PARAMS)
        cur = conn.cursor()

        cur.execute("""
            SELECT t.truck_num, o.owner_name, o.phone
            FROM trucks t
            JOIN truck_owners o ON t.owner_id = o.owner_id
            ORDER BY t.truck_num
            LIMIT %s OFFSET %s
        """, (limit, offset))

        rows = cur.fetchall()

        # عدد السجلات الكلي لحساب الصفحات
        cur.execute("SELECT COUNT(*) FROM trucks")
        total_count = cur.fetchone()[0]

        cur.close()
        conn.close()

        truck_owners = [
            {'truck_number': r[0], 'truck_owner': r[1], 'phone_number': r[2]} for r in rows
        ]

        return truck_owners, total_count

    except Exception as e:
        print(f"Error fetching truck owners: {e}")
        return [], 0

def search_truck_owners(query):
    try:
        conn = psycopg2.connect(**PG_PARAMS)
        cur = conn.cursor()

        cur.execute("""
            SELECT t.truck_num, o.owner_name, o.phone
            FROM trucks t
            JOIN truck_owners o ON t.owner_id = o.owner_id
            WHERE t.truck_num ILIKE %s
               OR o.owner_name ILIKE %s
               OR o.phone ILIKE %s
            ORDER BY t.truck_num
        """, (f"%{query}%", f"%{query}%", f"%{query}%"))

        rows = cur.fetchall()
        cur.close()
        conn.close()

        return [{'truck_number': r[0], 'truck_owner': r[1], 'phone_number': r[2]} for r in rows]
    except Exception as e:
        print(f"Error searching truck owners: {e}")
        return []

def insert_supplier(supplier_name, phone_number):
    try:
        conn = psycopg2.connect(**PG_PARAMS)
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO suppliers (supplier_name, phone)
            VALUES (%s, %s)
            ON CONFLICT (supplier_name) DO NOTHING
        """, (supplier_name, phone_number))
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error inserting supplier: {e}")
        raise

def fetch_all_suppliers(limit=10, offset=0):
    try:
        conn = psycopg2.connect(**PG_PARAMS)
        cur = conn.cursor()

        cur.execute("""
            SELECT supplier_name, phone
            FROM suppliers
            ORDER BY supplier_name
            LIMIT %s OFFSET %s
        """, (limit, offset))
        rows = cur.fetchall()

        cur.execute("SELECT COUNT(*) FROM suppliers")
        total_count = cur.fetchone()[0]

        cur.close()
        conn.close()

        return [{'supplier_name': r[0], 'phone_number': r[1]} for r in rows], total_count
    except Exception as e:
        print(f"Error fetching suppliers: {e}")
        return [], 0

def search_suppliers(query):
    try:
        conn = psycopg2.connect(**PG_PARAMS)
        cur = conn.cursor()

        cur.execute("""
            SELECT supplier_name, phone
            FROM suppliers
            WHERE supplier_name ILIKE %s OR phone ILIKE %s
            ORDER BY supplier_name
        """, (f"%{query}%", f"%{query}%"))

        rows = cur.fetchall()
        cur.close()
        conn.close()

        return [{'supplier_name': r[0], 'phone_number': r[1]} for r in rows]
    except Exception as e:
        print(f"Error searching suppliers: {e}")
        return []

def insert_zone(zone_name):
    try:
        conn = psycopg2.connect(**PG_PARAMS)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO zones (zone_name)
            VALUES (%s)
            ON CONFLICT (zone_name) DO NOTHING
            RETURNING zone_id;
        """, (zone_name,))
        result = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()

        if result:
            return True  # تمت الإضافة بنجاح
        else:
            return False  # موجود مسبقًا

    except Exception as e:
        print(f"Error inserting zone: {e}")
        return None  # خطأ في التنفيذ

# الدالة لجلب كل المناطق (مع pagination)
def fetch_all_zones(limit=10, offset=0):
    try:
        conn = conn = psycopg2.connect(**PG_PARAMS)
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM zones")
        total = cursor.fetchone()[0]
        cursor.execute("SELECT zone_name FROM zones ORDER BY zone_name LIMIT %s OFFSET %s", (limit, offset))
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return [row[0] for row in rows], total
    except Exception as e:
        print(f"Error fetching zones: {e}")
        return [], 0

# الدالة للبحث
def search_zones(query):
    try:
        conn = conn = psycopg2.connect(**PG_PARAMS)
        cursor = conn.cursor()

        cursor.execute("SELECT zone_name FROM zones WHERE zone_name ILIKE %s", (f"%{query}%",))
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return [row[0] for row in rows]
    except Exception as e:
        print(f"Error searching zones: {e}")
        return []

def insert_factory(factory_name):
    try:
        conn = psycopg2.connect(**PG_PARAMS)
        cursor = conn.cursor()

        # هل الاسم موجود مسبقاً؟
        cursor.execute("SELECT 1 FROM factories WHERE factory_name = %s", (factory_name,))
        if cursor.fetchone():
            return "exists"

        # الإدخال
        cursor.execute("INSERT INTO factories (factory_name) VALUES (%s)", (factory_name,))
        conn.commit()
        cursor.close()
        conn.close()
        return "inserted"
    except Exception as e:
        print(f"Error inserting factory: {e}")
        return "error"


def fetch_all_factories(page, per_page, query):
    conn = psycopg2.connect(**PG_PARAMS)
    cursor = conn.cursor()

    offset = (page - 1) * per_page

    if query:
        cursor.execute("""
            SELECT factory_name
            FROM factories
            WHERE factory_name ILIKE %s
            ORDER BY factory_name ASC
        """, (f"%{query}%",))
    else:
        cursor.execute("SELECT COUNT(*) FROM factories")
        total_rows = cursor.fetchone()[0]
        total_pages = math.ceil(total_rows / per_page) if total_rows else 1

        cursor.execute("""
            SELECT factory_name
            FROM factories
            ORDER BY factory_name ASC
            LIMIT %s OFFSET %s
        """, (per_page, offset))

    rows = cursor.fetchall()
    factories = [row[0] for row in rows]

    cursor.close()
    conn.close()

    return factories, total_pages if not query else 1

def search_factories(query):
    try:
        conn = psycopg2.connect(**PG_PARAMS)
        cursor = conn.cursor()
        cursor.execute("SELECT factory_name FROM factories WHERE factory_name ILIKE %s", (f"%{query}%",))
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return [row[0] for row in rows]
    except Exception as e:
        print(f"Error searching factories: {e}")
        return []

def insert_representative(representative_name, phone):
    try:
        conn = psycopg2.connect(**PG_PARAMS)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO representatives (representative_name, phone)
            VALUES (%s, %s)
            ON CONFLICT (representative_name, phone) DO NOTHING
        """, (representative_name, phone))

        conn.commit()
        rows_inserted = cursor.rowcount

        cursor.close()
        conn.close()

        return "inserted" if rows_inserted > 0 else "exists"

    except Exception as e:
        print("Error inserting representative:", e)
        return "error"


def fetch_all_representatives(page, per_page, query=""):
    try:
        conn = psycopg2.connect(**PG_PARAMS)
        cursor = conn.cursor()

        offset = (page - 1) * per_page

        if query:
            cursor.execute("""
                SELECT representative_name, phone FROM representatives
                WHERE representative_name ILIKE %s OR phone ILIKE %s
                ORDER BY representative_id DESC
                LIMIT %s OFFSET %s
            """, (f"%{query}%", f"%{query}%", per_page, offset))
            rows = cursor.fetchall()

            cursor.execute("""
                SELECT COUNT(*) FROM representatives
                WHERE representative_name ILIKE %s OR phone ILIKE %s
            """, (f"%{query}%", f"%{query}%"))
        else:
            cursor.execute("""
                SELECT representative_name, phone FROM representatives
                ORDER BY representative_id DESC
                LIMIT %s OFFSET %s
            """, (per_page, offset))
            rows = cursor.fetchall()

            cursor.execute("SELECT COUNT(*) FROM representatives")

        total_count = cursor.fetchone()[0]
        total_pages = (total_count + per_page - 1) // per_page

        cursor.close()
        conn.close()

        return rows, total_pages

    except Exception as e:
        print(f"Error fetching representatives: {e}")
        return [], 1
