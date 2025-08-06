import aiofiles
import httpx

async def download_file(url: str, dest_path: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        async with aiofiles.open(dest_path, 'wb') as f:
            await f.write(response.content)
