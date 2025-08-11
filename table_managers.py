import psycopg2
import math
from db import PG_PARAMS

class BaseTableManager:
    def __init__(self, table_name, id_column, name_column):
        self.table_name = table_name
        self.id_column = id_column
        self.name_column = name_column

    def get_conn(self):
        return psycopg2.connect(**PG_PARAMS)

    def fetch_all_records(self, limit=10, offset=0, query=""):
        try:
            conn = self.get_conn()
            cur = conn.cursor()

            if query:
                cur.execute(f"SELECT {self.name_column} FROM {self.table_name} WHERE {self.name_column} ILIKE %s ORDER BY {self.name_column}", (f"%{query}%",))
                rows = cur.fetchall()
                total_count = len(rows)
            else:
                cur.execute(f"SELECT COUNT(*) FROM {self.table_name}")
                total_count = cur.fetchone()[0]
                cur.execute(f"SELECT {self.name_column} FROM {self.table_name} ORDER BY {self.name_column} LIMIT %s OFFSET %s", (limit, offset))
                rows = cur.fetchall()
            
            cur.close()
            conn.close()
            records = [row[0] for row in rows]
            return records, total_count
        except Exception as e:
            print(f"Error fetching records from {self.table_name}: {e}")
            return [], 0
            
    def search_records(self, query):
        try:
            conn = self.get_conn()
            cur = conn.cursor()
            cur.execute(f"SELECT {self.name_column} FROM {self.table_name} WHERE {self.name_column} ILIKE %s ORDER BY {self.name_column}", (f"%{query}%",))
            rows = cur.fetchall()
            cur.close()
            conn.close()
            return [row[0] for row in rows]
        except Exception as e:
            print(f"Error searching {self.table_name}: {e}")
            return []

class TruckOwnerManager(BaseTableManager):
    def __init__(self):
        super().__init__("trucks", "truck_num", "truck_num")

    def insert_record(self, truck_number, truck_owner, phone_number):
        try:
            conn = self.get_conn()
            cur = conn.cursor()
            cur.execute("SELECT owner_id FROM truck_owners WHERE owner_name = %s AND phone = %s", (truck_owner, phone_number))
            owner_result = cur.fetchone()
            if owner_result:
                owner_id = owner_result[0]
            else:
                cur.execute("INSERT INTO truck_owners (owner_name, phone) VALUES (%s, %s) RETURNING owner_id", (truck_owner, phone_number))
                owner_id = cur.fetchone()[0]
            cur.execute("SELECT truck_num FROM trucks WHERE truck_num = %s", (truck_number,))
            truck_exists = cur.fetchone()
            if truck_exists:
                raise Exception(f"🚫 رقم الشاحنة '{truck_number}' موجود بالفعل في قاعدة البيانات.")
            cur.execute("INSERT INTO trucks (truck_num, owner_id) VALUES (%s, %s)", (truck_number, owner_id))
            conn.commit()
            cur.close()
            conn.close()
            return {'success': True}
        except Exception as e:
            print(f"Error inserting truck owner and truck: {e}")
            conn.rollback()
            return {'success': False, 'error': str(e)}

    def fetch_all(self, limit=10, offset=0):
        try:
            conn = self.get_conn()
            cur = conn.cursor()
            cur.execute("""
                SELECT t.truck_num, o.owner_name, o.phone
                FROM trucks t
                JOIN truck_owners o ON t.owner_id = o.owner_id
                ORDER BY t.truck_num
                LIMIT %s OFFSET %s
            """, (limit, offset))
            rows = cur.fetchall()
            cur.execute("SELECT COUNT(*) FROM trucks")
            total_count = cur.fetchone()[0]
            cur.close()
            conn.close()
            truck_owners = [{'truck_number': r[0], 'truck_owner': r[1], 'phone_number': r[2]} for r in rows]
            return truck_owners, total_count
        except Exception as e:
            print(f"Error fetching truck owners: {e}")
            return [], 0
            
    def search(self, query):
        try:
            conn = self.get_conn()
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

    def fetch_trucks_with_owners(self):
        try:
            conn = self.get_conn()
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
            return rows
        except Exception as e:
            print(f"Error fetching trucks with owners: {e}")
            return []

    def update_record(self, original_truck_num, new_data):
        try:
            conn = self.get_conn()
            cur = conn.cursor()
            new_truck_num = new_data['new_truck_num']
            new_owner_name = new_data['new_owner_name']
            new_phone = new_data['new_phone']
            cur.execute("SELECT owner_id FROM trucks WHERE truck_num = %s", (original_truck_num,))
            truck_row = cur.fetchone()
            if not truck_row:
                conn.rollback()
                return {'success': False, 'error': 'Truck not found.'}
            owner_id = truck_row[0]
            cur.execute("UPDATE truck_owners SET owner_name = %s, phone = %s WHERE owner_id = %s", (new_owner_name, new_phone, owner_id))
            if original_truck_num != new_truck_num:
                cur.execute("UPDATE trucks SET truck_num = %s WHERE truck_num = %s", (new_truck_num, original_truck_num))
            conn.commit()
            cur.close()
            conn.close()
            return {'success': True}
        except Exception as e:
            print(f"Error updating truck owner: {e}")
            conn.rollback()
            return {'success': False, 'error': str(e)}

