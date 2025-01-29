import requests

QDRANT_URL = "https://49f65a5e-6012-409b-b1ac-5a70af9dceb3.europe-west3-0.gcp.cloud.qdrant.io:6333"
QDRANT_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIiwiZXhwIjoxNzQ1OTE5NDYzfQ._u1W4HiEiMpRHCKdbN7MeIwLtVwyXxaiZS2WF5YbUHM"
# Get collection information
response = requests.get(f"{QDRANT_URL}/collections", headers={"Authorization": f"Bearer {QDRANT_API_KEY}"})

print(response.json())

response = requests.get(
    f"{QDRANT_URL}/collections/documents/points/count",
    headers={"Authorization": f"Bearer {eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIiwiZXhwIjoxNzQ1OTE5NDYzfQ._u1W4HiEiMpRHCKdbN7MeIwLtVwyXxaiZS2WF5YbUHM}"}
)

print(response.json())
