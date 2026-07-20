import asyncio
import httpx

async def test_genre():
    tag_id = "eabc5b4c-6aff-42f3-b657-3e90cbd00b75"  # Supernatural
    params = {
        "limit": 20,
        "contentRating[]": ["safe", "suggestive", "erotica"],
        "includes[]": ["cover_art"],
        "order[relevance]": "desc",
        "includedTags[]": [tag_id],
    }
    headers = {"User-Agent": "KamiWatch/2.0.4"}
    async with httpx.AsyncClient(timeout=15, headers=headers) as client:
        r = await client.get("https://api.mangadex.org/manga", params=params)
        print("Status:", r.status_code)
        data = r.json()
        print("Total:", data.get("total"))
        print("Count:", len(data.get("data", [])))
        if data.get("data"):
            print("First title:", list(data["data"][0]["attributes"]["title"].values())[0])

async def test_demo():
    params = {
        "limit": 20,
        "contentRating[]": ["safe", "suggestive", "erotica"],
        "includes[]": ["cover_art"],
        "order[relevance]": "desc",
        "publicationDemographic[]": ["shounen"],
    }
    headers = {"User-Agent": "KamiWatch/2.0.4"}
    async with httpx.AsyncClient(timeout=15, headers=headers) as client:
        r = await client.get("https://api.mangadex.org/manga", params=params)
        print("Demo Status:", r.status_code)
        data = r.json()
        print("Demo Total:", data.get("total"))

asyncio.run(test_genre())
asyncio.run(test_demo())
