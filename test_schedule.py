import httpx

url = "https://animeschedule.net/api/v3/timetables"
print("Fetching url:", url)
resp = httpx.get(url, timeout=15)
print("Status:", resp.status_code)
if resp.status_code == 200:
    data = resp.json()
    print("Type of data:", type(data))
    if isinstance(data, list):
        print("Total items:", len(data))
        if len(data) > 0:
            print("First item keys:", data[0].keys())
            print("First item title:", data[0].get("title"))
            print("First item episode:", data[0].get("episode"))
            print("First item date:", data[0].get("airingDate"))
    elif isinstance(data, dict):
        print("Keys:", data.keys())
