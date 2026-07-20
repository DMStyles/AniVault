import asyncio
import httpx
import json

async def main():
    # The Cat and the Dragon data_ids for episode 4. I'll just search for it directly without vrf
    url = "https://anikototv.to/ajax/episode/list/19302" # I don't know the exact ID
    print("Cannot easily get the data_ids without VRF which requires the exact HTML.")
    
asyncio.run(main())
