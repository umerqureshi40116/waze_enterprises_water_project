#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple server runner that keeps uvicorn alive
"""
import sys
import os
import subprocess
import time

# Set UTF-8 encoding for Windows
os.environ['PYTHONIOENCODING'] = 'utf-8'

os.chdir(r'e:\water\backend')
os.environ['PYTHONPATH'] = r'e:\water\backend'

print("Starting Water Inventory Backend Server...")
print("Listening on http://0.0.0.0:8000")
print("API Docs: http://localhost:8000/api/docs")
print("\nPress Ctrl+C to stop the server\n")

try:
    subprocess.run([
        sys.executable, '-m', 'uvicorn',
        'app.main:app',
        '--host', '0.0.0.0',
        '--port', '8000'
    ], check=True)
except KeyboardInterrupt:
    print("\n\nServer stopped")
    sys.exit(0)
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
