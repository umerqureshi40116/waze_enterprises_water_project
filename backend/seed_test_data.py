#!/usr/bin/env python3
"""
Seed test data for development:
- Multiple customers
- Multiple items with various types/sizes
"""

import os
import sys
from decimal import Decimal
from datetime import datetime, timedelta

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db.database import SessionLocal
from app.models.party import Customer
from app.models.item import Item, Stock

def seed_customers():
    """Add sample customers"""
    db = SessionLocal()
    
    customers_data = [
        {
            "id": "CUST-001",
            "name": "One Stop Marketing",
            "contact_person": "Ahmed Ali",
            "phone": "03001234567",
            "email": "ahmed@onestop.com",
            "address": "123 Business Avenue",
            "city": "Karachi"
        },
        {
            "id": "CUST-002",
            "name": "Retail Hub Stores",
            "contact_person": "Fatima Khan",
            "phone": "03119876543",
            "email": "fatima@retailhub.com",
            "address": "456 Commerce Street",
            "city": "Lahore"
        },
        {
            "id": "CUST-003",
            "name": "Fresh Beverages Ltd",
            "contact_person": "Hassan Malik",
            "phone": "03335554444",
            "email": "hassan@freshbev.com",
            "address": "789 Industrial Zone",
            "city": "Islamabad"
        },
        {
            "id": "CUST-004",
            "name": "Mountain Springs Distribution",
            "contact_person": "Saira Ahmed",
            "phone": "03003332222",
            "email": "saira@mtnsprings.com",
            "address": "321 Trade Center",
            "city": "Peshawar"
        },
        {
            "id": "CUST-005",
            "name": "Urban Hydration Co",
            "contact_person": "Ali Raza",
            "phone": "03125551111",
            "email": "ali@urbanhydra.com",
            "address": "654 Market Plaza",
            "city": "Multan"
        }
    ]
    
    for cust_data in customers_data:
        existing = db.query(Customer).filter(Customer.id == cust_data["id"]).first()
        if not existing:
            customer = Customer(
                id=cust_data["id"],
                name=cust_data["name"],
                contact_person=cust_data["contact_person"],
                phone=cust_data["phone"],
                email=cust_data["email"],
                address=cust_data["address"],
                city=cust_data["city"],
                created_by="system",
                date=datetime.utcnow()
            )
            db.add(customer)
            print(f"✅ Added customer: {cust_data['id']} - {cust_data['name']}")
        else:
            print(f"⏭️  Customer already exists: {cust_data['id']}")
    
    db.commit()
    db.close()

def seed_items():
    """Add sample items"""
    db = SessionLocal()
    
    items_data = [
        # Preforms
        {"id": "PF-500ML", "name": "500ml Preform", "type": "preform", "size": "500ml", "grade": "A", "unit": "pcs"},
        {"id": "PF-1LT", "name": "1 Liter Preform", "type": "preform", "size": "1L", "grade": "A", "unit": "pcs"},
        {"id": "PF-2LT", "name": "2 Liter Preform", "type": "preform", "size": "2L", "grade": "A", "unit": "pcs"},
        {"id": "PF-500ML-B", "name": "500ml Preform Grade B", "type": "preform", "size": "500ml", "grade": "B", "unit": "pcs"},
        
        # Bottles
        {"id": "BT-500ML", "name": "500ml Bottle", "type": "bottle", "size": "500ml", "grade": "A", "unit": "pcs"},
        {"id": "BT-1LT", "name": "1 Liter Bottle", "type": "bottle", "size": "1L", "grade": "A", "unit": "pcs"},
        {"id": "BT-2LT", "name": "2 Liter Bottle", "type": "bottle", "size": "2L", "grade": "A", "unit": "pcs"},
        {"id": "BT-500ML-B", "name": "500ml Bottle Grade B", "type": "bottle", "size": "500ml", "grade": "B", "unit": "pcs"},
        
        # Sold (ready to sell)
        {"id": "SOLD-500ML", "name": "500ml Water Bottle", "type": "sold", "size": "500ml", "grade": "A", "unit": "pcs"},
        {"id": "SOLD-1LT", "name": "1 Liter Water Bottle", "type": "sold", "size": "1L", "grade": "A", "unit": "pcs"},
        {"id": "SOLD-2LT", "name": "2 Liter Water Bottle", "type": "sold", "size": "2L", "grade": "A", "unit": "pcs"},
    ]
    
    for item_data in items_data:
        existing = db.query(Item).filter(Item.id == item_data["id"]).first()
        if not existing:
            item = Item(
                id=item_data["id"],
                name=item_data["name"],
                type=item_data["type"],
                size=item_data["size"],
                grade=item_data["grade"],
                unit=item_data["unit"]
            )
            db.add(item)
            
            # Create stock entry with 0 quantity
            stock = Stock(
                item_id=item_data["id"],
                quantity=0
            )
            db.add(stock)
            print(f"✅ Added item: {item_data['id']} - {item_data['name']}")
        else:
            print(f"⏭️  Item already exists: {item_data['id']}")
    
    db.commit()
    db.close()

if __name__ == "__main__":
    print("🌱 Seeding test data...\n")
    
    print("📋 Seeding customers...")
    seed_customers()
    
    print("\n📦 Seeding items...")
    seed_items()
    
    print("\n✅ Test data seeding complete!")
