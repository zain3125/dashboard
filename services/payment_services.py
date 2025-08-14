import psycopg2
from psycopg2.extras import RealDictCursor
from db import PG_PARAMS

def get_supplier_payments(search=None):
    query = """
        SELECT sp.*, s.supplier_name
        FROM suppliers_payment sp
        JOIN suppliers s ON sp.supplier_id = s.supplier_id
    """
    params = []
    if search:
        query += " WHERE s.supplier_name ILIKE %s"
        params.append(f"%{search}%")

    query += " ORDER BY sp.supplier_transaction_id DESC"
    with psycopg2.connect(**PG_PARAMS) as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, params)
            return cur.fetchall()

def add_supplier_payment(date_id, supplier_id, amount, transfer_fees, payment_method, notes):
    query = """
        INSERT INTO suppliers_payment (date_id, supplier_id, amount, transfer_fees, payment_method, notes)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    with psycopg2.connect(**PG_PARAMS) as conn:
        with conn.cursor() as cur:
            cur.execute(query, (date_id, supplier_id, amount, transfer_fees, payment_method, notes))
            conn.commit()

def get_truck_owner_payments(search=None):
    query = """
        SELECT tp.*, t.owner_name
        FROM truck_owners_payment tp
        JOIN truck_owners t ON tp.owner_id = t.owner_id
    """
    params = []
    if search:
        query += " WHERE t.owner_name ILIKE %s"
        params.append(f"%{search}%")

    query += " ORDER BY tp.truck_owner_transaction_id DESC"
    with psycopg2.connect(**PG_PARAMS) as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, params)
            return cur.fetchall()


def add_truck_owner_payment(date_id, owner_id, amount, transfer_fees, payment_method, notes):
    query = """
        INSERT INTO truck_owners_payment (date_id, owner_id, amount, transfer_fees, payment_method, notes)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    with psycopg2.connect(**PG_PARAMS) as conn:
        with conn.cursor() as cur:
            cur.execute(query, (date_id, owner_id, amount, transfer_fees, payment_method, notes))
            conn.commit()

def update_supplier_payment(supplier_transaction_id, amount, transfer_fees, payment_method, notes):
    query = """
        UPDATE suppliers_payment
        SET amount = %s,
            transfer_fees = %s,
            payment_method = %s,
            notes = %s
        WHERE supplier_transaction_id = %s
    """
    with psycopg2.connect(**PG_PARAMS) as conn:
        with conn.cursor() as cur:
            cur.execute(query, (amount, transfer_fees, payment_method, notes, supplier_transaction_id))
            conn.commit()

def delete_supplier_payment(supplier_transaction_id):
    query = "DELETE FROM suppliers_payment WHERE supplier_transaction_id = %s"
    with psycopg2.connect(**PG_PARAMS) as conn:
        with conn.cursor() as cur:
            cur.execute(query, (supplier_transaction_id,))
            conn.commit()


def update_truck_owner_payment(truck_owner_transaction_id, amount, transfer_fees, payment_method, notes):
    query = """
        UPDATE truck_owners_payment
        SET amount = %s,
            transfer_fees = %s,
            payment_method = %s,
            notes = %s
        WHERE truck_owner_transaction_id = %s
    """
    with psycopg2.connect(**PG_PARAMS) as conn:
        with conn.cursor() as cur:
            cur.execute(query, (amount, transfer_fees, payment_method, notes, truck_owner_transaction_id))
            conn.commit()

def delete_truck_owner_payment(truck_owner_transaction_id):
    query = "DELETE FROM truck_owners_payment WHERE truck_owner_transaction_id = %s"
    with psycopg2.connect(**PG_PARAMS) as conn:
        with conn.cursor() as cur:
            cur.execute(query, (truck_owner_transaction_id,))
            conn.commit()