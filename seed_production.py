"""
Seed production database with items via API
"""
import requests
import json

# Backend URL
BACKEND_URL = "https://waze-enterprises-water-project-backend.onrender.com/api/v1"

# Login
print("🔐 Logging in...")
login_response = requests.post(
    f"{BACKEND_URL}/auth/login",
    json={"username": "waheed", "password": "admin123"}
)
token = login_response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# Items to seed
items = [
    {
        "id": "Item_Preform_500A",
        "name": "PET Preform 500ml A",
        "type": "preform",
        "size": "500ml",
        "grade": "A",
        "unit": "pcs (1000)"
    },
    {
        "id": "Item_Preform_1500A",
        "name": "PET Preform 1500ml A",
        "type": "preform",
        "size": "1500ml",
        "grade": "A",
        "unit": "pcs (500)"
    },
    {
        "id": "Item_Bottle_500A",
        "name": "500ml Bottle A",
        "type": "bottle",
        "size": "500ml",
        "grade": "A",
        "unit": "pcs"
    },
    {
        "id": "Item_Bottle_1500A",
        "name": "1500ml Bottle A",
        "type": "bottle",
        "size": "1500ml",
        "grade": "A",
        "unit": "pcs"
    },
    {
        "id": "Item_Cap_Blue",
        "name": "Blue Cap",
        "type": "cap",
        "size": "Standard",
        "grade": "A",
        "unit": "pcs"
    },
    {
        "id": "Item_Label_Standard",
        "name": "Standard Label",
        "type": "label",
        "size": "Standard",
        "grade": "A",
        "unit": "sheets"
    }
]

# Create items
print("📦 Creating items...")
for item in items:
    response = requests.post(
        f"{BACKEND_URL}/stocks/items",
        json=item,
        headers=headers
    )
    if response.status_code == 201:
        print(f"✅ Created: {item['name']}")
    else:
        print(f"❌ Failed: {item['name']} - {response.text}")

print("✅ Done!")
