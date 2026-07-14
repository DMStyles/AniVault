import base64
import json
import httpx
from bs4 import BeautifulSoup

def rc4(key: str, data: str) -> str:
    s = list(range(256))
    j = 0
    for i in range(256):
        j = (j + s[i] + ord(key[i % len(key)])) % 256
        s[i], s[j] = s[j], s[i]
    
    i = j = 0
    out = []
    for char in data:
        i = (i + 1) % 256
        j = (j + s[i]) % 256
        s[i], s[j] = s[j], s[i]
        out.append(chr(ord(char) ^ s[(s[i] + s[j]) % 256]))
    return "".join(out)

def generate_vrf(text: str) -> str:
    encrypted = rc4("simple-hash", text)
    return base64.b64encode(encrypted.encode('latin1')).decode('utf-8')

show_id = "1642"
vrf = generate_vrf(show_id)
import urllib.parse
url = f"https://anikototv.to/ajax/episode/list/{show_id}?vrf={urllib.parse.quote(vrf)}"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://anikototv.to/watch/one-piece-odmau",
    "X-Requested-With": "XMLHttpRequest"
}
resp = httpx.get(url, headers=headers)
data = resp.json()
html = data.get("result", "")

soup = BeautifulSoup(html, "html.parser")
first_ep = soup.select_one("a")
data_ids = first_ep.get("data-ids")

# Call ajax/server/list
server_url = f"https://anikototv.to/ajax/server/list?servers={urllib.parse.quote(data_ids)}"
resp_server = httpx.get(server_url, headers=headers)
server_data = resp_server.json()
server_html = server_data.get("result", "")

server_soup = BeautifulSoup(server_html, "html.parser")
first_li = server_soup.select_one("li")
data_link_id = first_li.get("data-link-id")
print("First server data-link-id:", data_link_id[:40] + "...")

# Call ajax/server?get={data_link_id}
source_url = f"https://anikototv.to/ajax/server?get={urllib.parse.quote(data_link_id)}"
resp_source = httpx.get(source_url, headers=headers)
print("Source status:", resp_source.status_code)
source_data = resp_source.json()
print("Source response keys:", source_data.keys())
print("Source URL:", source_data.get("result", {}).get("url"))
