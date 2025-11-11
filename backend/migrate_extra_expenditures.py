"""
Migration script to add missing columns to extra_expenditures table
Run this once to update existing database schema on Render/Neon
"""
from sqlalchemy import text, inspect
from app.db.database import SessionLocal, engine

def migrate_extra_expenditures_table():
    """Add missing columns to extra_expenditures table if they don't exist"""
    db = SessionLocal()
    
    try:
        print("Checking extra_expenditures table schema...")
        
        # Use inspector to check what columns exist
        inspector = inspect(engine)
        existing_columns = [c['name'] for c in inspector.get_columns('extra_expenditures')]
        
        print(f"Existing columns: {existing_columns}")
        
        # Define columns that need to be added
        columns_to_add = [
            ("expense_type", "VARCHAR NOT NULL DEFAULT 'General'"),
            ("description", "TEXT"),
            ("amount", "NUMERIC(12, 2) NOT NULL DEFAULT 0"),
            ("date", "DATE NOT NULL DEFAULT CURRENT_DATE"),
            ("notes", "TEXT"),
            ("created_by", "VARCHAR"),
            ("created_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"),
        ]
        
        # Add missing columns
        with engine.begin() as connection:
            for col_name, col_definition in columns_to_add:
                if col_name not in existing_columns:
                    print(f"📝 Adding missing column: {col_name}...")
                    connection.execute(text(
                        f"ALTER TABLE extra_expenditures ADD COLUMN {col_name} {col_definition}"
                    ))
                    print(f"✅ Column {col_name} added successfully!")
                else:
                    print(f"ℹ️ Column {col_name} already exists")
        
        print("\n✅ Migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        print("\n💡 Try manually running this SQL in your Render database:")
        print("""
        ALTER TABLE extra_expenditures ADD COLUMN IF NOT EXISTS expense_type VARCHAR NOT NULL DEFAULT 'General';
        ALTER TABLE extra_expenditures ADD COLUMN IF NOT EXISTS description TEXT;
        ALTER TABLE extra_expenditures ADD COLUMN IF NOT EXISTS amount NUMERIC(12, 2) NOT NULL DEFAULT 0;
        ALTER TABLE extra_expenditures ADD COLUMN IF NOT EXISTS date DATE NOT NULL DEFAULT CURRENT_DATE;
        ALTER TABLE extra_expenditures ADD COLUMN IF NOT EXISTS notes TEXT;
        ALTER TABLE extra_expenditures ADD COLUMN IF NOT EXISTS created_by VARCHAR;
        ALTER TABLE extra_expenditures ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
        """)
    
    finally:
        db.close()

if __name__ == "__main__":
    migrate_extra_expenditures_table()
