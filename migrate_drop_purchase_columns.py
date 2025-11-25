"""
Migration script to drop old single-item columns from purchases table.
The purchases table was previously storing single items, but now uses line_items.
This migration removes those old columns that are no longer used.
"""

from app.db.database import SessionLocal
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate_drop_old_purchase_columns():
    """Drop old single-item columns from purchases table"""
    db = SessionLocal()
    
    try:
        logger.info("Starting migration to drop old purchase columns...")
        
        # Get the connection
        connection = db.connection()
        
        # Drop old columns if they exist
        old_columns = ['quantity', 'unit_price', 'cost_basis', 'blow_price']
        
        for col in old_columns:
            try:
                logger.info(f"Checking if column '{col}' exists in purchases table...")
                # Check if column exists by trying to drop it
                connection.execute(text(f"ALTER TABLE purchases DROP COLUMN IF EXISTS {col} CASCADE;"))
                logger.info(f"✅ Dropped column '{col}' from purchases table")
            except Exception as e:
                logger.warning(f"⚠️  Could not drop column '{col}': {str(e)}")
        
        db.commit()
        logger.info("✅ Migration completed successfully!")
        logger.info("Old single-item columns have been removed from purchases table")
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    migrate_drop_old_purchase_columns()
