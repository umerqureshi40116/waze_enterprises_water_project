#!/usr/bin/env python
"""Test if hash works"""
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# The exact hash
test_hash = "$2b$12$KOuvHgcJ/Kfgri/hJB8tT.RgWEfxKdUFLmnqQKIbwzYCBpefHV.m."
password = "admin123"

print("Testing hash verification:")
print(f"Hash: {test_hash}")
print(f"Password: {password}")
print()

try:
    result = pwd_context.verify(password, test_hash)
    print(f"✅ Result: {result}")
    if result:
        print("✅ PASSWORD MATCHES - Hash is correct!")
    else:
        print("❌ PASSWORD DOES NOT MATCH")
except Exception as e:
    print(f"❌ Error: {e}")
