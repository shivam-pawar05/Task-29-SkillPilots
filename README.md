# Warehouse Stock Transfer (Python + PostgreSQL)

This project transfers stock between warehouses using a PostgreSQL transaction.

## Setup
1. Create a PostgreSQL database named `bookstore_inventory`.
2. Run the schema:
   `psql -U postgres -d bookstore_inventory -f sql/schema.sql`
3. Install dependencies:
   `pip install -r requirements.txt`
4. Copy `.env.example` to `.env` and enter your PostgreSQL password.

## Run
`python transfer_stock.py --item 1 --source 1 --destination 2 --quantity 5`

## Verify
Run `sql/verification.sql` in pgAdmin or psql.

The script disables autocommit, checks source stock, updates both warehouses,
records the transfer, and commits. Any error causes a rollback.
