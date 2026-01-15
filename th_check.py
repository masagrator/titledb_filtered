import json
import requests
from concurrent.futures import ThreadPoolExecutor
import sys

OUTPUT = []

def checkTitleid(titleid: str):
    url = f"https://ec.nintendo.com/apps/{titleid}/TH"
    with requests.head(url, stream=True, allow_redirects=False) as response:
        status_code = response.status_code
        if (status_code == 303):
            OUTPUT.append(titleid)
            print(f"✓ {titleid}")
        elif (status_code == 403):
            print("✗ Hit rate limit, aborting...")
            sys.exit(1)
        else: print(f"✗ {titleid}: {status_code}")

with open("output/main_regions.json", "r", encoding="UTF-8") as f:
    titleids = list(json.load(f).keys())

with ThreadPoolExecutor(max_workers=1) as executor:
    executor.map(checkTitleid, titleids)

with open("output/main_regions_th.json", "w", encoding="UTF-8") as f:
    json.dump(OUTPUT, f)
