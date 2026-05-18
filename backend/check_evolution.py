import os
import asyncio
import httpx
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env'))

base_url = "https://evolution-api-production-cbc6.up.railway.app"
api_key = "ab41348576f3ea5d6e2937104c6702a57f9c3a9adbbaa9b18335fb30a222667c"
instance = "DMN"

headers = {
    "apikey": api_key,
    "Content-Type": "application/json"
}

async def check_api():
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            print("1. Checking Evolution API server status...")
            resp = await client.get(f"{base_url}/instance/fetchInstances", headers=headers)
            print(f"Server Response Code: {resp.status_code}")
            
            if resp.status_code == 200:
                instances = resp.json()
                print(f"Instances found: {[inst.get('instance', {}).get('instanceName') for inst in instances]}")
                
                print(f"\n2. Checking connection status for instance '{instance}'...")
                state_resp = await client.get(f"{base_url}/instance/connectionState/{instance}", headers=headers)
                if state_resp.status_code == 200:
                    state = state_resp.json()
                    print(f"Connection State: {state.get('instance', {}).get('state')}")
                else:
                    print(f"Failed to get state. Status: {state_resp.status_code}, Body: {state_resp.text}")
            else:
                print(f"Failed to fetch instances. Status: {resp.status_code}, Body: {resp.text}")
                
    except Exception as e:
        print(f"Error checking Evolution API: {e}")

if __name__ == "__main__":
    asyncio.run(check_api())
