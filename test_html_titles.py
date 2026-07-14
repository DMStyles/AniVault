import httpx

url = "https://animeschedule.net/"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}
resp = httpx.get(url, headers=headers)
html = resp.text
# Check if english name of otonari exists in html
search_word = "Spoils Me Rotten"
if search_word.lower() in html.lower():
    print("Found 'Spoils Me Rotten'!")
    # Print around it
    idx = html.lower().index(search_word.lower())
    print(html[idx-100:idx+100])
else:
    print("Not found in html.")
