import httpx

try:
    resp = httpx.get("http://127.0.0.1:8643/jikan/all", timeout=10)
    print("STATUS:", resp.status_code)
    print("BODY:", resp.text[:500])
except Exception as e:
    print("ERROR:", e)
