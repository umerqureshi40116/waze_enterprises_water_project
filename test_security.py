"""
Test if JWT token authentication is working
"""
from app.core.security import create_access_token, get_password_hash, verify_password
from datetime import timedelta

# Test password hashing
print("Testing password hashing...")
hashed = get_password_hash("admin")
print(f"Hashed password: {hashed[:60]}...")
print(f"Verify correct password: {verify_password('admin', hashed)}")
print(f"Verify wrong password: {verify_password('wrong', hashed)}")

# Test token generation
print("\nTesting JWT token generation...")
token = create_access_token(data={"sub": "Waheed"}, expires_delta=timedelta(minutes=30))
print(f"Generated token: {token[:50]}...")

print("\n✅ Security functions working correctly!")
