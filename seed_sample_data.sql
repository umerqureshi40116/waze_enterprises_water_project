-- ============================================================================
-- SAMPLE DATA FOR WATER BOTTLE INVENTORY SYSTEM
-- ============================================================================
-- Insert 30 sample entries for: Suppliers, Purchases, Blow, Waste
-- This SQL can be run directly in Neon database console
-- ============================================================================

-- ============================================================================
-- 1. SUPPLIERS (30 entries)
-- ============================================================================
INSERT INTO suppliers (id, name) VALUES
('SUP001', 'Premier Packaging Ltd'),
('SUP002', 'Eco Supplies Co'),
('SUP003', 'Green Plastics Inc'),
('SUP004', 'National Packaging'),
('SUP005', 'Global Materials'),
('SUP006', 'Quality Caps Ltd'),
('SUP007', 'Premium Labels Co'),
('SUP008', 'Standard Supplies'),
('SUP009', 'Bulk Materials Ltd'),
('SUP010', 'Fast Delivery Supplies'),
('SUP011', 'Sustainable Packaging'),
('SUP012', 'Tech Packaging'),
('SUP013', 'Local Supplies Hub'),
('SUP014', 'Industrial Materials'),
('SUP015', 'Retail Packaging'),
('SUP016', 'Express Packaging'),
('SUP017', 'Premium Plastics'),
('SUP018', 'Budget Supplies'),
('SUP019', 'Wholesale Center'),
('SUP020', 'Direct Import'),
('SUP021', 'Valley Supplies'),
('SUP022', 'Coast Materials'),
('SUP023', 'Urban Packaging'),
('SUP024', 'Rural Distributors'),
('SUP025', 'Metro Supplies'),
('SUP026', 'Pioneer Materials'),
('SUP027', 'Swift Logistics'),
('SUP028', 'Precision Parts'),
('SUP029', 'Reliable Supply'),
('SUP030', 'Future Materials');

