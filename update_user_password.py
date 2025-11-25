#!/usr/bin/env python
"""Update user password in Neon database"""
import os
from sqlalchemy import create_engine, text
from passlib.context import CryptContext

# Get DATABASE_URL from .env or environment
DATABASE_URL = os.getenv("DATABASE_URL") or "postgresql://postgres:9876@localhost:5432/water_inventory"

print(f"📡 Connecting to: {DATABASE_URL[:60]}...")

try:
    engine = create_engine(DATABASE_URL)
    
    # Create password context
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    # Generate new hash
    password = "admin123"
    password_hash = pwd_context.hash(password[:72])  # Truncate to 72 bytes for bcrypt
    
    print(f"🔐 New password hash: {password_hash[:50]}...")
    print(f"📏 Hash length: {len(password_hash)} characters")
    
    with engine.connect() as conn:
        # Update the waheed user (case-sensitive)
        result = conn.execute(
            text("""
                UPDATE users 
                SET password_hash = :hash
                WHERE username = :username
            """),
            {"hash": password_hash, "username": "Waheed"}
        )
        conn.commit()
        print(f"✅ Updated {result.rowcount} user(s)")
        
        # Verify
        users = conn.execute(text("SELECT id, username, password_hash FROM users WHERE username = :username"), {"username": "Waheed"})
        for user in users:
            print(f"✓ User: {user[1]}, Password hash length: {len(user[2])}")
    
    print("✅ Password update complete!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
