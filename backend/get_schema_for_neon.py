from sqlalchemy import inspect, text
from app.db.database import engine

# Get the schema
inspector = inspect(engine)
columns = inspector.get_columns('extra_expenditures')

print("=" * 80)
print("NEON DATABASE SCHEMA - EXTRA EXPENDITURES TABLE")
print("=" * 80)
print("\n📋 SCHEMA DETAILS:")
print("-" * 80)

for col in columns:
    col_name = col['name']
    col_type = col['type']
    nullable = col['nullable']
    
    print(f"{col_name:20} {str(col_type):30} {'NULL' if nullable else 'NOT NULL'}")

print("\n" + "=" * 80)
print("SQL QUERIES TO RUN ON NEON:")
print("=" * 80)

print("""
-- Step 1: Drop extra_expenditures if it exists (optional, be careful!)
-- DROP TABLE IF EXISTS extra_expenditures;

-- Step 2: Create the table with correct schema
CREATE TABLE IF NOT EXISTS extra_expenditures (
    id VARCHAR NOT NULL,
    expense_type VARCHAR NOT NULL,
    description TEXT,
    amount NUMERIC(12, 2) NOT NULL,
    date DATE NOT NULL,
    notes TEXT,
    created_by VARCHAR,
    created_at TIMESTAMP,
    PRIMARY KEY (id)
);

-- Step 3: Verify the table was created correctly
SELECT * FROM extra_expenditures LIMIT 1;

-- Step 4: Check table structure
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'extra_expenditures' 
ORDER BY ordinal_position;
""")

print("\n" + "=" * 80)
print("⚠️  IMPORTANT NOTES:")
print("=" * 80)
print("""
1. Make sure to run these queries in your Neon database console
2. If extra_expenditures table already exists, the CREATE TABLE IF NOT EXISTS 
   will not recreate it. You may need to either:
   a) Drop the old table first (warning: will lose data!)
   b) Or add missing columns individually

3. To add missing columns individually (safer):

ALTER TABLE extra_expenditures ADD COLUMN IF NOT EXISTS expense_type VARCHAR NOT NULL DEFAULT 'General';
ALTER TABLE extra_expenditures ADD COLUMN IF NOT EXISTS description TEXT;
ALTER TABLE extra_expenditures ADD COLUMN IF NOT EXISTS amount NUMERIC(12, 2) NOT NULL;
ALTER TABLE extra_expenditures ADD COLUMN IF NOT EXISTS date DATE NOT NULL;
ALTER TABLE extra_expenditures ADD COLUMN IF NOT EXISTS notes TEXT;
ALTER TABLE extra_expenditures ADD COLUMN IF NOT EXISTS created_by VARCHAR;
ALTER TABLE extra_expenditures ADD COLUMN IF NOT EXISTS created_at TIMESTAMP;

4. After running the SQL, restart your Render backend deployment
""")
