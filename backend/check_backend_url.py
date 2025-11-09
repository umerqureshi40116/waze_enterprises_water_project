#!/usr/bin/env python
"""Check what database URL the backend is using"""
import os

print("Environment variables that might be DATABASE_URL:")
print("=" * 80)

# Check different possible sources
db_url_env = os.getenv("DATABASE_URL")
db_url_local = "postgresql://postgres:9876@localhost:5432/water_inventory"

print(f"DATABASE_URL env var: {db_url_env}")
print()

if db_url_env:
    if "neon" in db_url_env.lower():
        print("✅ Using NEON database (correct for production)")
    elif "localhost" in db_url_env:
        print("❌ Using LOCAL database (wrong for production)")
    else:
        print("⚠️  Using unknown database")
else:
    print("❌ DATABASE_URL NOT SET - will use default fallback")
    print(f"   Default fallback: {db_url_local}")
    print("   This is a LOCAL database, not Neon!")

print()
print("=" * 80)
print("SOLUTION:")
print("=" * 80)
print("You MUST set DATABASE_URL environment variable in Render:")
print("  Key: DATABASE_URL")
print("  Value: postgresql://neondb_owner:npg_IYnkVx8vrdy3@ep-old-grass-ahuzyjob-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require")
