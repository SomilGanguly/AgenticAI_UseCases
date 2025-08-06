import os
import httpx
from dotenv import load_dotenv

load_dotenv()

async def get_azure_token():
    url = f"https://login.microsoftonline.com/{os.getenv('AZURE_TENANT_ID')}/oauth2/v2.0/token"
    data = {
        'client_id': os.getenv('AZURE_CLIENT_ID'),
        'client_secret': os.getenv('AZURE_CLIENT_SECRET'),
        'scope': 'https://management.azure.com/.default',
        'grant_type': 'client_credentials',
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, data=data)
        try:
            response.raise_for_status()
            token = response.json()["access_token"]
            print("Azure token acquired")
            return token
        except Exception as e:
            print("Failed to get Azure token")
            print("Status:", response.status_code)
            print("Response:", response.text)
            raise
