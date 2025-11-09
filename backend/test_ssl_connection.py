#!/usr/bin/env python3
"""
Test SSL connection to Neon database with new settings
"""
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from app.core.config import settings
from sqlalchemy import text
from app.db.database import SessionLocal

print("=" * 60)
print("🔐 Testing SSL Connection to Neon Database")
print("=" * 60)

print(f"\n📍 Database URL Preview: {settings.DATABASE_URL[:60]}...")

try:
    print("\n⏳ Attempting to connect...")
    db = SessionLocal()
    
    # Test simple query
    print("📊 Running test query...")
    result = db.execute(text("SELECT 1 as test")).fetchone()
    
    if result:
        print(f"✅ Connection successful!")
        print(f"✅ Test query returned: {result[0]}")
        
        # Try to query users
        print("\n👤 Checking for test user...")
        user_result = db.execute(
            text("SELECT username, email FROM users WHERE username ILIKE 'waheed' LIMIT 1")
        ).fetchone()
        
        if user_result:
            print(f"✅ User found: {user_result[0]} ({user_result[1]})")
        else:
            print("⚠️  Test user 'waheed' not found in database")
        
        db.close()
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED - SSL Connection is working!")
        print("=" * 60)
        
    else:
        print("❌ Test query returned no results")
        
except Exception as e:
    print(f"\n❌ Connection failed with error:")
    print(f"   Error Type: {type(e).__name__}")
    print(f"   Error Message: {str(e)}")
    print("\n⚠️  This error might occur if:")
    print("   • DATABASE_URL environment variable is not set")
    print("   • Neon database URL is incorrect")
    print("   • Network connectivity issues")
    print("   • SSL certificate issues")
    
    import traceback
    print("\n📋 Full traceback:")
    traceback.print_exc()
