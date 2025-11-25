#!/usr/bin/env python3
"""
Check what items are in Neon database
"""
import os
import sys
from app.db.database import SessionLocal
from app.models.item import Item

def check_items():
    db = SessionLocal()
    try:
        items = db.query(Item).all()
        print(f"\n📦 Items in database: {len(items)}")
        for item in items:
            print(f"   - {item.id}: {item.name}")
        
        if len(items) == 0:
            print("\n❌ NO ITEMS IN DATABASE!")
            print("   Run: python init_db.py")
            return False
        else:
            print(f"\n✅ {len(items)} items found")
            return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    check_items()
