import httpx
import datetime
import re
from fastapi import APIRouter
from bs4 import BeautifulSoup

router = APIRouter()

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

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
            for show in shows:
                title_el = show.select_one(".show-title-small, .show-title-super-small, h3")
                ep_el = show.select_one(".show-episode")
                time_el = show.select_one(".show-air-time")
                img_el = show.select_one(".show-poster")
                
                title = title_el.text.strip() if title_el else "Unknown"
                ep = ep_el.text.strip() if ep_el else ""
                time_str = time_el.text.strip() if time_el else ""
                img = img_el.get("data-src") or img_el.get("src") if img_el else ""
                
                # Extract episode number
                episode_number = None
                if ep:
                    ep_clean = ep.lower().replace("ep", "").strip()
                    if ep_clean.isdigit():
                        episode_number = int(ep_clean)
                
                # Format time cleanly
                time_clean = re.sub(r'\s+', ' ', time_str).strip()
                
                show_data = {
                    "title": title,
                    "time": time_clean,
                    "episodeNumber": episode_number,
                    "imageVersionRoute": img
                }
                schedule[day.lower()].append(show_data)
                
    return schedule

@router.get("/anime/{slug}")
async def get_anime(slug: str):
    url = f"https://animeschedule.net/api/v3/anime/{slug}"
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(url)
    if resp.status_code == 200:
        return resp.json()
    return {"error": "Not found", "status": resp.status_code}
