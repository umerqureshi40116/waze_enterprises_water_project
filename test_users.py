"""
Test script to verify database users and passwords
"""
import sys
sys.path.insert(0, '.')

from app.db.database import SessionLocal
from app.models.user import User
from app.core.security import verify_password

db = SessionLocal()

print("=" * 50)
print("Checking users in database...")
print("=" * 50)

users = db.query(User).all()

if not users:
    print("❌ NO USERS FOUND IN DATABASE!")
    print("\nPlease run: python init_db.py")
else:
    print(f"✅ Found {len(users)} user(s):\n")
    
    for user in users:
        print(f"ID: {user.id}")
        print(f"Username: {user.username}")
        print(f"Email: {user.email}")
        print(f"Role: {user.role}")
        print(f"Password Hash: {user.password_hash[:50]}...")
        
        # Test passwords
        print("\nTesting passwords:")
        if user.username == "Waheed":
            test_pass = "admin"
        else:
            test_pass = "user"
        
        is_valid = verify_password(test_pass, user.password_hash)
        print(f"  Password '{test_pass}' → {'✅ VALID' if is_valid else '❌ INVALID'}")
        print("-" * 50)

db.close()
