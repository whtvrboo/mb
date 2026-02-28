import asyncio
import json
from httpx import AsyncClient

async def run():
    async with AsyncClient(base_url="http://test") as client:
        print("Testing...")

if __name__ == "__main__":
    asyncio.run(run())
