-- PostgreSQL Data Seed Script for Water Inventory System
-- Run this after init_db.py has created the tables

-- Clear existing data (optional - comment out if you want to keep existing data)
TRUNCATE TABLE stock_movements, payment_history, wastes, blows, sales, purchases, stocks, items, customers, suppliers, users CASCADE;

------------------------------------------------------------
-- USERS (passwords will be set via init_db.py or seed_users.py)
------------------------------------------------------------
-- Note: Use seed_users.py to create users with fresh password hashes
-- This prevents storing old/corrupted hashes in the database
INSERT INTO users (id, username, email, password_hash, role, created_at)
VALUES
('waheed', 'Waheed', 'waheed@company.com', '', 'admin', NOW()),
('umer', 'Umer', 'umer@company.com', '', 'user', NOW())
ON CONFLICT (id) DO NOTHING;
------------------------------------------------------------
-- SUPPLIERS
------------------------------------------------------------
INSERT INTO suppliers (id, name, contact, address, notes)
VALUES
('Supplier_Alpha', 'Alpha Plastics', '0300-1111111', 'Karachi', 'Main preform supplier'),
('Supplier_Hydro', 'HydroTech Pvt Ltd', '0301-2222222', 'Lahore', 'Blow mold supplier'),
('Supplier_PurePET', 'PurePET Traders', '0321-3333333', 'Faisalabad', 'Grade A preform source')
ON CONFLICT (id) DO NOTHING;

------------------------------------------------------------
-- CUSTOMERS
------------------------------------------------------------
INSERT INTO customers (id, name, contact, address, notes)
VALUES
('Customer_Aqua', 'Aqua Fresh Pvt Ltd', '0344-4444444', 'Lahore', 'Regular buyer'),
('Customer_Crystal', 'Crystal Waters', '0355-5555555', 'Karachi', 'Bulk buyer')
ON CONFLICT (id) DO NOTHING;

------------------------------------------------------------
-- ITEMS
------------------------------------------------------------
INSERT INTO items (id, name, type, size, grade, unit, created_at)
VALUES
('Item_Preform_500A', 'PET Preform 500ml A', 'preform', '500ml', 'A', 'pcs (1000)', NOW()),
('Item_Preform_1500A', 'PET Preform 1500ml A', 'preform', '1500ml', 'A', 'pcs (1000)', NOW()),
('Item_Bottle_500A', '500ml Bottle A', 'bottle', '500ml', 'A', 'pcs (1000)', NOW()),
('Item_Bottle_1500A', '1500ml Bottle A', 'bottle', '1500ml', 'A', 'pcs (1000)', NOW()),
('Item_Sold_500A', 'Sold 500ml Bottle A', 'sold', '500ml', 'A', 'pcs (1000)', NOW())
ON CONFLICT (id) DO NOTHING;

------------------------------------------------------------
-- STOCKS
------------------------------------------------------------
INSERT INTO stocks (item_id, quantity, last_updated)
VALUES
('Item_Preform_500A', 2000, NOW()),
('Item_Preform_1500A', 1000, NOW()),
('Item_Bottle_500A', 800, NOW()),
('Item_Bottle_1500A', 400, NOW()),
('Item_Sold_500A', 0, NOW())
ON CONFLICT (item_id) DO UPDATE SET 
    quantity = EXCLUDED.quantity,
    last_updated = EXCLUDED.last_updated;

------------------------------------------------------------
-- PURCHASES
------------------------------------------------------------
INSERT INTO purchases (bill_number, supplier_id, item_id, quantity, unit_price, total_amount, status, payment_status, paid_amount, created_by, date)
VALUES
('BILL-001', 'Supplier_Alpha', 'Item_Bottle_500A', 1000, 30.00, 30000.00, 'paid', 'paid', 30000.00, 'waheed', NOW() - INTERVAL '10 days'),
('BILL-002', 'Supplier_Hydro', 'Item_Bottle_1500A', 500, 32.00, 16000.00, 'pending', 'partial', 8000.00, 'umer', NOW() - INTERVAL '5 days')
ON CONFLICT (bill_number) DO NOTHING;