-- ============================================================================
-- 2. PURCHASES (30 entries - main purchase bills)
-- ============================================================================
INSERT INTO purchases (bill_number, supplier_id, total_amount, status, payment_status, paid_amount, due_date, date, notes) VALUES
('PUR001', 'SUP001', 42500.00, 'completed', 'paid', 42500.00, '2025-11-15', '2025-11-01', 'Initial purchase of preforms'),
('PUR002', 'SUP002', 26250.00, 'completed', 'paid', 26250.00, '2025-11-16', '2025-11-02', 'Secondary batch'),
('PUR003', 'SUP003', 34400.00, 'completed', 'paid', 34400.00, '2025-11-17', '2025-11-03', 'Alternative supplier test'),
('PUR004', 'SUP004', 30000.00, 'completed', 'paid', 30000.00, '2025-11-18', '2025-11-04', 'Cap purchase'),
('PUR005', 'SUP005', 12500.00, 'completed', 'paid', 12500.00, '2025-11-19', '2025-11-05', 'Label and sticker purchase'),
('PUR006', 'SUP006', 50400.00, 'completed', 'paid', 50400.00, '2025-11-20', '2025-11-06', 'Bulk preform order'),
('PUR007', 'SUP007', 23250.00, 'completed', 'paid', 23250.00, '2025-11-21', '2025-11-07', 'Additional caps'),
('PUR008', 'SUP008', 47575.00, 'completed', 'paid', 47575.00, '2025-11-22', '2025-11-08', 'Regular order'),
('PUR009', 'SUP009', 9600.00, 'completed', 'paid', 9600.00, '2025-11-23', '2025-11-09', 'Label reorder'),
('PUR010', 'SUP010', 29600.00, 'completed', 'paid', 29600.00, '2025-11-24', '2025-11-10', 'Premium caps'),
('PUR011', 'SUP011', 38475.00, 'completed', 'paid', 38475.00, '2025-11-25', '2025-11-11', 'Weekly preform delivery'),
('PUR012', 'SUP012', 15300.00, 'completed', 'paid', 15300.00, '2025-11-26', '2025-11-12', 'Labels for special edition'),
('PUR013', 'SUP013', 30450.00, 'completed', 'paid', 30450.00, '2025-11-27', '2025-11-13', 'Mid-month order'),
('PUR014', 'SUP014', 27360.00, 'completed', 'paid', 27360.00, '2025-11-28', '2025-11-14', 'Standard caps'),
('PUR015', 'SUP015', 42500.00, 'completed', 'paid', 42500.00, '2025-11-29', '2025-11-15', 'Regular supply'),
('PUR016', 'SUP016', 58100.00, 'completed', 'paid', 58100.00, '2025-11-30', '2025-11-16', 'Bulk discount order'),
('PUR017', 'SUP017', 13000.00, 'completed', 'paid', 13000.00, '2025-12-01', '2025-11-17', 'Label restock'),
('PUR018', 'SUP018', 33660.00, 'completed', 'paid', 33660.00, '2025-12-02', '2025-11-18', 'Cap replenishment'),
('PUR019', 'SUP019', 40560.00, 'completed', 'paid', 40560.00, '2025-12-03', '2025-11-19', 'Weekly supply'),
('PUR020', 'SUP020', 23840.00, 'completed', 'paid', 23840.00, '2025-12-04', '2025-11-20', 'Express delivery'),
('PUR021', 'SUP021', 44720.00, 'completed', 'paid', 44720.00, '2025-12-05', '2025-11-21', 'Regular batch'),
('PUR022', 'SUP022', 12160.00, 'completed', 'paid', 12160.00, '2025-12-06', '2025-11-22', 'Label update'),
('PUR023', 'SUP023', 34600.00, 'completed', 'paid', 34600.00, '2025-12-07', '2025-11-23', 'Mid-week order'),
('PUR024', 'SUP024', 21560.00, 'completed', 'paid', 21560.00, '2025-12-08', '2025-11-24', 'Sustainable caps'),
('PUR025', 'SUP025', 47025.00, 'completed', 'paid', 47025.00, '2025-12-09', '2025-11-25', 'Quality batch'),
('PUR026', 'SUP026', 14835.00, 'completed', 'paid', 14835.00, '2025-12-10', '2025-11-26', 'Label emergency order'),
('PUR027', 'SUP027', 31710.00, 'completed', 'paid', 31710.00, '2025-12-11', '2025-11-27', 'Cap shortage'),
('PUR028', 'SUP028', 36540.00, 'completed', 'paid', 36540.00, '2025-12-12', '2025-11-28', 'Tech materials'),
('PUR029', 'SUP029', 16965.00, 'completed', 'paid', 16965.00, '2025-12-13', '2025-11-29', 'Label batch'),
('PUR030', 'SUP030', 48720.00, 'completed', 'paid', 48720.00, '2025-12-14', '2025-11-30', 'Month-end order');

-- ============================================================================
-- 2B. PURCHASE LINE ITEMS (30 entries - detailed items per purchase bill)
-- ============================================================================
INSERT INTO purchase_line_items (bill_number, item_id, quantity, unit_price, cost_basis) VALUES
('PUR001', 1, 5000, 8.50, 8.50),
('PUR002', 1, 3000, 8.75, 8.75),
('PUR003', 1, 4000, 8.60, 8.60),
('PUR004', 2, 2000, 15.00, 15.00),
('PUR005', 3, 1000, 12.50, 12.50),
('PUR006', 1, 6000, 8.40, 8.40),
('PUR007', 2, 1500, 15.50, 15.50),
('PUR008', 1, 5500, 8.65, 8.65),
('PUR009', 3, 800, 12.00, 12.00),
('PUR010', 2, 2000, 14.80, 14.80),
('PUR011', 1, 4500, 8.55, 8.55),
('PUR012', 3, 1200, 12.75, 12.75),
('PUR013', 1, 3500, 8.70, 8.70),
('PUR014', 2, 1800, 15.20, 15.20),
('PUR015', 1, 5000, 8.50, 8.50),
('PUR016', 1, 7000, 8.30, 8.30),
('PUR017', 3, 1000, 13.00, 13.00),
('PUR018', 2, 2200, 15.30, 15.30),
('PUR019', 1, 4800, 8.45, 8.45),
('PUR020', 2, 1600, 14.90, 14.90),
('PUR021', 1, 5200, 8.60, 8.60),
('PUR022', 3, 950, 12.80, 12.80),
('PUR023', 1, 4000, 8.65, 8.65),
('PUR024', 2, 1400, 15.40, 15.40),
('PUR025', 1, 5500, 8.55, 8.55),
('PUR026', 3, 1150, 12.90, 12.90),
('PUR027', 2, 2100, 15.10, 15.10),
('PUR028', 1, 4200, 8.70, 8.70),
('PUR029', 3, 1300, 13.05, 13.05),
('PUR030', 1, 5800, 8.40, 8.40);

