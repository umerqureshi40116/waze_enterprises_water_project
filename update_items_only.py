#!/usr/bin/env python3
"""
Update items to ONLY have the specified items with no grades
Mapping: Grade A = Pure, Grade B = Mix, Grade C = Local
"""
import os
import sys
from app.db.database import SessionLocal
from app.models.item import Item, Stock
from sqlalchemy import text

def update_items():
    db = SessionLocal()
    try:
        print("\n🔄 Clearing all existing items...")
        
        # First, disable foreign key constraints temporarily
        db.execute(text("SET session_replication_role = 'replica'"))
        
        # Delete all related data first
        db.execute(text("DELETE FROM purchase_line_items"))
        db.execute(text("DELETE FROM sale_line_items"))
        db.execute(text("DELETE FROM stocks"))
        db.execute(text("DELETE FROM items"))
        
        # Re-enable foreign key constraints
        db.execute(text("SET session_replication_role = 'origin'"))
        
        db.commit()
        print("✅ Cleared all items, stocks, and related transactions")
        
        # Define items to keep (without grades in the item name)
        items_to_create = [
            {
                "id": "pure_500ml_getron_15_50g",
                "name": "Pure 500ml Getron",
                "type": "preform",
                "size": "500ml",
                "unit": "pcs",
                "grade": "A",  # A = Pure
                "weight": "15.50 gram"
            },
            {
                "id": "pure_500ml_17g_preform",
                "name": "Pure 500ml",
                "type": "preform",
                "size": "500ml",
                "unit": "pcs",
                "grade": "A",  # A = Pure
                "weight": "17 gram preform"
            },
            {
                "id": "local_pure_preform_15g",
                "name": "Local Pure",
                "type": "preform",
                "size": "500ml",
                "unit": "pcs",
                "grade": "C",  # C = Local
                "weight": "15 gram"
            },
            {
                "id": "pure_1500ml_getron_31_50g",
                "name": "Pure 1500ml Getron",
                "type": "preform",
                "size": "1500ml",
                "unit": "pcs",
                "grade": "A",  # A = Pure
                "weight": "31.50 gram"
            },
            {
                "id": "local_pure_1500ml_preform",
                "name": "Local Pure 1500ml",
                "type": "preform",
                "size": "1500ml",
                "unit": "pcs",
                "grade": "C",  # C = Local
                "weight": "preform"
            }
        ]
        
        print(f"\n➕ Creating {len(items_to_create)} items...\n")
        
        for item_data in items_to_create:
            # Create item without weight in name
            item = Item(
                id=item_data["id"],
                name=item_data["name"],
                type=item_data["type"],
                size=item_data["size"],
                grade=item_data["grade"],
                unit=item_data["unit"]
            )
            db.add(item)
            
            # Create stock entry for this item
            stock = Stock(
                item_id=item_data["id"],
                quantity=0
            )
            db.add(stock)
            
            print(f"   ✅ {item_data['name']:<30} ({item_data['grade']}) - {item_data['weight']}")
        
        db.commit()
        print(f"\n✅ Successfully created {len(items_to_create)} items\n")
        
        # Verify
        all_items = db.query(Item).all()
        print(f"📦 Total items in database: {len(all_items)}\n")
        
        for item in all_items:
            grade_name = {"A": "Pure", "B": "Mix", "C": "Local"}.get(item.grade, item.grade)
            print(f"   {item.name:<30} | Size: {item.size:<10} | Grade: {grade_name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    update_items()
