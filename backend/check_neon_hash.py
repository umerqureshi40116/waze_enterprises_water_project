#!/usr/bin/env python
"""Check what password hash is actually in Neon database"""
import os
from sqlalchemy import create_engine, text

# Your Neon connection string
DATABASE_URL = "postgresql://neondb_owner:npg_IYnkVx8vrdy3@ep-old-grass-ahuzyjob-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

print("Connecting to Neon database...")
print()

try:
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT username, password_hash, LENGTH(password_hash) as hash_len
            FROM users
            WHERE username = 'waheed'
        """))
        
        row = result.fetchone()
        if row:
            username, hash_val, hash_len = row
            print(f"Username: {username}")
            print(f"Hash length: {hash_len} characters")
            print(f"Hash value: {hash_val}")
            print()
            print("=" * 80)
            if hash_len == 60:
                print("✅ Hash looks correct (60 characters)")
            elif hash_len > 100:
                print(f"❌ HASH IS TOO LONG ({hash_len} chars) - This is causing the error!")
                print("   Need to update it to the correct 60-character hash")
            else:
                print(f"⚠️  Hash length is unusual ({hash_len} chars)")
            print("=" * 80)
        else:
            print("❌ No user 'waheed' found in database!")
            
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
