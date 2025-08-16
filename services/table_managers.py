import psycopg2
from db import PG_PARAMS

class BaseTable:
    def __init__(self, table_name, id_column, name_column, phone_column=None):
        self.table_name = table_name
        self.id_column = id_column
        self.name_column = name_column
        self.phone_column = phone_column

    def get_conn(self):
        return psycopg2.connect(**PG_PARAMS)

    def fetch_all(self, limit=10, offset=0):
        try:
            conn = self.get_conn()
            cur = conn.cursor()
            
            columns = [self.name_column]
            if self.phone_column:
                columns.append(self.phone_column)

            cur.execute(f"""
                SELECT {', '.join(columns)}
                FROM {self.table_name}
                ORDER BY {self.name_column}
                LIMIT %s OFFSET %s
            """, (limit, offset))
            rows = cur.fetchall()
            
            cur.execute(f"SELECT COUNT(*) FROM {self.table_name}")
            total_count = cur.fetchone()[0]
            
            cur.close()
            conn.close()
            
            if self.phone_column:
                result = [{self.name_column: r[0], self.phone_column: r[1]} for r in rows]
            else:
                result = [{self.name_column: r[0]} for r in rows]

            return result, total_count
        except Exception as e:
            print(f"Error fetching records: {e}")
            return [], 0
            
    def search(self, query):
        try:
            conn = self.get_conn()
            cur = conn.cursor()
            
            select_columns = [self.name_column]
            if self.phone_column:
                select_columns.append(self.phone_column)
            
            conditions = [f"{self.name_column} ILIKE %s"]
            params = [f"%{query}%"]
            
            if self.phone_column:
                conditions.append(f"{self.phone_column} ILIKE %s")
                params.append(f"%{query}%")
                
            cur.execute(f"""
                SELECT {', '.join(select_columns)}
                FROM {self.table_name}
                WHERE {' OR '.join(conditions)}
                ORDER BY {self.name_column}
            """, tuple(params))
            
            rows = cur.fetchall()
            cur.close()
            conn.close()

            if self.phone_column:
                return [{self.name_column: r[0], self.phone_column: r[1]} for r in rows]
            else:
                return [{self.name_column: r[0]} for r in rows]
        
        except Exception as e:
            print(f"Error searching records: {e}")
            return []
            
    def delete_record(self, name_value):
        try:
            conn = self.get_conn()
            cur = conn.cursor()
            cur.execute(f"DELETE FROM {self.table_name} WHERE {self.name_column} = %s", (name_value,))
            deleted_rows = cur.rowcount
            conn.commit()
            cur.close()
            conn.close()
            return {'success': deleted_rows > 0}
        except Exception as e:
            print(f"Error deleting record: {e}")
            if 'conn' in locals():
                conn.rollback()
            return {'success': False, 'error': str(e)}

    def insert_record(self, name_value, phone_value=None):
        try:
            conn = self.get_conn()
            cur = conn.cursor()
            
            if self.phone_column and phone_value is not None:
                cur.execute(f"""
                    INSERT INTO {self.table_name} ({self.name_column}, {self.phone_column})
                    VALUES (%s, %s)
                    ON CONFLICT ({self.name_column}) DO NOTHING
                    RETURNING {self.name_column};
                """, (name_value, phone_value))
            else:
                cur.execute(f"""
                    INSERT INTO {self.table_name} ({self.name_column})
                    VALUES (%s)
                    ON CONFLICT ({self.name_column}) DO NOTHING
                    RETURNING {self.name_column};
                """, (name_value,))
                
            result = cur.fetchone()
            conn.commit()
            cur.close()
            conn.close()
            
            return "inserted" if result else "exists"
            
        except Exception as e:
            print(f"Error inserting record: {e}")
            if 'conn' in locals() and conn:
                conn.rollback()
            return "error"
            
    def update_record(self, original_name, new_data):
        try:
            conn = self.get_conn()
            cur = conn.cursor()
            
            set_clauses = []
            params = []
            
            if f'new_{self.name_column}' in new_data:
                set_clauses.append(f"{self.name_column} = %s")
                params.append(new_data[f'new_{self.name_column}'])
            
            if self.phone_column and 'new_phone' in new_data:
                set_clauses.append(f"{self.phone_column} = %s")
                params.append(new_data['new_phone'])
                
            params.append(original_name)
            
            query = f"UPDATE {self.table_name} SET {', '.join(set_clauses)} WHERE {self.name_column} = %s"
            
            cur.execute(query, tuple(params))
            
            updated_rows = cur.rowcount
            conn.commit()
            cur.close()
            conn.close()
            
            return {'success': updated_rows > 0}
            
        except Exception as e:
            print(f"Error updating record: {e}")
            if 'conn' in locals() and conn:
                conn.rollback()
            return {'success': False, 'error': str(e)}

class SupplierManager(BaseTable):
    def __init__(self):
        super().__init__("suppliers", "supplier_id", "supplier_name", "phone")

class RepresentativeManager(BaseTable):
    def __init__(self):
        super().__init__("representatives", "representative_id", "representative_name", "phone")

class ZoneManager(BaseTable):
    def __init__(self):
        super().__init__("zones", "zone_id", "zone_name")

class FactoryManager(BaseTable):
    def __init__(self):
        super().__init__("factories", "factory_id", "factory_name")

# TruckOwnerManager handles truck owners and their associated trucks
class TruckOwnerManager(BaseTable):
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
            new_truck_num = new_data.get('new_truck_num')
            new_owner_name = new_data.get('new_owner_name')
            new_phone = new_data.get('new_phone')
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
            if 'conn' in locals() and conn:
                conn.rollback()
            return {'success': False, 'error': str(e)}
