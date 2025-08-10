# utils.py
import os
import pandas as pd
import psycopg2
from psycopg2 import extras
import math
from datetime import datetime
from db import PG_PARAMS

SAVEING_PATH = "exports"

# User management functions
def get_user_by_username(username):
    conn = psycopg2.connect(**PG_PARAMS)
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE username = %s", (username,))
    row = cur.fetchone()
    conn.close()
    if row:
        return {
            "id": row[0],
            "username": row[1],
            "password_hash": row[2],
            "role": row[3]
        }
    return None

def update_user_password(user_id, new_password_hash):
    conn = psycopg2.connect(**PG_PARAMS)
    cur = conn.cursor()
    cur.execute(
        "UPDATE users SET password_hash = %s WHERE id = %s",
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
        query = f"SELECT id, username, role FROM users WHERE role NOT IN ({placeholders}) ORDER BY username"
        cur.execute(query, exclude_roles)
    else:
        cur.execute("SELECT id, username, role FROM users ORDER BY username")

    users = cur.fetchall()
    cur.close()
    conn.close()
    return users
# ========================

# Transaction management functions
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
# ========================

# *******************************************************
# * Dim table management functions            *
# *******************************************************

# Truck management functions
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
# ========================

# Supplier management functions
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
# ========================

# Zone management functions
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
# ========================

# Factory management functions
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
# ========================

# Representative management functions
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
# ========================
# *******************************************************

# Custody management functions
def get_custody_by_user_id(user_id):
    conn = psycopg2.connect(**PG_PARAMS)
    cur = conn.cursor(cursor_factory=extras.RealDictCursor)
    cur.execute("SELECT * FROM custody WHERE user_id = %s ORDER BY date", (user_id,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

# Data entry functions
def fetch_all_trucks_with_owners():
    try:
        conn = psycopg2.connect(**PG_PARAMS)
        cur = conn.cursor()
        cur.execute("""
            SELECT t.truck_num, o.owner_name
            FROM trucks t
            JOIN truck_owners o ON t.owner_id = o.owner_id
            ORDER BY t.truck_num
        """)
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return rows  # [(truck_num, owner_name), ...]
    except Exception as e:
        print(f"Error fetching trucks with owners: {e}")
        return []

def get_or_create_date_id(cur, full_date):
    cur.execute("SELECT date_id FROM dim_date WHERE full_date = %s", (full_date,))
    row = cur.fetchone()
    if row:
        return row[0]
    cur.execute("""
        INSERT INTO dim_date (full_date, year, month, day, day_name)
        VALUES (
            %s,
            EXTRACT(YEAR FROM %s::date),
            EXTRACT(MONTH FROM %s::date),
            EXTRACT(DAY FROM %s::date),
            TO_CHAR(%s::date, 'Day')
        )
        RETURNING date_id
    """, (full_date, full_date, full_date, full_date, full_date))
    return cur.fetchone()[0]

def get_id_by_name(cur, table, id_col, name_col, name):
    cur.execute(f"SELECT {id_col} FROM {table} WHERE {name_col} = %s", (name,))
    row = cur.fetchone()
    if row:
        return row[0]
    cur.execute(f"INSERT INTO {table} ({name_col}) VALUES (%s) RETURNING {id_col}", (name,))
    return cur.fetchone()[0]

def save_data_entry(data):
    """
    data: dict يحتوي على القوائم القادمة من الفورم
    """
    try:
        conn = psycopg2.connect(**PG_PARAMS)
        cur = conn.cursor()

        for i in range(len(data["dates"])):
            if not data["dates"][i] or not data["truck_nums"][i] or not data["suppliers"][i] \
               or not data["factories_list"][i] or not data["zones_list"][i] or not data["representatives_list"][i]:
                continue

            date_id = get_or_create_date_id(cur, data["dates"][i])
            supplier_id = get_id_by_name(cur, "suppliers", "supplier_id", "supplier_name", data["suppliers"][i])
            factory_id = get_id_by_name(cur, "factories", "factory_id", "factory_name", data["factories_list"][i])
            zone_id = get_id_by_name(cur, "zones", "zone_id", "zone_name", data["zones_list"][i])
            representative_id = get_id_by_name(cur, "representatives", "representative_id", "representative_name", data["representatives_list"][i])
            owner_id = get_id_by_name(cur, "truck_owners", "owner_id", "owner_name", data["truck_owners"][i]) if data["truck_owners"][i] else None

            cur.execute("SELECT truck_num FROM trucks WHERE truck_num = %s", (data["truck_nums"][i],))
            if not cur.fetchone():
                cur.execute("INSERT INTO trucks (truck_num, owner_id) VALUES (%s, %s)", (data["truck_nums"][i], owner_id))

            cur.execute("""
                INSERT INTO main (date_id, truck_num, supplier_id, factory_id, zone_id, weight, ohda, factory_price, sell_price, representative_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                date_id, data["truck_nums"][i], supplier_id, factory_id, zone_id,
                data["weights"][i] or None, data["ohdas"][i] or None,
                data["factory_prices"][i] or None, data["sell_prices"][i] or None,
                representative_id
            ))

        conn.commit()
        cur.close()
        conn.close()
        return True

    except Exception as e:
        print(f"Error saving data: {e}")
        return False
# *******************************************************

def get_current_month_records():
    try:
        conn = psycopg2.connect(**PG_PARAMS)
        cur = conn.cursor()

        cur.execute("""
            SELECT 
                m.naqla_id,
                d.full_date,
                m.truck_num,
                t_o.owner_name AS truck_owner,
                s.supplier_name,
                f.factory_name,
                z.zone_name,
                m.weight,
                m.ohda,
                m.factory_price,
                m.sell_price,
                r.representative_name
            FROM main m
            JOIN dim_date d ON m.date_id = d.date_id
            JOIN trucks t ON m.truck_num = t.truck_num
            JOIN truck_owners t_o ON t.owner_id = t_o.owner_id
            JOIN suppliers s ON m.supplier_id = s.supplier_id
            JOIN factories f ON m.factory_id = f.factory_id
            JOIN zones z ON m.zone_id = z.zone_id
            JOIN representatives r ON m.representative_id = r.representative_id
            WHERE d.month = EXTRACT(MONTH FROM CURRENT_DATE)
              AND d.year = EXTRACT(YEAR FROM CURRENT_DATE)
            ORDER BY d.full_date DESC
        """)

        records = cur.fetchall()
        # نحول الحقل الثاني لتاريخ
        records = [(r[0], datetime.strptime(r[1], "%Y-%m-%d"), *r[2:]) for r in records]
        cur.close()
        conn.close()
        return records

    except Exception as e:
        print("خطأ في جلب البيانات:", e)
        return []


def update_naqla_record(naqla_id, data):
    """
    Corrected function to update a single record in the main table.
    """
    try:
        conn = psycopg2.connect(**PG_PARAMS)
        cur = conn.cursor()
        
        # Get IDs for the provided names
        date_id = get_or_create_date_id(cur, data['date'])
        supplier_id = get_id_by_name(cur, 'suppliers', 'supplier_id', 'supplier_name', data['supplier'])
        factory_id = get_id_by_name(cur, 'factories', 'factory_id', 'factory_name', data['factory'])
        zone_id = get_id_by_name(cur, 'zones', 'zone_id', 'zone_name', data['zone'])
        representative_id = get_id_by_name(cur, 'representatives', 'representative_id', 'representative_name', data['representative'])
        
        # Update the main table with the new data.
        # Note: 'truck_owner' is not a column in 'main' so we don't include it here.
        cur.execute("""
            UPDATE main
            SET date_id=%s, truck_num=%s, supplier_id=%s, factory_id=%s, zone_id=%s,
                weight=%s, ohda=%s, factory_price=%s, sell_price=%s, representative_id=%s
            WHERE naqla_id = %s
        """, (
            date_id,
            data['truck_num'],
            supplier_id,
            factory_id,
            zone_id,
            data['weight'],
            data['ohda'],
            data['factory_price'],
            data['sell_price'],
            representative_id,
            naqla_id
        ))
        
        conn.commit()
        cur.close()
        conn.close()
        return {'success': True}
    except Exception as e:
        print(f"Error updating record: {e}")
        conn.rollback()
        return {'success': False, 'error': str(e)}
