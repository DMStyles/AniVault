import httpx
from bs4 import BeautifulSoup
import re

urls = [
    "https://animeschedule.net/api/v3/documentation/anime",
    "https://animeschedule.net/api/v3/documentation/animelists"
]

for url in urls:
    print("=" * 60)
    print("Fetching:", url)
    resp = httpx.get(url)
    print("Status:", resp.status_code)
    soup = BeautifulSoup(resp.text, "html.parser")
    # Search for all elements that look like API endpoint names or headers
    print("API Endpoints:")
    for el in soup.select(".api-doc-names, .api-doc-name, .request-header-name"):
        print(el.text.strip())
