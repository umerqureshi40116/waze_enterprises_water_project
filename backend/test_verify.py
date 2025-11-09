"""Test password verification with new hash"""
from app.core.security import verify_password

# Test with the new hash from Neon
hash_val = "$2b$12$krN90PLKnT471U.bKVQVC.wlbQSbITX6U9Jn7RTNUH9mlVdYWZY6q"
password = "admin123"

print(f"Testing password verification:")
print(f"  Hash: {hash_val}")
print(f"  Password: {password}")
print(f"  Hash length: {len(hash_val)}")

try:
    result = verify_password(password, hash_val)
    print(f"  ✅ Result: {result}")
except Exception as e:
    print(f"  ❌ Error: {e}")
    import traceback
    traceback.print_exc()
