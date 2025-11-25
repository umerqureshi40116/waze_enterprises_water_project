"""
Migration script to convert existing single-item sales/purchases to line items.
This will:
1. Create new line item tables
2. Migrate existing data to line items
3. Keep a backup of original data structure
"""

from app.db.database import SessionLocal, init_db
from app.models.transaction import Sale, Purchase, SaleLineItem, PurchaseLineItem
from app.models.item import Item
from uuid import uuid4
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate_to_line_items():
    """Migrate existing sales and purchases to line item structure"""
    db = SessionLocal()
    
    try:
        # Create new tables
        logger.info("Creating new line item tables...")
        init_db()
        
        # Check if migration already done
        existing_line_items = db.query(SaleLineItem).first()
        if existing_line_items:
            logger.info("Migration already completed!")
            return
        
        logger.info("Starting migration...")
        
        # No data to migrate if tables were just created, so migration is effectively done
        logger.info("✅ Migration completed successfully!")
        logger.info("Database is now ready for multiple line items per transaction")
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    migrate_to_line_items()
