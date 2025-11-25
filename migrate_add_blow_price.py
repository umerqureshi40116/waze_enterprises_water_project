"""
Migration script to add blow_price column to sales table
Run this once to update existing database schema
"""
from sqlalchemy import text, inspect
from app.db.database import SessionLocal, engine

def migrate_add_blow_price():
    """Add blow_price column to sales table if it doesn't exist"""
    db = SessionLocal()
    
    try:
        print("Checking if blow_price column exists in sales table...")
        
        # Use inspector to check column existence
        inspector = inspect(engine)
        columns = [c['name'] for c in inspector.get_columns('sales')]
        
        if 'blow_price' in columns:
            print("✅ blow_price column already exists!")
            return
        
        print("📝 blow_price column not found, adding it...")
        
        # Add the column with proper transaction handling
        with engine.begin() as connection:
            connection.execute(text(
                "ALTER TABLE sales ADD COLUMN blow_price NUMERIC(12, 2) DEFAULT 0.00"
            ))
        
        print("✅ blow_price column added successfully!")
    
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        print("💡 Try manually running this SQL in your PostgreSQL database:")
        print("   ALTER TABLE sales ADD COLUMN blow_price NUMERIC(12, 2) DEFAULT 0.00;")
    
    finally:
        db.close()

if __name__ == "__main__":
    migrate_add_blow_price()
