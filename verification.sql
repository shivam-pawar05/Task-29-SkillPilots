SELECT w.warehouse_name, i.item_name, s.quantity
FROM warehouse_stock s
JOIN warehouses w USING (warehouse_id)
JOIN items i USING (item_id)
ORDER BY i.item_id, w.warehouse_id;

SELECT * FROM stock_transfers ORDER BY transfer_id DESC;
