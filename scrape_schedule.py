import httpx
from bs4 import BeautifulSoup

url = "https://animeschedule.net/"
print("Fetching:", url)
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}
resp = httpx.get(url, headers=headers, timeout=15)
print("Status:", resp.status_code)
soup = BeautifulSoup(resp.text, "html.parser")

# Let's check for any elements containing schedule data
print("Timetable elements:")
timetable = soup.select("#timetable")
print("Timetable element count:", len(timetable))

# Print first 500 characters of timetable element if found
if timetable:
    print(str(timetable[0])[:1000])
else:
    # Print some divs
    print("Found divs with class:")
    for el in soup.select("div[class]")[:10]:
        print(el.get("class"))
