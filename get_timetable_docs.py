import httpx
from bs4 import BeautifulSoup
import re

url = "https://animeschedule.net/api/v3/documentation"
resp = httpx.get(url)
soup = BeautifulSoup(resp.text, "html.parser")

print("Searching for Authentication details in documentation:")
# Look for any headers, keys, or auth mention in the text
text = soup.get_text()
for line in text.split("\n"):
    if any(k in line.lower() for k in ["auth", "token", "key", "header", "client"]):
        print(line.strip())
