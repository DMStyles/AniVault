import httpx
import datetime
import re
from fastapi import APIRouter
from bs4 import BeautifulSoup

from database import get_translation, save_translation
import asyncio

router = APIRouter()

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

async def fetch_english_title(title: str) -> str:
    cached = get_translation(title)
    if cached:
        return cached

    query = """
    query ($search: String) {
      Media (search: $search, type: ANIME) {
        title {
          english
          romaji
        }
      }
    }
    """
    url = "https://graphql.anilist.co"
    try:
        async with httpx.AsyncClient(timeout=8) as client:
            resp = await client.post(url, json={"query": query, "variables": {"search": title}})
            if resp.status_code == 200:
                data = resp.json()
                media = data.get("data", {}).get("Media", {})
                if media:
                    eng = media.get("title", {}).get("english")
                    rom = media.get("title", {}).get("romaji")
                    final_title = eng or rom or title
                    save_translation(title, final_title)
                    return final_title
    except Exception:
        pass

    return title

@router.get("/timetables")
async def get_timetables(weeksAfter: int = 0):
    dt = datetime.date.today() + datetime.timedelta(weeks=weeksAfter)
    year = dt.year
    week = dt.isocalendar()[1]
    
    url = f"https://animeschedule.net/?year={year}&week={week}"
    
    async with httpx.AsyncClient(headers=HEADERS, timeout=15) as client:
        resp = await client.get(url)
        
    if resp.status_code != 200:
        return {"error": f"Failed to fetch schedule: status {resp.status_code}"}
        
    soup = BeautifulSoup(resp.text, "html.parser")
    schedule = {
        "monday": [],
        "tuesday": [],
        "wednesday": [],
        "thursday": [],
        "friday": [],
        "saturday": [],
        "sunday": []
    }
    
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    for day in days:
        column = soup.select_one(f".timetable-column.{day}")
        if column:
            shows = column.select(".timetable-column-show")
            grouped = {}
            for show in shows:
                route = show.get("route") or ""
                
                title_bar = show.select_one(".show-title-bar")
                title_small = show.select_one(".show-title-small, .show-title-super-small")
                img_el = show.select_one(".show-poster")
                
                title = "Unknown"
                if title_bar:
                    title = title_bar.text.strip()
                elif title_small:
                    title = title_small.text.strip()
                elif img_el and img_el.get("alt"):
                    alt = img_el.get("alt")
                    if "Official promotional poster for" in alt:
                        title = alt.replace("Official promotional poster for", "").strip()
                    else:
                        title = alt.strip()
                
                if "\n" in title or "PM" in title or "AM" in title:
                    if img_el and img_el.get("alt"):
                        alt = img_el.get("alt")
                        if "Official promotional poster for" in alt:
                            title = alt.replace("Official promotional poster for", "").strip()
                        else:
                            title = alt.strip()
                    else:
                        title = route.replace("-", " ").title()
                
                ep_el = show.select_one(".show-episode")
                time_el = show.select_one(".show-air-time")
                air_type_el = show.select_one(".air-type-text")
                
                ep = ep_el.text.strip() if ep_el else ""
                time_str = time_el.text.strip() if time_el else ""
                air_type = air_type_el.text.strip() if air_type_el else ""
                
                img = img_el.get("data-src") or img_el.get("src") if img_el else ""
                if img == "data:image/gif;base64,R0lGODlhAQABAAD/ACwAAAAAAQABAAACADs=":
                    img = img_el.get("data-src") or ""
                
                episode_number = None
                if ep:
                    ep_clean = ep.lower().replace("ep", "").replace("f", "").strip()
                    if ep_clean.isdigit():
                        episode_number = int(ep_clean)
                
                time_clean = re.sub(r'\s+', ' ', time_str).strip()
                
                key = route or title.lower()
                
                if key not in grouped:
                    grouped[key] = {
                        "title": title,
                        "imageVersionRoute": img,
                        "episode": ep,
                        "episodeNumber": episode_number,
                        "airings": []
                    }
                
                if air_type and time_clean:
                    grouped[key]["airings"].append({
                        "type": air_type,
                        "time": time_clean
                    })
                elif time_clean:
                    grouped[key]["airings"].append({
                        "type": "SUB" if not air_type else air_type,
                        "time": time_clean
                    })
            
            async def resolve_title(v):
                v["titleEnglish"] = await fetch_english_title(v["title"])
            
            await asyncio.gather(*[resolve_title(val) for val in grouped.values()])
            
            for val in grouped.values():
                if not val["airings"]:
                    val["airings"].append({
                        "type": "SUB",
                        "time": "Time TBA"
                    })
                schedule[day.lower()].append(val)
                
    return schedule

@router.get("/anime/{slug}")
async def get_anime(slug: str):
    url = f"https://animeschedule.net/api/v3/anime/{slug}"
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(url)
    if resp.status_code == 200:
        return resp.json()
    return {"error": "Not found", "status": resp.status_code}
