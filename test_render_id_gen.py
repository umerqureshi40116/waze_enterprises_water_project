import requests

# Test the expense ID generation endpoint
try:
    url = 'https://waze-enterprises-water-project-backend.onrender.com/api/v1/reports/count/exp'
    headers = {'Authorization': 'Bearer test_token'}
    
    print("Testing expense ID generation endpoint...")
    response = requests.get(url, headers=headers, timeout=10)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
