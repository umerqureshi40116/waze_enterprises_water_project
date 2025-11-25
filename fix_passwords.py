"""
Fix user passwords by updating with proper bcrypt hashes
"""
from app.db.database import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash

db = SessionLocal()

try:
    # Update Waheed's password to 'admin'
    waheed = db.query(User).filter(User.username == 'Waheed').first()
    if waheed:
        waheed.password_hash = get_password_hash('admin')
        print(f"✅ Updated Waheed password hash: {waheed.password_hash[:60]}...")
    else:
        print("❌ Waheed user not found!")
    
    # Update Umer's password to 'user'
    umer = db.query(User).filter(User.username == 'Umer').first()
    if umer:
        umer.password_hash = get_password_hash('user')
        print(f"✅ Updated Umer password hash: {umer.password_hash[:60]}...")
    else:
        print("❌ Umer user not found!")
    
    db.commit()
    print("\n✅ Password hashes updated successfully!")
    print("\nYou can now login with:")
    print("  Admin: Waheed / admin")
    print("  User:  Umer / user")
    
except Exception as e:
    print(f"❌ Error: {e}")
    db.rollback()
finally:
    db.close()
