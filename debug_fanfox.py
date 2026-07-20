"""
Test FanFox.net chapter image fetching approaches.
FanFox uses JavaScript to load images - we need to find their internal API.
"""
import httpx
import re
import json
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://fanfox.net/",
}

def test_fanfox():
    BASE = "https://fanfox.net"
    
    # Test 1: Fetch a chapter page and look for image URLs
    # One Piece Chapter 1
    chapter_url = f"{BASE}/manga/one_piece/v01/c001/1.html"
    print(f"\n=== TEST 1: Chapter page HTML ===\nURL: {chapter_url}")
    
    r = httpx.get(chapter_url, headers=HEADERS, timeout=15, follow_redirects=True)
    print(f"Status: {r.status_code}")
    soup = BeautifulSoup(r.text, "html.parser")
    
    # Look for image in the reader
    imgs = soup.select("img")
    for img in imgs[:5]:
        src = img.get("src", "")
        if "mfcdn" in src or "fanfox" in src:
            print(f"  Image found: {src}")
    
    # Look for JS variables containing image list
    scripts = soup.select("script")
    for script in scripts:
        text = script.string or ""
        if "imageList" in text or "imgurl" in text or "chapterimage" in text or "mfcdn" in text:
            print(f"\n  JS with images found (first 500 chars):\n  {text[:500]}")
            break
    
    # Test 2: Try the chapterimage.ashx endpoint
    # Need to find chapter ID first
    print("\n=== TEST 2: Looking for chapter ID ===")
    for script in scripts:
        text = script.string or ""
        # Look for chapter ID patterns
        m = re.search(r'["\'](chapterid|chapter_id|cid)["\']?\s*[=:]\s*(\d+)', text, re.I)
        if m:
            print(f"  Found {m.group(1)}: {m.group(2)}")
        m2 = re.search(r'var\s+(\w*id\w*)\s*=\s*(\d+)', text, re.I)
        if m2:
            print(f"  Found var {m2.group(1)} = {m2.group(2)}")
    
    # Test 3: Try the mobile version which tends to be simpler
    print("\n=== TEST 3: Mobile version ===")
    mobile_url = f"https://m.fanfox.net/manga/one_piece/v01/c001/1.html"
    r3 = httpx.get(mobile_url, headers=HEADERS, timeout=15, follow_redirects=True)
    print(f"Status: {r3.status_code}")
    soup3 = BeautifulSoup(r3.text, "html.parser")
    imgs3 = soup3.select("img.reader-main-img, #image, .image img")
    for img in imgs3:
        print(f"  Image: {img.get('src')}")
    
    # Also check for data attributes
    for el in soup3.select("[data-original], [data-src]"):
        src = el.get("data-original") or el.get("data-src")
        if src and ("mfcdn" in src or "fanfox" in src):
            print(f"  Data-src: {src}")
    
    # Test 4: Try their search
    print("\n=== TEST 4: Search ===")
    r4 = httpx.get(f"{BASE}/search?title=one+piece&page=1", headers=HEADERS, timeout=15, follow_redirects=True)
    print(f"Status: {r4.status_code}")
    soup4 = BeautifulSoup(r4.text, "html.parser")
    # Various possible result containers
    for sel in [".manga-list-4 li", ".manga-list-1 li", ".result li", ".search-result li"]:
        results = soup4.select(sel)
        if results:
            print(f"  Found {len(results)} results with selector '{sel}'")
            for r_ in results[:3]:
                a = r_.select_one("a[href]")
                title = r_.select_one(".title, p, h3")
                if a:
                    print(f"    - {title.text.strip() if title else a.text.strip()}: {a['href']}")
            break
    
    # Test 5: Try the chapterimage.ashx API directly
    print("\n=== TEST 5: chapterimage.ashx API ===")
    # The CID might be in the URL or page - let's try known IDs
    # One Piece CID is typically around 1000 range
    test_url = f"{BASE}/chapterimage.ashx?cid=36862&page=1&key=&_=1600000000"
    r5 = httpx.get(test_url, headers={**HEADERS, "X-Requested-With": "XMLHttpRequest"}, timeout=10)
    print(f"Status: {r5.status_code}")
    print(f"Response (first 300): {r5.text[:300]}")
    
    # Test 6: Look at the manga detail page for One Piece
    print("\n=== TEST 6: Manga detail + chapters ===")
    r6 = httpx.get(f"{BASE}/manga/one_piece/", headers=HEADERS, timeout=15, follow_redirects=True)
    print(f"Status: {r6.status_code}")
    soup6 = BeautifulSoup(r6.text, "html.parser")
    
    # Find chapter list
    chapters = soup6.select(".detail-main-list li a[href]")
    print(f"  Found {len(chapters)} chapters")
    if chapters:
        print(f"  First: {chapters[0].get('href')} - {chapters[0].text.strip()}")
        print(f"  Last: {chapters[-1].get('href')} - {chapters[-1].text.strip()}")
    
    # Find meta info
    title = soup6.select_one(".detail-info-right-title-font")
    status = soup6.select_one(".detail-info-right-title-tip")
    score = soup6.select_one(".detail-info-right-title-font")
    author = soup6.select_one(".detail-info-right-say a")
    synopsis = soup6.select_one(".detail-info-description")
    genres = soup6.select(".detail-info-right-tag-list a")
    cover = soup6.select_one(".detail-info-cover-img")
    
    print(f"\n  Title: {title.text.strip() if title else 'N/A'}")
    print(f"  Status: {status.text.strip() if status else 'N/A'}")
    print(f"  Author: {author.text.strip() if author else 'N/A'}")
    print(f"  Cover: {cover.get('src') if cover else 'N/A'}")
    print(f"  Genres: {[g.text.strip() for g in genres[:5]]}")
    print(f"  Synopsis (50 chars): {synopsis.text.strip()[:50] if synopsis else 'N/A'}")

test_fanfox()
