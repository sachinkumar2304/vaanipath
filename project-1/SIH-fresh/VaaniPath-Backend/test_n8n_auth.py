import httpx
import base64
import asyncio
import json

async def test_n8n():
    username = "Gyanify"
    password = "Gyanify123"
    
    url = "https://zaiddd.app.n8n.cloud/webhook/8be78b34-dbc8-418a-83b0-044991ac14c2"
    
    # Payload matching the example exactly
    payload = {
        "current-skills": "java,python",
        "goal": "SDE",
        "language": "english"
    }
    
    print(f"Testing URL: {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    async with httpx.AsyncClient() as client:
        try:
            print("\n--- Attempt 1: httpx.BasicAuth ---")
            response = await client.post(
                url, 
                json=payload, 
                auth=(username, password),
                timeout=30.0
            )
            print(f"Status Code: {response.status_code}")
            print(f"Headers: {response.headers}")
            print(f"Response Body: {response.text}")
            
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_n8n())
