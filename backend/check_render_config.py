"""Check if backend is properly configured on Render"""
import os
import sys

print("🔍 Backend Configuration Check:")
print("=" * 60)

# Check DATABASE_URL
db_url = os.getenv("DATABASE_URL", "NOT_SET")
print(f"\n1. DATABASE_URL environment variable:")
if db_url == "NOT_SET":
    print(f"   ❌ NOT SET - Backend will fail to connect!")
else:
    print(f"   ✅ SET")
    print(f"   Preview: {db_url[:80]}...")

# Check other env vars
print(f"\n2. Other important variables:")
print(f"   SECRET_KEY: {'✅ SET' if os.getenv('SECRET_KEY') else '❌ NOT SET'}")
print(f"   ENVIRONMENT: {os.getenv('ENVIRONMENT', 'unknown')}")

# List all env vars
print(f"\n3. All environment variables ({len(os.environ)} total):")
for key in sorted(os.environ.keys())[:10]:
    print(f"   - {key}")

print("\n" + "=" * 60)
if db_url == "NOT_SET":
    print("⚠️  ACTION REQUIRED: Set DATABASE_URL in Render dashboard!")
else:
    print("✅ Backend appears properly configured")
