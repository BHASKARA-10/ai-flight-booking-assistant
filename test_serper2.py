import requests
import json

api_key = "621c318eb5f20da9fccff0c90d21dddc70842d75"
url = "https://google.serper.dev/search"
payload = json.dumps({
  "q": "flights from HYD to MUM next sunday"
})
headers = {
  'X-API-KEY': api_key,
  'Content-Type': 'application/json'
}
response = requests.request("POST", url, headers=headers, data=payload)
with open("serper_out.json", "w", encoding="utf-8") as f:
    f.write(response.text)

# Also test if there's a flights endpoint
url2 = "https://google.serper.dev/flights"
payload2 = json.dumps({
  "q": "flights from HYD to MUM next sunday"
})
response2 = requests.request("POST", url2, headers=headers, data=payload2)
with open("serper_flights.json", "w", encoding="utf-8") as f:
    f.write(response2.text)