------------------------------------------------------------
-- SALES
------------------------------------------------------------
INSERT INTO sales (bill_number, customer_id, item_id, quantity, unit_price, total_price, cost_basis, status, payment_status, paid_amount, editable_by_admin_only, created_by, date)
VALUES
('SALE-001', 'Customer_Aqua', 'Item_Bottle_500A', 1000, 30.00, 30000.00, 30.00, 'confirmed', 'paid', 30000.00, FALSE, 'umer', NOW() - INTERVAL '7 days'),
('SALE-002', 'Customer_Crystal', 'Item_Bottle_1500A', 500, 32.00, 16000.00, 32.00, 'confirmed', 'partial', 8000.00, FALSE, 'waheed', NOW() - INTERVAL '3 days')
ON CONFLICT (bill_number) DO NOTHING;

------------------------------------------------------------
-- BLOWS
------------------------------------------------------------
INSERT INTO blows (id, user_id, from_item_id, to_item_id, quantity, blow_cost_per_unit, input_quantity, output_quantity, waste_quantity, efficiency_rate, notes, date_time)
VALUES
('BLOW-001', 'umer', 'Item_Preform_500A', 'Item_Bottle_500A', 800, 2.00, 850, 800, 50, 94.12, 'Regular production', NOW() - INTERVAL '8 days'),
('BLOW-002', 'waheed', 'Item_Preform_1500A', 'Item_Bottle_1500A', 400, 3.00, 420, 400, 20, 95.24, 'Batch 2 blowing', NOW() - INTERVAL '4 days')
ON CONFLICT (id) DO NOTHING;

------------------------------------------------------------
-- WASTES
------------------------------------------------------------
INSERT INTO wastes (id, user_id, item_id, quantity, price_per_unit, total_price, notes, date)
VALUES
('WASTE-001', 'umer', 'Item_Bottle_500A', 20, 5.00, 100.00, 'Faulty bottles', NOW() - INTERVAL '6 days'),
('WASTE-002', 'waheed', 'Item_Preform_500A', 30, 3.00, 90.00, 'Damaged preforms', NOW() - INTERVAL '2 days')
ON CONFLICT (id) DO NOTHING;

------------------------------------------------------------
-- STOCK MOVEMENTS (ledger)
------------------------------------------------------------
INSERT INTO stock_movements (item_id, movement_type, quantity_change, reference_id, before_quantity, after_quantity, recorded_by, movement_date, notes)
VALUES
('Item_Preform_500A', 'purchase', 1000, 'BILL-001', 1000, 2000, 'waheed', NOW() - INTERVAL '10 days', 'Purchase from Alpha'),
('Item_Preform_500A', 'production', -850, 'BLOW-001', 2000, 1150, 'umer', NOW() - INTERVAL '8 days', 'Used in blow process'),
('Item_Bottle_500A', 'production', 800, 'BLOW-001', 0, 800, 'umer', NOW() - INTERVAL '8 days', 'Produced from preforms'),
('Item_Sold_500A', 'sale', -1000, 'SALE-001', 1000, 0, 'umer', NOW() - INTERVAL '7 days', 'Sold to Aqua'),
('Item_Preform_1500A', 'purchase', 500, 'BILL-002', 500, 1000, 'umer', NOW() - INTERVAL '5 days', 'Purchase from Hydro'),
('Item_Preform_1500A', 'production', -420, 'BLOW-002', 1000, 580, 'waheed', NOW() - INTERVAL '4 days', 'Used in blow process'),
('Item_Bottle_1500A', 'production', 400, 'BLOW-002', 0, 400, 'waheed', NOW() - INTERVAL '4 days', 'Produced from preforms')

------------------------------------------------------------
-- PAYMENT HISTORY
------------------------------------------------------------
INSERT INTO payment_history (bill_number, bill_type, paid_by, amount, paid_on, notes)
VALUES
('BILL-001', 'purchase', 'waheed', 20000.00, NOW() - INTERVAL '10 days', 'Full payment for Alpha'),
('BILL-002', 'purchase', 'umer', 5000.00, NOW() - INTERVAL '5 days', 'Partial payment for Hydro'),
('SALE-001', 'sale', 'umer', 30000.00, NOW() - INTERVAL '7 days', 'Full payment from Aqua'),
('SALE-002', 'sale', 'waheed', 8000.00, NOW() - INTERVAL '3 days', 'Partial payment received from Crystal');

-- Display summary
SELECT 'Database seeded successfully!' AS status;
SELECT COUNT(*) AS users_count FROM users;
SELECT COUNT(*) AS suppliers_count FROM suppliers;
SELECT COUNT(*) AS customers_count FROM customers;
SELECT COUNT(*) AS items_count FROM items;
SELECT COUNT(*) AS purchases_count FROM purchases;
SELECT COUNT(*) AS sales_count FROM sales;
SELECT COUNT(*) AS stock_movements_count FROM stock_movements;
