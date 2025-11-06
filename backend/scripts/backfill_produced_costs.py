#!/usr/bin/env python3
"""Backfill produced_unit_cost on existing Blow records.

This script will:
 - add the `produced_unit_cost` column to `blows` table if missing (best-effort),
 - compute produced_unit_cost = preform_purchase_price_at_blow + blow_cost_per_unit
   using the latest purchase for the preform at or before the blow date (fallback to last purchase).

Run from backend folder:
  python scripts/backfill_produced_costs.py
"""
import os
import sys
from decimal import Decimal

# Make backend package importable
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app.db.database import SessionLocal, engine
from app.models.transaction import Blow, Purchase
from sqlalchemy import text

def ensure_column():
    # Check information_schema first to avoid errors
    conn = engine.connect()
    try:
        res = conn.execute(text("SELECT 1 FROM information_schema.columns WHERE table_name = 'blows' AND column_name = 'produced_unit_cost' LIMIT 1")).fetchone()
        if res:
            print('Column produced_unit_cost already exists on blows')
            return True
        # Try to add the column; commit the change so other connections see it
        conn.execute(text('ALTER TABLE blows ADD COLUMN produced_unit_cost NUMERIC(12,2)'))
        conn.execute(text('COMMIT'))
        print('Added column produced_unit_cost to blows')
        return True
    except Exception as e:
        print('Failed to add produced_unit_cost column:', e)
        return False
    finally:
        conn.close()

def backfill():
    db = SessionLocal()
    updated = 0
    skipped = 0
    try:
        # Ensure the column exists before attempting to read/update it.
        col_ok = ensure_column()

        # Use raw SQL to fetch blows (avoid selecting produced_unit_cost directly so the query
        # won't fail if the column still isn't visible to this session).
        rows = db.execute(text("SELECT id, from_item_id, to_item_id, quantity, blow_cost_per_unit, input_quantity, output_quantity, waste_quantity, efficiency_rate, notes, date_time FROM blows ORDER BY date_time ASC")).fetchall()
        total = len(rows)
        for row in rows:
            # Row may be a MappingRow or a positional-only Row; use _mapping for safe keyed access
            mapping = None
            try:
                mapping = row._mapping
            except Exception:
                mapping = None

            if mapping is not None:
                b_id = mapping.get('id')
                blow_date = mapping.get('date_time')
                from_item = mapping.get('from_item_id')
                blow_cost = mapping.get('blow_cost_per_unit')
            else:
                # positional fallback
                b_id = row[0]
                blow_date = row[10]
                from_item = row[1]
                blow_cost = row[4]

            produced_val = None

            # find purchase for preform at or before blow date
            preform_purchase = None
            if blow_date:
                preform_purchase = db.execute(text("SELECT unit_price, date FROM purchases WHERE item_id = :item AND date <= :dt ORDER BY date DESC LIMIT 1"), {"item": from_item, "dt": blow_date}).fetchone()
            if not preform_purchase:
                preform_purchase = db.execute(text("SELECT unit_price, date FROM purchases WHERE item_id = :item ORDER BY date DESC LIMIT 1"), {"item": from_item}).fetchone()

            if preform_purchase and preform_purchase[0] is not None:
                try:
                    preform_price = float(preform_purchase[0])
                    blow_cost_unit = float(blow_cost or 0)
                    produced_val = Decimal(preform_price + blow_cost_unit)
                except Exception:
                    produced_val = None

            if produced_val is not None:
                # update row via raw SQL; ensure column exists first
                if col_ok:
                    try:
                        db.execute(text("UPDATE blows SET produced_unit_cost = :val WHERE id = :id"), {"val": produced_val, "id": b_id})
                        updated += 1
                    except Exception:
                        skipped += 1
                else:
                    skipped += 1
            else:
                skipped += 1

        db.commit()
        print(f'Backfill complete. updated={updated}, skipped={skipped}, total_blows={total}')
    finally:
        db.close()

if __name__ == '__main__':
    print('Ensuring produced_unit_cost column on blows...')
    ensure_column()
    print('Running backfill...')
    backfill()
