"""
Fix production database items - delete old ones and create with proper IDs
"""
import requests
import json

BACKEND_URL = "https://waze-enterprises-water-project-backend.onrender.com/api/v1"

# Login
print("🔐 Logging in...")
login_response = requests.post(
    f"{BACKEND_URL}/auth/login",
    json={"username": "waheed", "password": "admin123"}
)
token = login_response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# Get all items
print("📦 Getting existing items...")
items_response = requests.get(
    f"{BACKEND_URL}/stocks/items",
    headers=headers
)
items = items_response.json()
print(f"Found {len(items)} items")

# Delete all items
print("🗑️  Deleting all items...")
for item in items:
    if item.get("id"):  # Only delete if has ID
        response = requests.delete(
            f"{BACKEND_URL}/stocks/items/{item['id']}",
            headers=headers
        )
        print(f"Deleted: {item['name']}")
    else:
        print(f"⚠️  Skipped (no ID): {item['name']}")

# Create items with proper IDs
print("\n✨ Creating items with proper IDs...")
items_to_create = [
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

for item in items_to_create:
    response = requests.post(
        f"{BACKEND_URL}/stocks/items",
        json=item,
        headers=headers
    )
    if response.status_code in [201, 200]:
        print(f"✅ Created: {item['name']} (ID: {item['id']})")
    else:
        print(f"❌ Failed: {item['name']} - {response.status_code}: {response.text}")

print("\n✅ Done! Items fixed.")

# Verify
print("\n🔍 Verifying...")
items_response = requests.get(
    f"{BACKEND_URL}/stocks/items",
    headers=headers
)
items = items_response.json()
print(f"Total items now: {len(items)}")
for item in items:
    print(f"  - {item['id']}: {item['name']}")
