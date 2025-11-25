"""
Migration script to convert unit system from "pcs (1000)" to simple "pcs"
and multiply quantities by the conversion factor.

Before: Item.unit = "pcs (1000)", Stock.quantity = 100 (means 100 cartons)
After:  Item.unit = "pcs", Stock.quantity = 100000 (means 100,000 pieces)
"""

import re
from sqlalchemy import text
from app.db.database import SessionLocal
from app.models.item import Item, Stock

def extract_conversion_factor(unit_str):
    """
    Extract the conversion factor from unit string.
    Examples:
    - "pcs (1000)" -> 1000
    - "pcs (500)" -> 500
    - "kg" -> 1 (no conversion factor)
    """
    match = re.search(r'\((\d+)\)', unit_str)
    if match:
        return int(match.group(1))
    return 1  # Default to 1 if no factor found

def extract_unit_base(unit_str):
    """
    Extract the base unit from unit string.
    Examples:
    - "pcs (1000)" -> "pcs"
    - "pcs (500)" -> "pcs"
    - "kg" -> "kg"
    """
    base = re.sub(r'\s*\(\d+\)\s*', '', unit_str).strip()
    return base if base else "pcs"

def migrate():
    """Run the migration"""
    db = SessionLocal()
    
    try:
        print("🔄 Starting unit migration...")
        print("-" * 60)
        
        # Get all items with old unit format
        items = db.query(Item).all()
        migration_count = 0
        
        for item in items:
            if item.unit is None:
                print(f"⚠️  Item {item.id}: unit is NULL, skipping")
                continue
                
            # Extract conversion factor and base unit
            conversion_factor = extract_conversion_factor(item.unit)
            base_unit = extract_unit_base(item.unit)
            
            # Get current stock
            stock = db.query(Stock).filter(Stock.item_id == item.id).first()
            old_quantity = stock.quantity if stock else 0
            
            # Calculate new quantity
            new_quantity = old_quantity * conversion_factor
            
            print(f"\n📦 Item: {item.id}")
            print(f"   Name: {item.name}")
            print(f"   Old Unit: '{item.unit}' → New Unit: '{base_unit}'")
            print(f"   Factor: {conversion_factor}")
            print(f"   Old Quantity: {old_quantity} → New Quantity: {new_quantity}")
            
            # Update item unit
            item.unit = base_unit
            
            # Update stock quantity
            if stock:
                stock.quantity = new_quantity
                print(f"   ✅ Updated stock")
            else:
                # Create stock if it doesn't exist
                new_stock = Stock(item_id=item.id, quantity=new_quantity)
                db.add(new_stock)
                print(f"   ✅ Created stock")
            
            migration_count += 1
        
        # Commit changes
        db.commit()
        
        print("\n" + "=" * 60)
        print(f"✅ Migration complete!")
        print(f"   Items migrated: {migration_count}")
        print("=" * 60)
        
        # Verify
        print("\n📋 Verification:")
        items_after = db.query(Item).all()
        for item in items_after:
            stock = db.query(Stock).filter(Stock.item_id == item.id).first()
            qty = stock.quantity if stock else 0
            print(f"   {item.id}: unit='{item.unit}' quantity={qty}")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    migrate()
