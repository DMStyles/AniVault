import httpx
from bs4 import BeautifulSoup
import re

headers_browser = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Referer": "https://anikototv.to/",
}

# Fetch vidtube embed page and look for m3u8 or direct stream links
vidtube_url = "https://vidtube.site/stream/V3JaTDBHOTFaSE1zOWNyR01JdUZJd1c0QTJHQlE4bmtZaWVDbkZ6Y3g1OXdwTXVRbUtPdlBkZFQ4U0tGMXI1OQ/sub"
resp = httpx.get(vidtube_url, headers=headers_browser, timeout=15, follow_redirects=True)
print("Status:", resp.status_code)
print("Final URL:", str(resp.url))

# Look for m3u8 links
m3u8_matches = re.findall(r'https?://[^\'"<>\s]+\.m3u8[^\'"<>\s]*', resp.text)
print(f"m3u8 links found: {len(m3u8_matches)}")
for m in m3u8_matches[:5]:
    print(" ", m)

# Look for any direct video sources
mp4_matches = re.findall(r'https?://[^\'"<>\s]+\.mp4[^\'"<>\s]*', resp.text)
print(f"mp4 links found: {len(mp4_matches)}")
for m in mp4_matches[:5]:
    print(" ", m)

# Look for source tags
soup = BeautifulSoup(resp.text, "html.parser")
for src in soup.select("source"):
    print("source:", src)

# Look for file/src patterns
file_patterns = re.findall(r'"file"\s*:\s*"([^"]+)"', resp.text)
src_patterns = re.findall(r'"src"\s*:\s*"([^"]+)"', resp.text)
print("file patterns:", file_patterns[:5])
print("src patterns:", src_patterns[:5])

print("\nHTML snippet (2000 chars):")
print(resp.text[:2000])
