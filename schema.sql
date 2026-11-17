CREATE TABLE IF NOT EXISTS warehouses (
 warehouse_id SERIAL PRIMARY KEY, warehouse_name VARCHAR(100) UNIQUE NOT NULL
);
CREATE TABLE IF NOT EXISTS items (
 item_id SERIAL PRIMARY KEY, item_name VARCHAR(150) UNIQUE NOT NULL
);
CREATE TABLE IF NOT EXISTS warehouse_stock (
 warehouse_id INT REFERENCES warehouses(warehouse_id),
 item_id INT REFERENCES items(item_id),
 quantity INT NOT NULL DEFAULT 0 CHECK (quantity >= 0),
 PRIMARY KEY (warehouse_id, item_id)
);
CREATE TABLE IF NOT EXISTS stock_transfers (
 transfer_id SERIAL PRIMARY KEY,
 item_id INT REFERENCES items(item_id),
 source_warehouse_id INT REFERENCES warehouses(warehouse_id),
 destination_warehouse_id INT REFERENCES warehouses(warehouse_id),
 quantity INT NOT NULL CHECK (quantity > 0),
 transferred_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
 CHECK (source_warehouse_id <> destination_warehouse_id)
);

INSERT INTO warehouses (warehouse_name) VALUES
('Main Warehouse'), ('Branch Warehouse')
ON CONFLICT (warehouse_name) DO NOTHING;
INSERT INTO items (item_name) VALUES ('Database Textbook')
ON CONFLICT (item_name) DO NOTHING;
INSERT INTO warehouse_stock (warehouse_id, item_id, quantity)
SELECT w.warehouse_id, i.item_id,
 CASE WHEN w.warehouse_name = 'Main Warehouse' THEN 50 ELSE 10 END
FROM warehouses w CROSS JOIN items i
ON CONFLICT (warehouse_id, item_id) DO NOTHING;