-- ============================================================================
-- 3. BLOW PROCESS (30 entries - converting preforms to finished bottles)
-- ============================================================================
INSERT INTO blows (date_time, from_item_id, to_item_id, quantity, blow_cost_per_unit, produced_unit_cost, notes) VALUES
('2025-11-01 08:00:00', 1, 4, 1000, 2.50, 11.00, 'Morning batch - 500ml bottles'),
('2025-11-01 14:00:00', 1, 4, 800, 2.50, 11.00, 'Afternoon batch'),
('2025-11-02 08:30:00', 1, 4, 1200, 2.50, 11.00, 'High volume day'),
('2025-11-02 15:00:00', 1, 5, 600, 2.60, 11.50, 'Switch to 1L bottles'),
('2025-11-03 09:00:00', 1, 4, 950, 2.50, 11.00, 'Regular production'),
('2025-11-03 16:00:00', 1, 5, 700, 2.60, 11.50, '1L production'),
('2025-11-04 08:00:00', 1, 4, 1100, 2.50, 11.00, 'Morning run'),
('2025-11-04 13:30:00', 1, 5, 550, 2.60, 11.50, 'Afternoon mix'),
('2025-11-05 09:15:00', 1, 4, 1050, 2.50, 11.00, 'Tuesday production'),
('2025-11-05 15:30:00', 1, 5, 680, 2.60, 11.50, 'Mixed production'),
('2025-11-06 08:00:00', 1, 4, 1300, 2.50, 11.00, 'High demand day'),
('2025-11-06 14:00:00', 1, 5, 750, 2.60, 11.50, 'Peak production'),
('2025-11-07 09:00:00', 1, 4, 900, 2.50, 11.00, 'Weekly start'),
('2025-11-07 16:00:00', 1, 5, 620, 2.60, 11.50, 'Evening batch'),
('2025-11-08 08:30:00', 1, 4, 1080, 2.50, 11.00, 'Consistent output'),
('2025-11-08 15:00:00', 1, 5, 700, 2.60, 11.50, 'Standard batch'),
('2025-11-09 09:00:00', 1, 4, 1150, 2.50, 11.00, 'Thursday production'),
('2025-11-09 14:30:00', 1, 5, 580, 2.60, 11.50, 'Mixed sizes'),
('2025-11-10 08:00:00', 1, 4, 1200, 2.50, 11.00, 'Friday peak'),
('2025-11-10 15:00:00', 1, 5, 800, 2.60, 11.50, 'High volume'),
('2025-11-11 08:15:00', 1, 4, 950, 2.50, 11.00, 'Monday restart'),
('2025-11-11 14:45:00', 1, 5, 650, 2.60, 11.50, 'Afternoon batch'),
('2025-11-12 09:00:00', 1, 4, 1100, 2.50, 11.00, 'Regular day'),
('2025-11-12 16:00:00', 1, 5, 720, 2.60, 11.50, 'Evening production'),
('2025-11-13 08:30:00', 1, 4, 1050, 2.50, 11.00, 'Stable output'),
('2025-11-13 15:15:00', 1, 5, 690, 2.60, 11.50, 'Consistent batch'),
('2025-11-14 09:00:00', 1, 4, 1180, 2.50, 11.00, 'Thursday volume'),
('2025-11-14 14:30:00', 1, 5, 610, 2.60, 11.50, 'Afternoon run'),
('2025-11-15 08:00:00', 1, 4, 1220, 2.50, 11.00, 'Friday finish'),
('2025-11-15 15:00:00', 1, 5, 780, 2.60, 11.50, 'Week end rush');

