import httpx
from fastapi import APIRouter
from bs4 import BeautifulSoup
import sys
import os
import re

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import DynamicBaseURL
from client import SharedClientContext

# Monkey-patch httpx.AsyncClient to enable connection pooling
httpx.AsyncClient = SharedClientContext

router = APIRouter()

BASE_URL = DynamicBaseURL("animetake_domain", "https://animetake.tv")
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

@router.get("/search")
async def search_animetake(q: str):
    url = f"{BASE_URL}/search/?search={q}"
    async with httpx.AsyncClient(headers=HEADERS, timeout=15) as client:
        resp = await client.get(url)
    soup = BeautifulSoup(resp.text, "html.parser")
    results = []
    for item in soup.select(".component-animelist")[:20]:
        a = item.select_one(".animeposter a[href]")
        img = item.select_one(".animeposter img")
        name = item.select_one(".animename")
        type_el = item.select_one(".year") # fallback year/type info
        if a and name:
            href = a["href"]
            img_src = ""
            if img:
                img_src = img.get("data-src", img.get("src", ""))
                if img_src and not img_src.startswith("http"):
                    img_src = BASE_URL + img_src
            results.append({
                "title": name.get_text(strip=True),
                "url": href if href.startswith("http") else BASE_URL + href,
                "thumbnail": img_src,
                "sub_episodes": "?",
                "dub_episodes": "0",
                "type": type_el.get_text(strip=True) if type_el else "TV",
                "source": "animetake",
            })
    return {"results": results, "source": "animetake"}


@router.get("/episodes")
async def get_episodes(url: str):
    async with httpx.AsyncClient(headers=HEADERS, timeout=15) as client:
        resp = await client.get(url)
    soup = BeautifulSoup(resp.text, "html.parser")
    
    title_el = soup.select_one("h2")
    title = title_el.get_text(strip=True) if title_el else "Unknown"
    
    thumb_el = soup.select_one("img.main-poster")
    thumbnail = ""
    if thumb_el:
        src = thumb_el.get("data-src", thumb_el.get("src", ""))
        thumbnail = src if src.startswith("http") else BASE_URL + src
        
    episodes = []
    seen_urls = set()
    for a in soup.select("a[href*='/watch/']"):
        ep_href = a.get("href", "")
        if ep_href in seen_urls:
            continue
        seen_urls.add(ep_href)
        
        animename_el = a.select_one(".animename")
        if animename_el:
            ep_text = animename_el.get_text(strip=True)
            # Find episode number
            num_match = re.search(r'Episode\s+([A-Za-z0-9.-]+)', ep_text, re.IGNORECASE)
            ep_num = num_match.group(1) if num_match else "1"
            
            # Find sub-episode title if any
            sub_title_el = a.select_one(".animeinfo_bottom span")
            sub_title = sub_title_el.get_text(strip=True) if sub_title_el else ""
            
            full_title = f"Episode {ep_num}"
            if sub_title:
                full_title += f" - {sub_title}"
                
            episodes.append({
                "number": ep_num,
                "title": full_title,
                "url": ep_href if ep_href.startswith("http") else BASE_URL + ep_href,
            })
            
    # Sort episodes by number if possible
    try:
        episodes.sort(key=lambda x: float(x["number"]))
    except:
        pass
        
    return {"title": title, "thumbnail": thumbnail, "episodes": episodes, "source": "animetake"}
