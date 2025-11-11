import requests

# Test the extra-expenditures endpoint on Render
try:
    url = 'https://waze-enterprises-water-project-backend.onrender.com/api/v1/extra-expenditures/'
    headers = {'Authorization': 'Bearer test_token'}
    
    print(f"Testing: {url}")
    response = requests.get(url, headers=headers, timeout=10)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    print(f"Response Body: {response.text[:500] if response.text else 'No content'}")
    
except Exception as e:
    print(f"Error: {e}")
    print(f"Error Type: {type(e)}")
