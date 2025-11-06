#!/usr/bin/env python3
"""Run basic consistency checks for purchases, sales and blow costs.

Usage:
  cd backend
  python scripts/validate_costs.py

This script uses the project's SQLAlchemy config (SessionLocal) so run from the backend folder
so that `app` package imports resolve.
"""
import os
import sys

# Ensure the backend package directory is on sys.path so `import app` works
# regardless of the current working directory. This makes the script runnable
# from the repo root or from inside the scripts directory.
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from decimal import Decimal
from app.db.database import SessionLocal
from app.models.transaction import Purchase, Sale, Blow
from sqlalchemy import func, text
from sqlalchemy.exc import ProgrammingError

TOL = Decimal('0.01')

def approx_equal(a, b, tol=TOL):
    try:
        return abs(Decimal(a) - Decimal(b)) <= tol
    except Exception:
        return False

def check_purchases_totals(db):
    print('\nChecking purchases: total_amount == quantity * unit_price')
    bad = []
    for p in db.query(Purchase).all():
        expected = (p.quantity or 0) * (p.unit_price or 0)
        if not approx_equal(p.total_amount or 0, expected):
            bad.append((p.bill_number, p.item_id, p.quantity, float(p.unit_price or 0), float(p.total_amount or 0), float(expected)))
    print(f'  checked {db.query(func.count(Purchase.bill_number)).scalar()} purchases, mismatches: {len(bad)}')
    for row in bad[:20]:
        print('   ', row)
    return bad

def check_sales_totals(db):
    print('\nChecking sales: total_price == quantity * unit_price')
    bad = []
    for s in db.query(Sale).all():
        expected = (s.quantity or 0) * (s.unit_price or 0)
        if not approx_equal(s.total_price or 0, expected):
            bad.append((s.bill_number, s.item_id, s.quantity, float(s.unit_price or 0), float(s.total_price or 0), float(expected)))
    print(f'  checked {db.query(func.count(Sale.bill_number)).scalar()} sales, mismatches: {len(bad)}')
    for row in bad[:20]:
        print('   ', row)
    return bad

def last_purchase_price_for_item(db, item_id):
    p = db.query(Purchase).filter(Purchase.item_id == item_id).order_by(Purchase.date.desc()).first()
    return float(p.unit_price) if p and p.unit_price is not None else None

def check_sales_costs_vs_last_purchase(db):
    print('\nChecking sale.cost_basis vs last purchase unit_price for same item (heuristic)')
    bad = []
    for s in db.query(Sale).all():
        last_price = last_purchase_price_for_item(db, s.item_id)
        if last_price is None:
            continue
        if not approx_equal(s.cost_basis or 0, last_price):
            bad.append((s.bill_number, s.item_id, float(s.cost_basis or 0), float(last_price)))
    print(f'  compared {db.query(func.count(Sale.bill_number)).scalar()} sales, mismatches: {len(bad)}')
    for row in bad[:20]:
        print('   ', row)
    return bad

def check_blown_items_costs(db):
    print('\nChecking blown items: sale.cost_basis vs (preform last purchase + blow_cost_per_unit)')
    bad = []
    # For each sale, find a blow record that produces the sold item
    for s in db.query(Sale).all():
        # The Blow model may have a produced_unit_cost column in the ORM model but
        # the physical database may not have that column yet (migration/backfill
        # pending). Accessing the full ORM Blow object can raise a ProgrammingError
        # if the column is missing. We attempt the ORM query first and fall back
        # to a raw SQL select that only fetches columns we know exist.
        b = None
        try:
            b = db.query(Blow).filter(Blow.to_item_id == s.item_id).order_by(Blow.date_time.desc()).first()
        except ProgrammingError:
            # The session may now be in an aborted state; rollback before running raw SQL
            try:
                db.rollback()
            except Exception:
                pass
            # fall back to raw SQL that doesn't reference produced_unit_cost
            try:
                row = db.execute(text("""
                    SELECT id, user_id, from_item_id, to_item_id, quantity, blow_cost_per_unit, input_quantity, output_quantity, waste_quantity, efficiency_rate, notes, date_time
                    FROM blows
                    WHERE to_item_id = :to_id
                    ORDER BY date_time DESC
                    LIMIT 1
                """), {"to_id": s.item_id}).first()
                if row:
                    class BObj: pass
                    b = BObj()
                    # row may be a Row object; access by key if possible, else positional
                    try:
                        b.from_item_id = row['from_item_id']
                    except Exception:
                        b.from_item_id = row[2]
                    try:
                        b.blow_cost_per_unit = row['blow_cost_per_unit']
                    except Exception:
                        b.blow_cost_per_unit = row[5]
            except Exception:
                b = None
        except Exception:
            # Some other error may also abort the transaction; rollback defensively
            try:
                db.rollback()
            except Exception:
                pass
            b = None

        if not b:
            continue
        preform_last = last_purchase_price_for_item(db, b.from_item_id)
        expected = (preform_last or 0) + (float(b.blow_cost_per_unit or 0))
        if not approx_equal(s.cost_basis or 0, expected):
            bad.append((s.bill_number, s.item_id, float(s.cost_basis or 0), float(preform_last or 0), float(b.blow_cost_per_unit or 0), float(expected)))
    print(f'  analysed {db.query(func.count(Sale.bill_number)).scalar()} sales, blown mismatches: {len(bad)}')
    for row in bad[:20]:
        print('   ', row)
    return bad

def main():
    db = SessionLocal()
    try:
        bad_purchases = check_purchases_totals(db)
        bad_sales = check_sales_totals(db)
        bad_costs = check_sales_costs_vs_last_purchase(db)
        bad_blown = check_blown_items_costs(db)

        print('\nSummary:')
        print('  purchase mismatches:', len(bad_purchases))
        print('  sales mismatches:', len(bad_sales))
        print('  sales vs last-purchase mismatches:', len(bad_costs))
        print('  blown-item cost mismatches:', len(bad_blown))
    finally:
        db.close()

if __name__ == '__main__':
    main()
