"""Add notes columns to purchases and sales tables (one-time migration)."""
import sys
from pathlib import Path

repo_root = Path(__file__).resolve().parents[1]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from sqlalchemy import text
from app.db.database import SessionLocal

def main():
    db = SessionLocal()
    try:
        print("Adding notes column to purchases table...")
        try:
            db.execute(text("ALTER TABLE purchases ADD COLUMN notes TEXT"))
            db.commit()
            print("✓ Added notes column to purchases")
        except Exception as e:
            if "already exists" in str(e) or "duplicate" in str(e).lower():
                print("✓ notes column already exists on purchases")
            else:
                print(f"✗ Error adding notes to purchases: {e}")
                db.rollback()
        
        print("\nAdding notes column to sales table...")
        try:
            db.execute(text("ALTER TABLE sales ADD COLUMN notes TEXT"))
            db.commit()
            print("✓ Added notes column to sales")
        except Exception as e:
            if "already exists" in str(e) or "duplicate" in str(e).lower():
                print("✓ notes column already exists on sales")
            else:
                print(f"✗ Error adding notes to sales: {e}")
                db.rollback()
        
        print("\n✓ Migration complete. You can now restart your app.")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == '__main__':
    main()
