import httpx
from bs4 import BeautifulSoup

url = "https://animeschedule.net/"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}
resp = httpx.get(url, headers=headers)
soup = BeautifulSoup(resp.text, "html.parser")
column = soup.select_one(".timetable-column.Wednesday")
if column:
    show = column.select_one(".timetable-column-show")
    print("--- SHOW ELEMENT HTML ---")
    print(show.prettify()[:1500])
