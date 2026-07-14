import httpx
from bs4 import BeautifulSoup
import re

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Referer": "https://anikototv.to/",
}

embed_url = "https://megaplay.buzz/stream/s-5/141683/sub"
resp = httpx.get(embed_url, headers=headers, timeout=15)
print("Status:", resp.status_code)
print("m3u8 found:", len(re.findall(r'https?://[^\'"<>\s]+\.m3u8[^\'"<>\s]*', resp.text)))
print("file found:", re.findall(r'"file"\s*:\s*"([^"]+)"', resp.text))
