#!/usr/bin/env python
"""Check what's in the Neon database"""
import os
from sqlalchemy import create_engine, text, inspect

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("❌ DATABASE_URL not set!")
    exit(1)

print(f"📡 Connecting to: {DATABASE_URL[:80]}...")

try:
    engine = create_engine(DATABASE_URL)
    
    # Test connection
    with engine.connect() as conn:
        # Check tables
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        print(f"\n📊 Tables in database: {tables}")
        
        # Check if users table exists
        if 'users' in tables:
            result = conn.execute(text("SELECT COUNT(*) as count FROM users"))
            count = result.fetchone()[0]
            print(f"👥 Users in database: {count}")
            
            # List all users
            result = conn.execute(text("""
                SELECT id, username, LENGTH(password_hash) as hash_len, password_hash
                FROM users
            """))
            print("\n📋 All users:")
            for row in result:
                print(f"  - ID: {row[0]}, Username: {row[1]}, Hash length: {row[2]}, Hash starts: {row[3][:40]}...")
        else:
            print("❌ users table not found!")
            
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
