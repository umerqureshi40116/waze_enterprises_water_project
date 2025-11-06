#!/usr/bin/env python
"""Debug script to check FIFO cost calculation"""
from app.db.database import SessionLocal
from app.models.transaction import Purchase, PurchaseLineItem, Sale, SaleLineItem

db = SessionLocal()

print("=" * 80)
print("PURCHASES:")
print("=" * 80)

purchases = db.query(Purchase).all()
for p in purchases:
    print(f"\n📦 {p.bill_number}")
    print(f"   Supplier: {p.supplier_id}")
    print(f"   Total: Rs {p.total_amount}")
    print(f"   Date: {p.date}")
    
    line_items = db.query(PurchaseLineItem).filter(
        PurchaseLineItem.bill_number == p.bill_number
    ).all()
    
    for li in line_items:
        print(f"   - Item {li.item_id}: Qty {li.quantity} x Rs {li.unit_price} = Rs {li.total_price}")

print("\n" + "=" * 80)
print("SALES:")
print("=" * 80)

sales = db.query(Sale).all()
for s in sales:
    print(f"\n💰 {s.bill_number}")
    print(f"   Customer: {s.customer_id}")
    print(f"   Total: Rs {s.total_price}")
    print(f"   Date: {s.date}")
    
    line_items = db.query(SaleLineItem).filter(
        SaleLineItem.bill_number == s.bill_number
    ).all()
    
    for li in line_items:
        print(f"   - Item {li.item_id}:")
        print(f"     Qty: {li.quantity}")
        print(f"     Unit Price: Rs {li.unit_price}")
        print(f"     Cost Basis: Rs {li.cost_basis} ⚠️ (THIS SHOULD BE Rs 50!)")
        print(f"     Total: Rs {li.total_price}")

print("\n" + "=" * 80)
print("CHECKING FIFO LOGIC:")
print("=" * 80)

# Check what the oldest purchase is for each item sold
from sqlalchemy import func

sales = db.query(Sale).all()
for s in sales:
    sale_line_items = db.query(SaleLineItem).filter(
        SaleLineItem.bill_number == s.bill_number
    ).all()
    
    for sli in sale_line_items:
        item_id = sli.item_id
        
        # Find oldest purchase for this item
        oldest_purchase_li = db.query(PurchaseLineItem).filter(
            PurchaseLineItem.item_id == item_id
        ).join(Purchase, Purchase.bill_number == PurchaseLineItem.bill_number).order_by(Purchase.date.asc()).first()
        
        print(f"\n📊 Sale Item: {item_id}")
        print(f"   Current Cost Basis in DB: Rs {sli.cost_basis}")
        
        if oldest_purchase_li:
            print(f"   ✅ Oldest Purchase Found:")
            print(f"      Bill: {oldest_purchase_li.bill_number}")
            print(f"      Unit Price: Rs {oldest_purchase_li.unit_price}")
            print(f"      Date: {oldest_purchase_li.purchase.date if oldest_purchase_li.purchase else 'N/A'}")
        else:
            print(f"   ❌ NO OLDEST PURCHASE FOUND!")

db.close()
