import httpx
import asyncio
from fastapi import APIRouter

router = APIRouter()

# AniList GraphQL API - CDN-backed, fast, free, no auth needed
ANILIST = "https://graphql.anilist.co"
HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json",
}

# AniList uses genre names directly as strings
GENRE_MAP = {
    "action": "Action",
    "adventure": "Adventure",
    "comedy": "Comedy",
    "drama": "Drama",
    "ecchi": "Ecchi",
    "fantasy": "Fantasy",
    "mystery": "Mystery",
    "psychological": "Psychological",
    "romance": "Romance",
    "sci-fi": "Sci-Fi",
    "slice of life": "Slice of Life",
    "supernatural": "Supernatural",
    "thriller": "Thriller",
    "horror": "Horror",
    "sports": "Sports",
    "mecha": "Mecha",
    "music": "Music",
    "school": "School",
    "shounen": "Action",  # AniList uses demographics differently; map to closest
    "shoujo": "Romance",
    "seinen": "Seinen",
    "isekai": "Adventure",
}

MEDIA_FRAGMENT = """
  id
  title { english romaji }
  coverImage { large extraLarge }
  episodes
  format
  averageScore
  status
  startDate { year }
"""


async def anilist_post(query: str, variables: dict = None) -> dict:
    payload = {"query": query, "variables": variables or {}}
    try:
        async with httpx.AsyncClient(headers=HEADERS, timeout=20) as client:
            resp = await client.post(ANILIST, json=payload)
            if resp.status_code != 200:
                return {"errors": [{"message": f"HTTP {resp.status_code}"}], "data": None}
            return resp.json()
    except Exception as e:
        return {"errors": [{"message": str(e)}], "data": None}


def parse_media(item: dict) -> dict:
    title_en = (item.get("title") or {}).get("english") or (item.get("title") or {}).get("romaji", "")
    title_jp = (item.get("title") or {}).get("romaji", "")
    score = item.get("averageScore")
    if score:
        score = round(score / 10, 1)
    img = (item.get("coverImage") or {})
    thumbnail = img.get("extraLarge") or img.get("large", "")
    return {
        "title": title_en or title_jp,
        "title_japanese": title_jp,
        "thumbnail": thumbnail,
        "sub_episodes": str(item.get("episodes") or "?"),
        "dub_episodes": "0",
        "type": (item.get("format") or "TV").replace("_", " "),
        "score": score,
        "source": "jikan",
        "mal_id": item.get("id"),
        "year": (item.get("startDate") or {}).get("year"),
        "status": item.get("status"),
        "ep": item.get("episodes") or "?",
    }


@router.get("/by-genre")
async def get_by_genre(genre: str, page: int = 1):
    genre_lower = genre.lower()
    genre_name = GENRE_MAP.get(genre_lower, genre.title())

    query = """
    query ($genre: String, $page: Int) {
      Page(page: $page, perPage: 24) {
        pageInfo { hasNextPage currentPage lastPage }
        media(type: ANIME, genre: $genre, sort: SCORE_DESC, isAdult: false) {
          """ + MEDIA_FRAGMENT + """
        }
      }
    }
    """
    result = await anilist_post(query, {"genre": genre_name, "page": page})
    errors = result.get("errors")
    page_data = (result.get("data") or {}).get("Page") or {}
    anime_list = page_data.get("media") or []
    page_info = page_data.get("pageInfo") or {}

    if errors and not anime_list:
        return {"results": [], "genre": genre, "error": errors[0].get("message", "Unknown error")}

    return {
        "results": [parse_media(a) for a in anime_list],
        "genre": genre,
        "page": page,
        "has_next": page_info.get("hasNextPage", False),
    }


@router.get("/search")
async def search_jikan(q: str, page: int = 1):
    query = """
    query ($search: String, $page: Int) {
      Page(page: $page, perPage: 20) {
        media(type: ANIME, search: $search, sort: POPULARITY_DESC, isAdult: false) {
          """ + MEDIA_FRAGMENT + """
        }
      }
    }
    """
    result = await anilist_post(query, {"search": q, "page": page})
    anime_list = ((result.get("data") or {}).get("Page") or {}).get("media") or []
    return {"results": [parse_media(a) for a in anime_list], "source": "jikan"}


@router.get("/airing")
async def get_airing(limit: int = 20):
    query = """
    query ($perPage: Int) {
      Page(perPage: $perPage) {
        media(type: ANIME, status: RELEASING, sort: POPULARITY_DESC, isAdult: false) {
          """ + MEDIA_FRAGMENT + """
          nextAiringEpisode { episode }
        }
      }
    }
    """
    result = await anilist_post(query, {"perPage": limit})
    anime_list = ((result.get("data") or {}).get("Page") or {}).get("media") or []

    results = []
    for item in anime_list:
        r = parse_media(item)
        # Use next airing episode number if available
        nae = item.get("nextAiringEpisode")
        if nae and nae.get("episode"):
            r["ep"] = nae["episode"] - 1 if nae["episode"] > 1 else nae["episode"]
        results.append(r)

    return {"results": results}


@router.get("/all")
async def get_all_anime(page: int = 1, letter: str = None):
    if letter and letter != "#":
        # Search by letter prefix
        query = """
        query ($search: String, $page: Int) {
          Page(page: $page, perPage: 24) {
            pageInfo { hasNextPage currentPage lastPage }
            media(type: ANIME, search: $search, sort: TITLE_ENGLISH_DESC, isAdult: false) {
              """ + MEDIA_FRAGMENT + """
            }
          }
        }
        """
        variables = {"search": letter, "page": page}
    else:
        # Default: popular anime
        query = """
        query ($page: Int) {
          Page(page: $page, perPage: 24) {
            pageInfo { hasNextPage currentPage lastPage }
            media(type: ANIME, sort: POPULARITY_DESC, isAdult: false) {
              """ + MEDIA_FRAGMENT + """
            }
          }
        }
        """
        variables = {"page": page}

    result = await anilist_post(query, variables)
    errors = result.get("errors")
    page_data = ((result.get("data") or {}).get("Page")) or {}
    anime_list = page_data.get("media") or []
    page_info = page_data.get("pageInfo") or {}

    if errors and not anime_list:
        return {
            "results": [],
            "error": errors[0].get("message", "Unknown error"),
            "page": page,
            "has_next": False,
            "total_pages": 1,
        }

    return {
        "results": [parse_media(a) for a in anime_list],
        "page": page,
        "has_next": page_info.get("hasNextPage", False),
        "total_pages": page_info.get("lastPage", 1),
        "letter": letter,
    }
