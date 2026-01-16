import json
import requests
from concurrent.futures import ThreadPoolExecutor
import sys

REGIONS = ["MY", "SG", "TH", "TW"]

region = ""

FOLDERS = ["output", "output2"]

def checkTitleid(titleid: str):
    global region
    url = f"https://ec.nintendo.com/apps/{titleid}/{region}"
    with requests.head(url, stream=True, allow_redirects=False) as response:
        status_code = response.status_code
        if (status_code == 303):
            OUTPUT[f"{titleid}"]["True"].append(region)
            print(f"✓ {titleid}")
        elif (status_code == 403):
            print("✗ Hit rate limit. Aborting...")
            sys.exit(1)
        else: 
            print(f"✗ {titleid}: {status_code}")
            OUTPUT[f"{titleid}"]["False"].append(region)

try:
    with open(f"{folder}/main_regions_alt.json", "r", encoding="UTF-8") as f:
        OUTPUT = json.load(f)
except:
    OUTPUT = {}
    
for folder in FOLDERS:
    with open(f"{folder}/main_regions.json", "r", encoding="UTF-8") as f:
        main_titleids = list(json.load(f).keys())
    
    keys = list(OUTPUT.keys())
    
    titleids_temp = [x for x in main_titleids if x not in keys]

    for titleid in titleids_temp:
        OUTPUT[f"{titleid}"] = {"True": [], "False": []}

    for m_region in REGIONS:
        region = m_region
        titleids = [x for x in main_titleids if (m_region not in OUTPUT[f"{titleid}"]["True"] and m_region not in OUTPUT[f"{titleid}"]["False"])]
        
        with ThreadPoolExecutor(max_workers=1) as executor:
            executor.map(checkTitleid, titleids)
        
    with open(f"{folder}/main_regions_alt.json", "w", encoding="UTF-8") as f:
        json.dump(OUTPUT, f, indent="\t")
