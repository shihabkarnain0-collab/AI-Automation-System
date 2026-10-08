import requests

response = requests.get("https://example.com", timeout=10)

print("Status:", response.status_code)
print("Connection: OK")
