"""
Alternative: Use curl to set DATABASE_URL via Render API
This avoids the UI wrapping issue
"""

import subprocess
import json

# Your Render service ID - you can find this in the URL
# Format: https://dashboard.render.com/web/srv_XXXXX
SERVICE_ID = "srv_xxxxxxxx"  # UPDATE THIS
RENDER_API_KEY = "rkey_xxxxxxxx"  # UPDATE THIS

DATABASE_URL = "postgresql://neondb_owner:npg_IYnkVx8vrdy3@ep-old-grass-ahuzyjob-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

# You would run this command to set env var via Render API:
# curl -X PATCH https://api.render.com/v1/services/{SERVICE_ID}/env-vars \
#   -H "Authorization: Bearer {RENDER_API_KEY}" \
#   -H "Content-Type: application/json" \
#   -d '{
#     "envVars": [
#       {
#         "key": "DATABASE_URL",
#         "value": "postgresql://neondb_owner:npg_IYnkVx8vrdy3@ep-old-grass-ahuzyjob-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
#       }
#     ]
#   }'

print("⚠️  To use Render API, you need:")
print("1. Your Service ID (from dashboard URL: srv_xxxxx)")
print("2. Your Render API Key (from https://dashboard.render.com/account/api-tokens)")
print("\nThen run the curl command above.")
print("\nOr use the Render dashboard with these steps:")
print("1. Copy the DATABASE_URL carefully")
print("2. Make sure NO line breaks are included")
print("3. If UI wraps it visually, that's OK - it's just display")
print("4. Click Save and wait for redeploy")