class SupplierManager(BaseTableManager):
    def __init__(self):
        super().__init__("suppliers", "supplier_id", "supplier_name")

    def insert_record(self, supplier_name, phone_number):
        try:
            conn = self.get_conn()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO suppliers (supplier_name, phone)
                VALUES (%s, %s)
                ON CONFLICT (supplier_name) DO NOTHING
            """, (supplier_name, phone_number))
            conn.commit()
            cur.close()
            conn.close()
            return True
        except Exception as e:
            print(f"Error inserting supplier: {e}")
            return False

    def fetch_all(self, limit=10, offset=0):
        try:
            conn = self.get_conn()
            cur = conn.cursor()
            cur.execute("SELECT supplier_name, phone FROM suppliers ORDER BY supplier_name LIMIT %s OFFSET %s", (limit, offset))
            rows = cur.fetchall()
            cur.execute("SELECT COUNT(*) FROM suppliers")
            total_count = cur.fetchone()[0]
            cur.close()
            conn.close()
            return [{'supplier_name': r[0], 'phone_number': r[1]} for r in rows], total_count
        except Exception as e:
            print(f"Error fetching suppliers: {e}")
            return [], 0

    def search(self, query):
        try:
            conn = self.get_conn()
            cur = conn.cursor()
            cur.execute("SELECT supplier_name, phone FROM suppliers WHERE supplier_name ILIKE %s OR phone ILIKE %s ORDER BY supplier_name", (f"%{query}%", f"%{query}%"))
            rows = cur.fetchall()
            cur.close()
            conn.close()
            return [{'supplier_name': r[0], 'phone_number': r[1]} for r in rows]
        except Exception as e:
            print(f"Error searching suppliers: {e}")
            return []

class ZoneManager(BaseTableManager):
    def __init__(self):
        super().__init__("zones", "zone_id", "zone_name")

    def insert_record(self, zone_name):
        try:
            conn = self.get_conn()
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
            return result is not None
        except Exception as e:
            print(f"Error inserting zone: {e}")
            return None

class FactoryManager(BaseTableManager):
    def __init__(self):
        super().__init__("factories", "factory_id", "factory_name")

    def insert_record(self, factory_name):
        try:
            conn = self.get_conn()
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM factories WHERE factory_name = %s", (factory_name,))
            if cursor.fetchone():
                return "exists"
            cursor.execute("INSERT INTO factories (factory_name) VALUES (%s)", (factory_name,))
            conn.commit()
            cursor.close()
            conn.close()
            return "inserted"
        except Exception as e:
            print(f"Error inserting factory: {e}")
            return "error"

    def fetch_all(self, page, per_page, query=""):
        conn = self.get_conn()
        cursor = conn.cursor()
        offset = (page - 1) * per_page
        if query:
            cursor.execute("""
                SELECT factory_name
                FROM factories
                WHERE factory_name ILIKE %s
                ORDER BY factory_name ASC
            """, (f"%{query}%",))
            rows = cursor.fetchall()
            total_pages = 1
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
        return factories, total_pages

class RepresentativeManager(BaseTableManager):
    def __init__(self):
        super().__init__("representatives", "representative_id", "representative_name")

    def insert_record(self, representative_name, phone):
        try:
            conn = self.get_conn()
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

    def fetch_all(self, page, per_page, query=""):
        try:
            conn = self.get_conn()
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