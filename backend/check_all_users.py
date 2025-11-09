"""Check ALL users in Neon database"""
import os
from sqlalchemy import create_engine, text

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://neondb_owner:npg_IYnkVx8vrdy3@ep-old-grass-ahuzyjob-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require")

engine = create_engine(DATABASE_URL)

try:
    with engine.connect() as conn:
        print("📋 ALL USERS IN NEON DATABASE:")
        print("=" * 100)
        
        result = conn.execute(text("""
            SELECT id, username, email, LENGTH(password_hash) as hash_len, 
                   password_hash as hash_preview
            FROM users
            ORDER BY created_at DESC
        """))
        
        rows = result.fetchall()
        
        if not rows:
            print("❌ No users found!")
        else:
            for i, row in enumerate(rows, 1):
                user_id, username, email, hash_len, hash_val = row
                print(f"\n{i}. ID: {user_id}")
                print(f"   Username: {username}")
                print(f"   Email: {email}")
                print(f"   Hash Length: {hash_len} characters")
                if hash_len > 72:
                    print(f"   ❌ PROBLEM: Hash is > 72 bytes ({hash_len})")
                elif hash_len == 60:
                    print(f"   ✅ GOOD: Hash is 60 bytes (correct bcrypt)")
                else:
                    print(f"   ⚠️  UNUSUAL: Hash is {hash_len} bytes")
                print(f"   Hash: {hash_val[:50]}...")
        
        print("\n" + "=" * 100)
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    engine.dispose()
