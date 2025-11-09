"""
Reset Neon database users with fresh password hashes
This script clears out old corrupted hashes and regenerates them fresh
"""
import os
from sqlalchemy import create_engine, text
from app.core.security import get_password_hash

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://neondb_owner:npg_IYnkVx8vrdy3@ep-old-grass-ahuzyjob-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require")

def reset_users():
    """Delete existing users and recreate with fresh hashes"""
    engine = create_engine(DATABASE_URL)
    
    try:
        with engine.connect() as conn:
            # Delete existing users
            print("🗑️ Deleting old users from database...")
            conn.execute(text("DELETE FROM users"))
            conn.commit()
            
            # Generate fresh hashes
            waheed_hash = get_password_hash("admin123")
            umer_hash = get_password_hash("user123")
            
            print(f"🔐 Generated fresh hashes:")
            print(f"   waheed: {waheed_hash[:30]}... (len: {len(waheed_hash)})")
            print(f"   umer:   {umer_hash[:30]}... (len: {len(umer_hash)})")
            
            # Insert fresh users
            print("➕ Inserting fresh users...")
            conn.execute(text("""
                INSERT INTO users (id, username, email, password_hash, role, created_at)
                VALUES 
                ('waheed', 'waheed', 'waheed@company.com', :waheed_hash, 'admin', NOW()),
                ('umer', 'umer', 'umer@company.com', :umer_hash, 'user', NOW())
            """), {"waheed_hash": waheed_hash, "umer_hash": umer_hash})
            conn.commit()
            
            # Verify
            result = conn.execute(text("SELECT id, username, LENGTH(password_hash) as hash_len FROM users"))
            rows = result.fetchall()
            
            print("\n✅ Users reset successfully!")
            print("\n📋 Verification:")
            for row in rows:
                print(f"   {row[0]:10} | {row[1]:15} | Hash length: {row[2]}")
            
            print("\n📝 Test Credentials:")
            print("   Username: waheed")
            print("   Password: admin123")
            print("\n   Username: umer")
            print("   Password: user123")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        engine.dispose()

if __name__ == "__main__":
    reset_users()
