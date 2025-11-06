"""Quick script to check user records and verify passwords"""
from app.db.database import SessionLocal
from app.models.user import User
from app.core.security import verify_password, get_password_hash

db = SessionLocal()

print("\n=== Current Users in Database ===")
users = db.query(User).all()
for u in users:
    print(f"ID: {u.id}, Username: {u.username}, Role: {u.role}")
    print(f"  Hash preview: {u.password_hash[:60]}...")
    
print("\n=== Password Verification Tests ===")
for u in users:
    # Test with common passwords
    for pwd in ['admin', 'user', 'admin123', 'user123']:
        if verify_password(pwd, u.password_hash):
            print(f"✓ User '{u.username}' password is: {pwd}")
            break
    else:
        print(f"✗ User '{u.username}' password NOT in test list")

db.close()
