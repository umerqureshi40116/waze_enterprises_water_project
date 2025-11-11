import requests

# Test the Render backend database connection
try:
    # Check the database via the test-db endpoint
    url = 'https://waze-enterprises-water-project-backend.onrender.com/api/v1/auth/test-db'
    headers = {'Authorization': 'Bearer test_token'}
    
    print("Testing database connection on Render...")
    response = requests.get(url, headers=headers, timeout=10)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
except Exception as e:
    print(f"Error: {e}")
