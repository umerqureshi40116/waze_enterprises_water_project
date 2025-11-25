#!/usr/bin/env python3
"""
Clear all dummy/test data from the database.
Delete all records from: sales, purchases, stock, stock_movements, and customer transactions.
"""

import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.db.database import SessionLocal, engine
from app.models.transaction import Sale, Purchase, SaleLineItem, PurchaseLineItem, StockMovement
from app.models.item import Stock
from app.models.party import Customer

def clear_dummy_data():
    """Clear all dummy data from database"""
    db = SessionLocal()
    
    try:
        print("🗑️  Clearing dummy data from database...")
        
        # Delete in order to avoid foreign key constraints
        print("  - Deleting SaleLineItems...")
        db.query(SaleLineItem).delete()
        
        print("  - Deleting PurchaseLineItems...")
        db.query(PurchaseLineItem).delete()
        
        print("  - Deleting StockMovements...")
        db.query(StockMovement).delete()
        
        print("  - Deleting Sales...")
        db.query(Sale).delete()
        
        print("  - Deleting Purchases...")
        db.query(Purchase).delete()
        
        print("  - Deleting Stock...")
        db.query(Stock).delete()
        
        print("  - Deleting Customers...")
        db.query(Customer).delete()
        
        db.commit()
        print("\n✅ All dummy data cleared successfully!")
        print("   Database is now ready for fresh data entry.")
        
    except Exception as e:
        print(f"\n❌ Error clearing data: {e}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    print("\n" + "="*60)
    print("  DATABASE CLEANUP - REMOVE DUMMY DATA")
    print("="*60 + "\n")
    
    response = input("⚠️  This will DELETE all sales, purchases, stock, and customers.\nContinue? (yes/no): ").strip().lower()
    
    if response == 'yes':
        clear_dummy_data()
    else:
        print("Cancelled.")
        sys.exit(0)
