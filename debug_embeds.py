import asyncio
import httpx
import base64
import urllib.parse
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "X-Requested-With": "XMLHttpRequest"
}

def rc4(key, text):
    s = list(range(256)); j = 0
    for i in range(256):
        j = (j + s[i] + ord(key[i % len(key)])) % 256
        s[i], s[j] = s[j], s[i]
    i = j = 0; out = []
    for char in text:
        i = (i+1)%256; j = (j+s[i])%256; s[i], s[j] = s[j], s[i]
        out.append(chr(ord(char) ^ s[(s[i]+s[j])%256]))
    return ''.join(out)

def vrf(t): return base64.b64encode(rc4('simple-hash',t).encode('latin1')).decode()

async def resolve_url(client, link_id):
    BASE_URL = "https://anikototv.to"
    res_resp = await client.get(f"{BASE_URL}/ajax/server?get={link_id}")
    return res_resp.json().get("result", {}).get("url", "N/A")

async def test_embed(client, url):
    try:
        resp = await client.get(url, headers={"Referer": "https://anikototv.to/"})
        return resp.status_code, resp.text
    except Exception as e:
        return str(e), ""

async def main():
    BASE_URL = "https://anikototv.to"
    search_title = "Re:ZERO -Starting Life in Another World-"
    
    async with httpx.AsyncClient(headers=HEADERS, timeout=15) as client:
        # Search
        search_url = f"{BASE_URL}/filter?keyword={urllib.parse.quote(search_title)}"
        resp = await client.get(search_url)
        soup = BeautifulSoup(resp.text, "html.parser")
        
        target = None
        for item in soup.select(".ani.items .item"):
            a = item.select_one("a[href]")
            name = item.select_one(".name")
            if a and name and name.text.strip() == search_title:
                target = {"title": name.text.strip(), "url": a["href"]}
                break
                
        if not target: return
        
        detail_url = target["url"] if target["url"].startswith("http") else BASE_URL + target["url"]
        
        resp2 = await client.get(detail_url)
        show_id = BeautifulSoup(resp2.text, "html.parser").select_one("[data-id]").get("data-id")
        
        ep_vrf = vrf(show_id)
        ep_url = f"{BASE_URL}/ajax/episode/list/{show_id}?vrf={urllib.parse.quote(ep_vrf)}"
        ep_resp = await client.get(ep_url, headers={**HEADERS, "Referer": detail_url})
        ep1 = BeautifulSoup(ep_resp.json().get("result", ""), "html.parser").select_one("a[data-ids]")
        data_ids = ep1.get("data-ids")
        
        srv_url = f"{BASE_URL}/ajax/server/list?servers={data_ids}"
        srv_resp = await client.get(srv_url)
        srv_soup = BeautifulSoup(srv_resp.json().get("result", ""), "html.parser")
        
        sub_block = srv_soup.select_one('.servers .type[data-type="sub"]')
        for li in sub_block.select("li[data-link-id]"):
            name = li.text.strip()
            link_id = li.get("data-link-id")
            embed_url = await resolve_url(client, link_id)
            status, text = await test_embed(client, embed_url)
            print(f"[{name}] -> {embed_url} (Status: {status})")
            if "Error Code: 410" in text or "410" in text or "deleted" in text.lower():
                print(f"   => DETECTED 410 ERROR TEXT IN HTML!")

asyncio.run(main())
