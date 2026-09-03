import requests
import json

api_key = "621c318eb5f20da9fccff0c90d21dddc70842d75"
url = "https://google.serper.dev/search"
payload = json.dumps({"q": "flights from NY to London tomorrow"})
headers = {
    'X-API-KEY': api_key,
    'Content-Type': 'application/json'
}

response = requests.post(url, headers=headers, data=payload)
print("STATUS CODE:", response.status_code)
if response.status_code == 200:
    data = response.json()
    if "organic" in data and len(data["organic"]) > 0:
        print("SERPER API IS WORKING! Found", len(data["organic"]), "results.")
    else:
        print("SERPER API WORKS, but no organic results found.")
else:
    print("SERPER API FAILED:", response.text)
