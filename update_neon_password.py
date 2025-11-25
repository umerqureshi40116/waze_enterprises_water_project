#!/usr/bin/env python
"""
Update password hash in production Neon database
Run this with DATABASE_URL env var pointing to Neon:
  export DATABASE_URL="postgresql://user:pass@host/db"
  python update_neon_password.py
"""
import os
from sqlalchemy import create_engine, text
from passlib.context import CryptContext

# Get DATABASE_URL from environment (set this from Neon credentials)
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("❌ DATABASE_URL not set!")
    print("Please set the DATABASE_URL environment variable with your Neon connection string")
    print("\nExample:")
    print("  set DATABASE_URL=postgresql://user:pass@ep-xxxxx.neon.tech/database?sslmode=require")
    exit(1)

print(f"📡 Connecting to: {DATABASE_URL[:80]}...")

try:
    engine = create_engine(DATABASE_URL)
    
    # Test connection
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print("✅ Database connection successful!")
    
    # Create password context
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    # Generate new hash
    password = "admin123"
    password_hash = pwd_context.hash(password[:72])
    
    print(f"\n🔐 New password hash: {password_hash[:50]}...")
    print(f"📏 Hash length: {len(password_hash)} characters")
    
    # Update in database
    with engine.connect() as conn:
        result = conn.execute(
            text("""
                UPDATE users 
                SET password_hash = :hash
                WHERE LOWER(username) = LOWER('Waheed')
            """),
            {"hash": password_hash}
        )
        conn.commit()
        print(f"\n✅ Updated {result.rowcount} user(s)")
        
        # Verify
        users = conn.execute(text("""
            SELECT id, username, LENGTH(password_hash) as hash_len
            FROM users 
            WHERE LOWER(username) = LOWER('Waheed')
        """))
        for user in users:
            print(f"✓ User: {user[1]}, ID: {user[0]}, Hash length: {user[2]}")
    
    print("\n✅ Password update complete!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
