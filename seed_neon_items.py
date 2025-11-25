#!/usr/bin/env python3
"""
Seed items to Neon database for the production system
Run this directly with your Neon DATABASE_URL
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.item import Item, Stock
from app.db.database import Base

# Get DATABASE_URL - Neon connection string
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/water_inventory")

print(f"🔗 Connecting to database: {DATABASE_URL[:50]}...")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def seed_items():
    """Seed sample items to database"""
    db = SessionLocal()
    
    try:
        # Check if items already exist
        existing_items = db.query(Item).count()
        if existing_items > 0:
            print(f"✅ Database already has {existing_items} items. Skipping seed.")
            return
        
        print("📦 Creating sample items...")
        
        # Items to create
        items = [
            Item(
                id="Item_Preform_500A",
                name="PET Preform 500ml A",
                type="preform",
                size="500ml",
                grade="A",
                unit="pcs (1000)"
            ),
            Item(
                id="Item_Preform_1500A",
                name="PET Preform 1500ml A",
                type="preform",
                size="1500ml",
                grade="A",
                unit="pcs (1000)"
            ),
            Item(
                id="Item_Bottle_500A",
                name="500ml Bottle A",
                type="bottle",
                size="500ml",
                grade="A",
                unit="pcs (1000)"
            ),
            Item(
                id="Item_Bottle_1500A",
                name="1500ml Bottle A",
                type="bottle",
                size="1500ml",
                grade="A",
                unit="pcs (1000)"
            ),
            Item(
                id="Item_Sold_500A",
                name="Sold 500ml Bottle A",
                type="sold",
                size="500ml",
                grade="A",
                unit="pcs (1000)"
            )
        ]
        
        db.add_all(items)
        db.flush()
        
        print("📊 Creating stock entries...")
        
        stocks = [
            Stock(item_id="Item_Preform_500A", quantity=2000),
            Stock(item_id="Item_Preform_1500A", quantity=1000),
            Stock(item_id="Item_Bottle_500A", quantity=800),
            Stock(item_id="Item_Bottle_1500A", quantity=400),
            Stock(item_id="Item_Sold_500A", quantity=0)
        ]
        
        db.add_all(stocks)
        db.commit()
        
        print("✅ Items seeded successfully!")
        print("\n📋 Seeded items:")
        for item in items:
            print(f"   - {item.name} ({item.id})")
        
    except Exception as e:
        print(f"❌ Error seeding items: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_items()
