import psycopg2
from datetime import datetime
from db import PG_PARAMS

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
        records = [(r[0], datetime.strptime(r[1], "%Y-%m-%d"), *r[2:]) for r in records]
        cur.close()
        conn.close()
        return records

    except Exception as e:
        print("خطأ في جلب البيانات:", e)
        return []

def update_naqla_record(naqla_id, data):
    try:
        conn = psycopg2.connect(**PG_PARAMS)
        cur = conn.cursor()
        
        date_id = get_or_create_date_id(cur, data['date'])
        supplier_id = get_id_by_name(cur, 'suppliers', 'supplier_id', 'supplier_name', data['supplier'])
        factory_id = get_id_by_name(cur, 'factories', 'factory_id', 'factory_name', data['factory'])
        zone_id = get_id_by_name(cur, 'zones', 'zone_id', 'zone_name', data['zone'])
        representative_id = get_id_by_name(cur, 'representatives', 'representative_id', 'representative_name', data['representative'])
        
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