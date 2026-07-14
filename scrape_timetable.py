import httpx
from bs4 import BeautifulSoup

url = "https://animeschedule.net/"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}
resp = httpx.get(url, headers=headers)
soup = BeautifulSoup(resp.text, "html.parser")

timetable = soup.select_one("#timetable")
if timetable:
    # Print the class names of all elements inside timetable
    classes = set()
    for el in timetable.select("*"):
        cls = el.get("class")
        if cls:
            classes.update(cls)
    print("Classes found inside #timetable:", sorted(list(classes)))
    
    # Print some of the elements
    print("\nSome sample elements:")
    for el in timetable.select("div")[:15]:
        print(el.get("id"), el.get("class"))
