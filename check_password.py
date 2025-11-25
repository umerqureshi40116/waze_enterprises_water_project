#!/usr/bin/env python
"""Check password hash in database"""
from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql://postgres:9876@localhost:5432/water_inventory"
engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    result = conn.execute(text("""
        SELECT username, LENGTH(password_hash) as hash_len, password_hash 
        FROM users 
        WHERE username = 'Waheed'
    """))
    
    row = result.fetchone()
    if row:
        print(f"Username: {row[0]}")
        print(f"Hash length: {row[1]}")
        print(f"Hash: {row[2]}")
        print(f"Hash starts with: {row[2][:30]}...")
    else:
        print("No user found")
