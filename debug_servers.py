import httpx
from bs4 import BeautifulSoup
import yt_dlp

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "X-Requested-With": "XMLHttpRequest",
    "Referer": "https://anikototv.to/",
}

data_ids = "aEFiQk8vbUM0aFpzb08vSW8zYjNuSVNaS25wUHpXNnhWL2RBMTFvQUJQdVQ4eUJheDEzMzdpaThUQ1JtKzhCaVVZR1ZTTDB1QXJIVjFCVi9VWXMvS28zMmhZOUJWYVpiajdMY0pJYW5Qc1lWczJtZFhzYkYwZlhIQk52T21sK2ZRZWIzMUYrZSsyc1QrKytLQW9QcFFXZkdwWVEydzFYM0I0SXE1OEhxY3pJPQ"

server_list_url = f"https://anikototv.to/ajax/server/list?servers={data_ids}"
resp = httpx.get(server_list_url, headers=headers, timeout=15)
soup = BeautifulSoup(resp.json().get("result", ""), "html.parser")

for li in soup.select("li[data-link-id]"):
    link_id = li.get("data-link-id")
    sv_id = li.get("data-sv-id")
    print(f"\n--- Server ID: {sv_id} ---")
    source_url = f"https://anikototv.to/ajax/server?get={link_id}"
    resp2 = httpx.get(source_url, headers=headers, timeout=15)
    if resp2.status_code == 200:
        res_data = resp2.json().get("result", {})
        embed_url = res_data.get("url")
        print("Embed URL:", embed_url)
        
        # Test yt-dlp on it
        ydl_opts = {"quiet": True, "skip_download": True}
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(embed_url, download=False)
                print("yt-dlp SUCCESS! Formats:", len(info.get("formats", [])))
        except Exception as e:
            print("yt-dlp error:", str(e).splitlines()[0])
