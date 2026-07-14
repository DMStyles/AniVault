import httpx

resp = httpx.get("https://animetake.tv/", timeout=15)
print("Status:", resp.status_code)
print("Preview:", resp.text[:200])