-- ============================================================================
-- 4. WASTE/DEFECTS (30 entries)
-- ============================================================================
INSERT INTO wastes (item_id, quantity, reason, date_time, notes) VALUES
(1, 45, 'Damaged preforms in shipment', '2025-11-01 10:00:00', 'Supplier quality issue'),
(4, 12, 'Defective bottles - air leak', '2025-11-01 11:30:00', 'Quality control rejection'),
(1, 30, 'Preform storage damage', '2025-11-02 09:00:00', 'Environmental exposure'),
(5, 8, 'Bottle cracks after blow', '2025-11-02 15:45:00', 'Production defect'),
(2, 20, 'Caps misalignment', '2025-11-03 08:15:00', 'Equipment calibration needed'),
(4, 15, 'Incomplete bottles', '2025-11-03 14:00:00', 'Blow pressure issue'),
(1, 35, 'Preform contamination', '2025-11-04 09:30:00', 'Storage condition'),
(5, 10, 'Bottle thickness issue', '2025-11-04 16:00:00', 'Mold problem'),
(3, 25, 'Label defects', '2025-11-05 10:00:00', 'Print quality issue'),
(4, 18, 'Bottle deformation', '2025-11-05 13:00:00', 'Cooling issue'),
(1, 40, 'Preform discoloration', '2025-11-06 08:00:00', 'Material batch issue'),
(2, 22, 'Cap defects', '2025-11-06 14:30:00', 'Manufacturing defect'),
(5, 14, 'Bottle leakage', '2025-11-07 09:00:00', 'Seal problem'),
(4, 16, 'Surface scratches', '2025-11-07 15:00:00', 'Handling damage'),
(1, 38, 'Preform shrinkage', '2025-11-08 10:15:00', 'Temperature control'),
(3, 28, 'Label peeling', '2025-11-08 14:00:00', 'Adhesive failure'),
(4, 20, 'Bottle shape deviation', '2025-11-09 08:30:00', 'Mold wear'),
(5, 11, 'Cap looseness', '2025-11-09 15:30:00', 'Thread issue'),
(2, 19, 'Cap color variation', '2025-11-10 09:00:00', 'Batch inconsistency'),
(1, 42, 'Preform brittleness', '2025-11-10 13:00:00', 'Material quality'),
(4, 17, 'Bottle clarity loss', '2025-11-11 10:00:00', 'Blow temperature'),
(5, 13, 'Bottle size variance', '2025-11-11 14:45:00', 'Calibration drift'),
(3, 26, 'Label misalignment', '2025-11-12 08:15:00', 'Applicator issue'),
(1, 36, 'Preform oxidation', '2025-11-12 15:00:00', 'Storage oxidation'),
(4, 21, 'Bottle neck defect', '2025-11-13 09:30:00', 'Mold damage'),
(2, 23, 'Cap threading issue', '2025-11-13 14:00:00', 'Injection defect'),
(5, 15, 'Bottle draft angle issue', '2025-11-14 08:00:00', 'Ejection problem'),
(3, 30, 'Label ink smudge', '2025-11-14 15:15:00', 'Printing error'),
(1, 44, 'Preform moisture absorption', '2025-11-15 09:00:00', 'Humidity issue'),
(4, 19, 'Bottle dimensional variation', '2025-11-15 16:00:00', 'Measurement drift');

-- ============================================================================
-- SUMMARY
-- ============================================================================
-- Total records inserted:
-- - Suppliers: 30
-- - Purchases: 30
-- - Blows: 30
-- - Wastes: 30
-- TOTAL: 120 entries
--
-- Next steps:
-- 1. Run this SQL in Neon console
-- 2. Data will automatically populate related tables via foreign keys
-- 3. Refresh the app to see sample data in dashboards and reports
-- ============================================================================
