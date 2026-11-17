import argparse
import os
import sys
import psycopg2
from dotenv import load_dotenv

def connect_db():
    load_dotenv()
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "bookstore_inventory"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "")
    )

def transfer_stock(item_id, source_id, destination_id, quantity):
    if quantity <= 0:
        raise ValueError("Quantity must be greater than zero.")
    if source_id == destination_id:
        raise ValueError("Source and destination must be different.")

    conn = None
    try:
        conn = connect_db()
        conn.autocommit = False  # Transaction is controlled manually.

        with conn.cursor() as cur:
            # Lock source stock while checking it.
            cur.execute("""
                SELECT quantity FROM warehouse_stock
                WHERE warehouse_id=%s AND item_id=%s FOR UPDATE
            """, (source_id, item_id))
            row = cur.fetchone()

            if row is None:
                raise ValueError("Source stock record was not found.")
            if row[0] < quantity:
                raise ValueError(f"Insufficient stock. Available: {row[0]}")

            # Decrement source warehouse.
            cur.execute("""
                UPDATE warehouse_stock SET quantity=quantity-%s
                WHERE warehouse_id=%s AND item_id=%s
            """, (quantity, source_id, item_id))

            # Increment destination warehouse (insert row if missing).
            cur.execute("""
                INSERT INTO warehouse_stock (warehouse_id, item_id, quantity)
                VALUES (%s, %s, %s)
                ON CONFLICT (warehouse_id, item_id)
                DO UPDATE SET quantity=warehouse_stock.quantity + EXCLUDED.quantity
            """, (destination_id, item_id, quantity))

            # Record transfer in the same transaction.
            cur.execute("""
                INSERT INTO stock_transfers
                (item_id, source_warehouse_id, destination_warehouse_id, quantity)
                VALUES (%s, %s, %s, %s) RETURNING transfer_id
            """, (item_id, source_id, destination_id, quantity))
            transfer_id = cur.fetchone()[0]

        conn.commit()
        print(f"Transfer successful. Transfer ID: {transfer_id}")
        print(f"Transferred {quantity} unit(s) of item {item_id}.")
    except Exception:
        if conn is not None:
            conn.rollback()
        raise
    finally:
        if conn is not None:
            conn.close()

def main():
    parser = argparse.ArgumentParser(description="Transfer stock between warehouses")
    parser.add_argument("--item", type=int, required=True)
    parser.add_argument("--source", type=int, required=True)
    parser.add_argument("--destination", type=int, required=True)
    parser.add_argument("--quantity", type=int, required=True)
    args = parser.parse_args()
    try:
        transfer_stock(args.item, args.source, args.destination, args.quantity)
    except (ValueError, psycopg2.Error) as exc:
        print(f"Transfer failed: {exc}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
