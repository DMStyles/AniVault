import httpx
from bs4 import BeautifulSoup

url = "https://animeschedule.net/"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}
resp = httpx.get(url, headers=headers)
soup = BeautifulSoup(resp.text, "html.parser")

days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
for day in days:
    print("\n" + "=" * 30)
    print("Day:", day)
    column = soup.select_one(f".timetable-column.{day}")
    if column:
        shows = column.select(".timetable-column-show")
        print("Total shows:", len(shows))
        for show in shows[:5]:
            title_el = show.select_one(".show-title-small, .show-title-super-small, h3")
            ep_el = show.select_one(".show-episode")
            time_el = show.select_one(".show-air-time")
            img_el = show.select_one(".show-poster")
            a_el = show.select_one("a.show-link")
            
            title = title_el.text.strip() if title_el else "Unknown"
            ep = ep_el.text.strip() if ep_el else "Unknown"
            time = time_el.text.strip() if time_el else "Unknown"
            img = img_el.get("data-src") or img_el.get("src") if img_el else ""
            href = a_el.get("href") if a_el else ""
            
            print(f"- Title: {title}")
            print(f"  Ep: {ep}")
            print(f"  Time: {time}")
            print(f"  Img: {img}")
            print(f"  Link: {href}")
            print("-" * 20)
