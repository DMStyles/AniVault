import httpx
import asyncio
from fastapi import APIRouter

router = APIRouter()

# Jikan v4 - free MyAnimeList API, no auth needed
JIKAN = "https://api.jikan.moe/v4"

# Map genre names to MyAnimeList genre IDs
# Supernatural (37) is a theme, not a genre - use genres + themes param
GENRE_IDS = {
    "action": 1,
    "adventure": 2,
    "comedy": 4,
    "drama": 8,
    "ecchi": 9,
    "fantasy": 10,
    "mystery": 7,
    "psychological": 40,
    "romance": 22,
    "sci-fi": 24,
    "slice of life": 36,
    "supernatural": 37,
    "thriller": 41,
    "horror": 14,
    "sports": 30,
    "mecha": 18,
    "music": 19,
    "school": 23,
    "shounen": 27,
    "shoujo": 25,
    "seinen": 42,
    "isekai": 62,
}

# These genres need to use "themes" param in Jikan v4 instead of "genres"
THEME_IDS = {
    "supernatural": 37,
    "school": 23,
    "music": 19,
    "isekai": 62,
}

HEADERS = {
    "User-Agent": "AniVault/1.0 (anime desktop app)",
    "Accept": "application/json",
}


async def jikan_get(url: str, retries: int = 3) -> dict:
    """Fetch from Jikan with retry on rate limit."""
    for attempt in range(retries):
        try:
            async with httpx.AsyncClient(headers=HEADERS, timeout=20) as client:
                resp = await client.get(url)
                if resp.status_code == 429:
                    # Rate limited — wait and retry
                    wait = 1.5 * (attempt + 1)
                    await asyncio.sleep(wait)
                    continue
                if resp.status_code != 200:
                    return {"error": f"API returned {resp.status_code}", "data": []}
                return resp.json()
        except Exception as e:
            if attempt < retries - 1:
                await asyncio.sleep(1)
            else:
                return {"error": str(e), "data": []}
    return {"error": "Rate limited. Please try again in a moment.", "data": []}


def parse_anime(item: dict) -> dict:
    title_en = item.get("title_english") or item.get("title", "")
    title_jp = item.get("title", "")
    return {
        "title": title_en or title_jp,
        "title_japanese": title_jp,
        "url": item.get("url", ""),
        "thumbnail": item.get("images", {}).get("jpg", {}).get("large_image_url", ""),
        "sub_episodes": str(item.get("episodes") or "?"),
        "dub_episodes": "0",
        "type": item.get("type", "TV"),
        "score": item.get("score"),
        "source": "jikan",
        "mal_id": item.get("mal_id"),
        "year": item.get("year"),
        "status": item.get("status"),
    }


@router.get("/by-genre")
async def get_by_genre(genre: str, page: int = 1):
    genre_lower = genre.lower()
    genre_id = GENRE_IDS.get(genre_lower)

    if not genre_id:
        return {"results": [], "genre": genre, "error": "Unknown genre"}

    # Supernatural and other themes need the `themes` param
    if genre_lower in THEME_IDS:
        url = f"{JIKAN}/anime?genres={genre_id}&order_by=score&sort=desc&limit=24&page={page}&sfw=true"
        data = await jikan_get(url)
        if not data.get("data"):
            # Try with themes param instead
            url2 = f"{JIKAN}/anime?themes={genre_id}&order_by=score&sort=desc&limit=24&page={page}&sfw=true"
            data = await jikan_get(url2)
    else:
        url = f"{JIKAN}/anime?genres={genre_id}&order_by=score&sort=desc&limit=24&page={page}&sfw=true"
        data = await jikan_get(url)

    if "error" in data and not data.get("data"):
        return {"results": [], "genre": genre, "error": data["error"]}

    results = [parse_anime(item) for item in data.get("data", [])]
    pagination = data.get("pagination", {})

    return {
        "results": results,
        "genre": genre,
        "page": page,
        "has_next": pagination.get("has_next_page", False),
    }


@router.get("/search")
async def search_jikan(q: str, page: int = 1):
    url = f"{JIKAN}/anime?q={q}&limit=20&page={page}&order_by=popularity&sfw=true"
    data = await jikan_get(url)

    if "error" in data and not data.get("data"):
        return {"results": [], "error": data.get("error")}

    return {"results": [parse_anime(item) for item in data.get("data", [])], "source": "jikan"}


@router.get("/airing")
async def get_airing(limit: int = 20):
    """Get currently airing anime."""
    url = f"{JIKAN}/anime?status=airing&order_by=popularity&sort=asc&limit={limit}&sfw=true"
    data = await jikan_get(url)

    results = []
    for item in data.get("data", []):
        r = parse_anime(item)
        r["ep"] = item.get("episodes") or "?"
        results.append(r)

    return {"results": results}


@router.get("/all")
async def get_all_anime(page: int = 1, letter: str = None):
    """Get all anime in alphabetical order."""
    # Use top-rated anime by default (more reliable than alphabetical which can be slow)
    if letter and letter != "#":
        params = f"order_by=title&sort=asc&limit=24&page={page}&letter={letter}&sfw=true"
    else:
        params = f"order_by=popularity&sort=asc&limit=24&page={page}&sfw=true"

    url = f"{JIKAN}/anime?{params}"
    data = await jikan_get(url)

    if "error" in data and not data.get("data"):
        return {"results": [], "error": data.get("error"), "page": page, "has_next": False, "total_pages": 1}

    pagination = data.get("pagination", {})
    return {
        "results": [parse_anime(item) for item in data.get("data", [])],
        "page": page,
        "has_next": pagination.get("has_next_page", False),
        "total_pages": pagination.get("last_visible_page", 1),
        "letter": letter,
    }
