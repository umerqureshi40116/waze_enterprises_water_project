#!/usr/bin/env python
"""Generate bcrypt hash for admin123"""
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
hash_val = pwd_context.hash('admin123')

print("=" * 70)
print("EXACT HASH FOR DATABASE:")
print("=" * 70)
print(hash_val)
print()
print(f"Length: {len(hash_val)} characters")
print()
print("=" * 70)
print("SQL UPDATE COMMAND FOR NEON:")
print("=" * 70)
print(f"UPDATE users SET password_hash = '{hash_val}' WHERE username = 'waheed';")
print()
print("=" * 70)
print("HOW TO USE:")
print("=" * 70)
print("1. Copy the hash above")
print("2. Go to Neon SQL Editor")
print("3. Run the SQL UPDATE command")
print("4. Then try logging in with: waheed / admin123")
