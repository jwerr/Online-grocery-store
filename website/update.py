import requests

BASE = "http://127.0.0.1:5000/"
headers = {'Content-Type': 'application/json'}

# Data to update the category
data = {
    "category_id": "new1",
    "user_id": 12
}

# Make the PUT request with the correct Content-Type header and URL path
response = requests.put(BASE + "api/user/12/category/new", json=data, headers=headers)

# Print the response
print(response.json())
