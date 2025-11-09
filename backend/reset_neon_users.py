"""
Reset Neon database users with plain text passwords
This script clears out old hashes and stores passwords as plain text
"""
import os
from sqlalchemy import create_engine, text

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://neondb_owner:npg_IYnkVx8vrdy3@ep-old-grass-ahuzyjob-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require")

def reset_users():
    """Delete existing users and recreate with plain text passwords"""
    engine = create_engine(DATABASE_URL)
    
    try:
        with engine.connect() as conn:
            # Delete existing users
            print("🗑️ Deleting old users from database...")
            conn.execute(text("DELETE FROM users"))
            conn.commit()
            
            # Set plain text passwords
            waheed_password = "admin123"
            umer_password = "user123"
            
            print(f"� Setting plain text passwords:")
            print(f"   waheed: {waheed_password}")
            print(f"   umer:   {umer_password}")
            
            # Insert fresh users with plain text passwords
            print("➕ Inserting fresh users...")
            conn.execute(text("""
                INSERT INTO users (id, username, email, password_hash, role, created_at)
                VALUES 
                ('waheed', 'waheed', 'waheed@company.com', :waheed_pass, 'admin', NOW()),
                ('umer', 'umer', 'umer@company.com', :umer_pass, 'user', NOW())
            """), {"waheed_pass": waheed_password, "umer_pass": umer_password})
            conn.commit()
            
            # Verify
            result = conn.execute(text("SELECT id, username, password_hash FROM users"))
            rows = result.fetchall()
            
            print("\n✅ Users reset successfully!")
            print("\n📋 Verification:")
            for row in rows:
                print(f"   {row[0]:10} | {row[1]:15} | Password: {row[2]}")
            
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
