#!/usr/bin/env python
"""Test bcrypt password verification"""
import os
from passlib.context import CryptContext
from sqlalchemy import create_engine, text

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("❌ DATABASE_URL not set!")
    exit(1)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

print("🔐 Testing bcrypt password verification...")
print()

try:
    # Get the hash from database
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT password_hash FROM users WHERE username = 'waheed'"))
        row = result.fetchone()
        if not row:
            print("❌ User 'waheed' not found!")
            exit(1)
        
        stored_hash = row[0]
        print(f"📦 Stored hash: {stored_hash}")
        print(f"📏 Hash length: {len(stored_hash)}")
        print()
        
        # Test the password
        test_password = "admin123"
        print(f"🧪 Testing password: '{test_password}'")
        print(f"📏 Password length: {len(test_password)}")
        
        # Truncate to 72 bytes like we do in the app
        test_password_truncated = test_password[:72]
        print(f"📏 Truncated password length: {len(test_password_truncated)}")
        print()
        
        try:
            result = pwd_context.verify(test_password_truncated, stored_hash)
            print(f"✅ Password verification result: {result}")
            if result:
                print("✅ PASSWORD IS CORRECT!")
            else:
                print("❌ PASSWORD IS WRONG!")
        except Exception as e:
            print(f"❌ Verification error: {e}")
            print()
            print("Trying to hash the password to generate a new hash...")
            try:
                new_hash = pwd_context.hash(test_password_truncated)
                print(f"✅ New hash generated: {new_hash}")
                print(f"📏 New hash length: {len(new_hash)}")
                
                # Test the new hash
                result = pwd_context.verify(test_password_truncated, new_hash)
                print(f"✅ New hash verification: {result}")
            except Exception as e2:
                print(f"❌ Error generating new hash: {e2}")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
