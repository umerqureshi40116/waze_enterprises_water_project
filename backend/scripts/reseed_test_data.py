"""Reseed test data (safe mode by default).

Usage:
  python reseed_test_data.py      # dry-run, prints planned actions
  python reseed_test_data.py --yes  # perform destructive truncation + reseed

This script expects the app package importable (same env used for running the app).
It truncates tables in a safe order and then inserts a tiny deterministic dataset:
- a preform `Purchase` (unit_price 20)
- a Blow that consumes preforms and produces bottles with blow_cost_per_unit 2 and produced_unit_cost 22
- a Sale that sells bottles with cost_basis set from produced_unit_cost and unit_price 30

It uses SQLAlchemy session from `app.db.database.SessionLocal` and ORM models in `app.models`.
"""
import sys
import argparse
from decimal import Decimal

# allow running from backend/ as working dir
from pathlib import Path
repo_root = Path(__file__).resolve().parents[1]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

# Import app modules
try:
    from app.db.database import SessionLocal, engine
    from sqlalchemy import text
    from app.models.transaction import Purchase, Sale, Blow
    # Ensure party models are imported so their tables are present in metadata
    from app.models.party import Supplier, Customer
    from app.models.stock_movement import StockMovement
    from app.models.item import Item
    from app.models.user import User
    from app.core.config import settings
except Exception as e:
    print("Failed to import app modules:", e)
    raise


def dry_run_plan():
    print("Dry run: would perform the following actions:")
    print("- TRUNCATE: stock_movements, sales, purchases, blows, stocks (in that order).")
    print("- Insert a preform Purchase (unit_price=20)")
    print("- Insert a Blow record producing 1 SKU from preform with blow_cost_per_unit=2 (produced_unit_cost=22)")
    print("- Insert a Sale selling the produced item with unit_price=30 and cost_basis=22")
    print("- Commit and print inserted ids")


def truncate_tables(session):
    # Use raw SQL TRUNCATE to reset sequences; adjust table names to actual DB names
    # Order: dependent children first
    tables = [
        'stock_movements',
        'sales',
        'purchases',
        'blows',
        # optionally 'stocks' if present in your schema
    ]
    print("Truncating tables:")
    for t in tables:
        print(f" - {t}")
        session.execute(text(f"TRUNCATE TABLE {t} RESTART IDENTITY CASCADE;"))
    session.commit()


def create_test_data(session):
    # Minimal user and items setup: attempt to find an existing user and items, else create them
    user = session.query(User).first()
    if not user:
        user = User(username='testuser')
        session.add(user)
        session.flush()
        print(f"Created test user id={user.id}")
    else:
        print(f"Using existing user id={user.id}")

    # Items: preform (raw) and bottle (produced)
    preform = session.query(Item).filter(Item.name.ilike('%preform%')).first()
    if not preform:
        preform = Item(name='Preform 500ml', sku='PREFORM-500')
        session.add(preform)
        session.flush()
        print(f"Created preform item id={preform.id}")
    else:
        print(f"Using existing preform id={preform.id}")

    bottle = session.query(Item).filter(Item.name.ilike('%bottle%')).first()
    if not bottle:
        bottle = Item(name='Bottle 500ml', sku='BOTTLE-500')
        session.add(bottle)
        session.flush()
        print(f"Created bottle item id={bottle.id}")
    else:
        print(f"Using existing bottle id={bottle.id}")

    # Insert a Purchase for preform with unit_price 20
    purchase = Purchase(
        bill_number='TEST-PUR-1',
        supplier_id=None,
        item_id=preform.id,
        quantity=1,
        unit_price=Decimal('20.00'),
        total_amount=Decimal('20.00'),
        created_by=user.id,
    )
    session.add(purchase)
    session.flush()
    print(f"Inserted Purchase bill_number={purchase.bill_number} item={preform.id} unit_price=20")

    # Create a Blow process that produces 1 bottle from 1 preform
    blow = Blow(
        id='TEST-BLOW-1',
        user_id=user.id,
        from_item_id=preform.id,
        to_item_id=bottle.id,
        quantity=1,
        blow_cost_per_unit=Decimal('2.00'),
        produced_unit_cost=Decimal('22.00'),
        input_quantity=1,
        output_quantity=1,
        efficiency_rate=Decimal('100.00'),
        notes='Test blow process',
    )
    session.add(blow)
    session.flush()
    print(f"Inserted Blow id={blow.id} produced_unit_cost=22")

    # Create a stock movement for produced bottle (+1)
    sm = StockMovement(
        item_id=bottle.id,
        movement_type='production',
        quantity_change=1,
        reference_id=blow.id,
        recorded_by=user.id,
        notes='Seeded production movement',
    )
    session.add(sm)
    session.flush()
    print(f"Inserted StockMovement id={sm.id}")

    # Create a Sale consuming the produced bottle with unit_price=30 and cost_basis=22
    sale = Sale(
        bill_number='TEST-SALE-1',
        customer_id=None,
        item_id=bottle.id,
        quantity=1,
        unit_price=Decimal('30.00'),
        total_price=Decimal('30.00'),
        cost_basis=Decimal('22.00'),
        created_by=user.id,
    )
    session.add(sale)
    session.flush()
    print(f"Inserted Sale bill_number={sale.bill_number} unit_price=30 cost_basis=22")

    session.commit()
    return {
        'purchase_bill_number': purchase.bill_number,
        'blow_id': blow.id,
        'sale_bill_number': sale.bill_number,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--yes', action='store_true', help='Apply truncation and reseed (destructive).')
    args = parser.parse_args()

    if not args.yes:
        dry_run_plan()
        print('\nRun with --yes to actually apply changes.')
        return

    print('Opening DB session...')
    session = SessionLocal()
    try:
        print('Beginning destructive reseed: truncating and inserting test data.')
        truncate_tables(session)
        ids = create_test_data(session)
        print('Reseed complete. Inserted ids:', ids)
        print('Run python scripts/validate_costs.py to validate test dataset (expected: no blown-item mismatches).')
    except Exception as e:
        print('Error during reseed:', e)
        session.rollback()
        raise
    finally:
        session.close()

if __name__ == '__main__':
    main()
