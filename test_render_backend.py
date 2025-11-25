"""
Test what's happening on the Render backend
Try to connect and see what error we get
"""
import requests

BACKEND_URL = "https://waze-enterprises-water-project-backend.onrender.com"

print("🔍 Testing Render Backend Configuration:")
print("=" * 80)

# Test 1: Health check
print("\n1. Health Check:")
try:
    resp = requests.get(f"{BACKEND_URL}/health", timeout=10)
    print(f"   Status: {resp.status_code}")
    print(f"   Response: {resp.text}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 2: Config endpoint
print("\n2. Config Endpoint:")
try:
    resp = requests.get(f"{BACKEND_URL}/config", timeout=10)
    print(f"   Status: {resp.status_code}")
    data = resp.json()
    print(f"   Response: {data}")
    if data.get("database_url_set"):
        print(f"   ✅ DATABASE_URL is SET in Render")
    else:
        print(f"   ❌ DATABASE_URL is NOT SET in Render")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 3: Test DB endpoint
print("\n3. Database Test Endpoint:")
try:
    resp = requests.get(f"{BACKEND_URL}/api/v1/auth/test-db", timeout=10)
    print(f"   Status: {resp.status_code}")
    print(f"   Response: {resp.text}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 4: Try login
print("\n4. Login Test (with waheed/admin123):")
try:
    resp = requests.post(
        f"{BACKEND_URL}/api/v1/auth/login",
        json={"username": "waheed", "password": "admin123"},
        timeout=10
    )
    print(f"   Status: {resp.status_code}")
    if resp.status_code == 200:
        print(f"   ✅ LOGIN SUCCESSFUL!")
        print(f"   Response: {resp.json()}")
    else:
        print(f"   ❌ LOGIN FAILED")
        print(f"   Response: {resp.text}")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "=" * 80)
