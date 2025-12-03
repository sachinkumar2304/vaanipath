import httpx
import asyncio

async def test():
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "http://localhost:8001/podcast/generate",
                json={"text": "Test podcast", "language": "english"},
                timeout=120.0
            )
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
        except Exception as e:
            print(f"Error: {e}")

asyncio.run(test())
