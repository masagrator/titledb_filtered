import json
import os
import shutil
import lzma
import glob
from pathlib import Path
import xml.etree.ElementTree as ET
from datetime import datetime
import requests
import sys

files = [
    "US.en",
    "GB.en",
    "JP.ja",
    "FR.fr",
    "DE.de",
    "ES.es",
    "IT.it",
    "NL.nl",
    "CA.fr",
    "PT.pt",
    "RU.ru",
    "KR.ko",
    "HK.zh",
    "BR.pt",
    
    "PL.en",
    "AR.en",
    "AR.es",
    "AT.de",
    "AU.en",
    "BE.fr",
    "BE.nl",
    "BG.en",
    "BR.en",
    "CA.en",
    "CH.de",
    "CH.fr",
    "CH.it",
    "CL.en",
    "CL.es",
    "CN.en",
    "CN.zh",
    "CO.en",
    "CO.es",
    "CY.en",
    "CZ.en",
    "DK.en",
    "EE.en",
    "FI.en",
    "GR.en",
    "HR.en",
    "HU.en",
    "IE.en",
    "IL.en",
    "JP.en",
    "LT.en",
    "LU.de",
    "LU.fr",
    "LV.en",
    "MT.en",
    "MX.en",
    "NO.en",
    "NZ.en",
    "PE.en",
    "PE.es",
    "RO.en",
    "SE.en",
    "SI.en",
    "SK.en",
    "US.es",
    "ZA.en"
]

shutil.rmtree("output/titleid", ignore_errors=True)
shutil.rmtree("output2/titleid", ignore_errors=True)
os.makedirs("output/titleid")
os.makedirs("output2/titleid")
LIST = {}
LIST_REGIONS = {}
NSUIDs = []
LIST2 = {}
LIST2_REGIONS = {}
NS2UIDs = []

for x in range(len(files)):

    file = open("titledb/%s.json" % files[x], "r", encoding="UTF-8")
    DUMP = json.load(file)
    file.close()

    keys = list(DUMP.keys())

    num = len(keys)
    print("Processing", files[x])
    added = []
    added2 = []
    for i in range(num):
        entry = DUMP[keys[i]]
        entry_id = DUMP[keys[i]]["id"]
        if (entry_id == None):
            continue
        ending = int("0x" + entry_id[12:16], base=16)
        if (ending % 0x2000 != 0):
            continue
        if (entry["publisher"] == None):
            continue
        isOunce = False
        if (entry_id[0:2] == "04"):
            isOunce = True
        if (isOunce == False):
            if (entry_id in LIST.keys()):
                if ((entry["name"] not in LIST[entry_id]) and (entry_id not in added)):
                    LIST[entry_id].append(entry["name"])
                if ((files[x][0:2] not in LIST_REGIONS[entry_id]) and (entry_id not in added)):
                    LIST_REGIONS[entry_id].append(files[x][0:2])
                added.append(entry_id)
                continue
        else:
            if (entry_id in LIST2.keys()):
                if ((entry["name"] not in LIST2[entry_id]) and (entry_id not in added2)):
                    LIST2[entry_id].append(entry["name"])
                if ((files[x][0:2] not in LIST2_REGIONS[entry_id]) and (entry_id not in added2)):
                    LIST2_REGIONS[entry_id].append(files[x][0:2])
                added2.append(entry_id)
                continue            
        if (isOunce == True):
            LIST2[entry_id] = [entry["name"]]
            LIST2_REGIONS[entry_id] = [files[x][0:2]]
            NS2UIDs.append(entry["nsuId"])
            added2.append(entry_id)
        else: 
            if (entry["name"] == "Borderlands: The Handsome Collection"): entry["name"] = "Borderlands 2: Game of the Year Edition"
            LIST[entry_id] = [entry["name"]]
            LIST_REGIONS[entry_id] = [files[x][0:2]]
            NSUIDs.append(entry["nsuId"])
            added.append(entry_id)
        entry = {}
        entry["bannerUrl"] = DUMP[keys[i]]["bannerUrl"]
        entry["iconUrl"] = DUMP[keys[i]]["iconUrl"]
        entry["publisher"] = DUMP[keys[i]]["publisher"]
        entry["screenshots"] = DUMP[keys[i]]["screenshots"]
        entry["releaseDate"] = DUMP[keys[i]]["releaseDate"]
        if (DUMP[keys[i]]["size"] == 0):
            entry["size"] = "Unknown"
        elif (DUMP[keys[i]]["size"] < 1024*1024*1024):
            entry["size"] = "%.0f MiB" % (DUMP[keys[i]]["size"] / (1024*1024))
        else:
            entry["size"] = "%.2f GiB" % (DUMP[keys[i]]["size"] / (1024*1024*1024))
        if (isOunce == False):
            new_file = open("output/titleid/%s.json" % entry_id, "w", encoding="UTF-8")
        else: new_file = open("output2/titleid/%s.json" % entry_id, "w", encoding="UTF-8")
        json.dump(entry, new_file, indent="\t", ensure_ascii=True)
        new_file.close()

new_file = open("output/nsuIDs.json", "w", encoding="UTF-8")
json.dump(NSUIDs, new_file, ensure_ascii=False)
new_file.close()
new_file = open("output2/nsuIDs.json", "w", encoding="UTF-8")
json.dump(NS2UIDs, new_file, ensure_ascii=False)
new_file.close()

"""
# Scrap Japanese eshop
print("Scrapping Japanese eshop...")

tree = ET.parse('switch.xml')
root = tree.getroot()

base_url = "https://store-jp.nintendo.com/item/software/D"

NSUIDs.extend(NS2UIDs)

missing_NSUIDs = []

if os.path.isfile("missing_new/NSUIDs.json"):
    file = open("missing_new/NSUIDs.json", "r", encoding="UTF-8")
    missing_NSUIDs = json.load(file)
    NSUIDs.extend(missing_NSUIDs)
    file.close()
else: 
    os.makedirs("missing_new/titleid", exist_ok=True)
    os.makedirs("missing_new/titleid2", exist_ok=True)

for title in root.findall('TitleInfo'):
    link = title.find('LinkURL').text
    
    nsuID = link.replace("/titles/", "")

    if (nsuID in NSUIDs or nsuID in missing_NSUIDs):
        continue

    new_url = base_url + nsuID

    response = requests.get(new_url)
    if response.status_code == 200:
        html_source_code = response.text
        pos = html_source_code.find("c_applicationId\":")
        if (pos != -1):
            pos += 18
            titleid = html_source_code[pos:pos+16]
            isSwitch2 = False
            if titleid.startswith("0400"):
                isSwitch2 = True
            missing_NSUIDs.append(int(nsuID, base=10))
            if os.path.isfile("output/titleid/%s.json" % titleid):
                continue
            entry = {}
            entry["name"] = title.find('TitleName').text
            entry["publisher"] = title.find('MakerName').text
            date_obj = datetime.strptime(title.find('SalesDate').text, "%Y.%m.%d")
            entry["releaseDate"] = int(date_obj.strftime("%Y%m%d"))
            entry["bannerUrl"] = title.find('ScreenshotImgURL').text
            entry["iconUrl"] = ""
            entry["screenshots"] = []
            entry["size"] = 0
            if (isSwitch2): file = open("missing_new/titleid2/%s.json" % (titleid), "w", encoding="UTF-8")
            else: file = open("missing_new/titleid/%s.json" % (titleid), "w", encoding="UTF-8")
            json.dump(entry, file, indent="\t", ensure_ascii=True)
            file.close()

file = open("missing_new/NSUIDs.json", "w", encoding="UTF-8")
json.dump(missing_NSUIDs, file, ensure_ascii=False)
file.close()
"""

missing_games = glob.glob("missing/*.json")

for i in range(len(missing_games)):
    titleid = Path(missing_games[i]).stem
    if (titleid in LIST):
        continue
    file = open(missing_games[i], "r", encoding="UTF-8")
    DUMP = json.load(file)
    file.close()
    if isinstance(DUMP["name"], list):
        LIST[titleid] = DUMP["name"]
    else:
        LIST[titleid] = [DUMP["name"]]
    entry = {}
    entry["bannerUrl"] = DUMP["bannerUrl"]
    entry["iconUrl"] = DUMP["iconUrl"]
    entry["publisher"] = DUMP["publisher"]
    entry["screenshots"] = DUMP["screenshots"]
    entry["releaseDate"] = DUMP["releaseDate"]
    if (("size" not in DUMP.keys()) or (DUMP["size"] == 0) or (DUMP["size"] == None)):
        entry["size"] = "Unknown"
    else: entry["size"] = DUMP["size"]
    if (titleid.startswith("0100") == True):
        new_file = open("output/titleid/%s.json" % titleid, "w", encoding="UTF-8")
    elif (titleid.startswith("0400") == True):
        new_file = open("output2/titleid/%s.json" % titleid, "w", encoding="UTF-8")
    json.dump(entry, new_file, indent="\t", ensure_ascii=True)
    new_file.close()

missing_games = glob.glob("eshopScrapper/output/titleid/*.json")

for i in range(len(missing_games)):
    titleid = Path(missing_games[i]).stem
    isOunce = False
    if (titleid.startswith("0400"):
        isOunce = True

    if isOunce:
        if titleid in LIST2: continue
    else:
        if titleid in LIST: continue
    file = open(missing_games[i], "r", encoding="UTF-8")
    DUMP = json.load(file)
    file.close()
    if isinstance(DUMP["name"], list):
        if isOunce: LIST2[titleid] = DUMP["name"]
        else: LIST[titleid] = DUMP["name"]
    else:
        if isOunce: LIST2[titleid] = [DUMP["name"]]
        else: LIST[titleid] = [DUMP["name"]]
    entry = {}
    entry["bannerUrl"] = DUMP["bannerUrl"]
    entry["iconUrl"] = DUMP["iconUrl"]
    entry["publisher"] = DUMP["publisher"]
    entry["screenshots"] = DUMP["screenshots"]
    entry["releaseDate"] = DUMP["releaseDate"]
    if (("size" not in DUMP.keys()) or (DUMP["size"] == 0) or (DUMP["size"] == None)):
        entry["size"] = "Unknown"
    else: entry["size"] = DUMP["size"]
    if (titleid.startswith("0100") == True):
        new_file = open("output/titleid/%s.json" % titleid, "w", encoding="UTF-8")
    elif (titleid.startswith("0400") == True):
        new_file = open("output2/titleid/%s.json" % titleid, "w", encoding="UTF-8")
    else:
        print(f"Invalid titleid: {titleid}")
        sys.exit(1)
    json.dump(entry, new_file, indent="\t", ensure_ascii=True)
    new_file.close()

file = open("eshopScrapper/output/main_regions_alt.json", "r", encoding="UTF-8")
DUMP = json.load(file)
file.close()

keys = list(DUMP.keys())

for i in range(len(DUMP)):
    if (keys[i].startswith("0100") == True):
        LIST_REGIONS[keys[i]] = DUMP[keys[i]]
    elif (keys[i].startswith("0400") == True):
        LIST2_REGIONS[keys[i]] = DUMP[keys[i]]
    else:
        print(f"Invalid titleid: {titleid}")
        sys.exit(2)

file = open("eshopScrapper/output/main_regions_alt2.json", "r", encoding="UTF-8")
DUMP = json.load(file)
file.close()

keys = list(DUMP.keys())

for i in range(len(DUMP)):
    if (keys[i].startswith("0100") == True):
        LIST_REGIONS[keys[i]] += DUMP[keys[i]]["True"]
    elif (keys[i].startswith("0400") == True):
        LIST2_REGIONS[keys[i]] += DUMP[keys[i]]["True"]
    else:
        print(f"Invalid titleid: {titleid}")
        sys.exit(3)

print("                        ")
print("Dumping...")
new_file = open("output/main.json", "w", encoding="UTF-8")
json.dump(LIST, new_file, ensure_ascii=False)
new_file.close()
with lzma.open("output/main.json.xz", "w", format=lzma.FORMAT_XZ) as f:
    f.write(json.dumps(LIST, ensure_ascii=False).encode("UTF-8"))
new_file = open("output2/main.json", "w", encoding="UTF-8")
json.dump(LIST2, new_file, ensure_ascii=False)
new_file.close()
with lzma.open("output2/main.json.xz", "w", format=lzma.FORMAT_XZ) as f:
    f.write(json.dumps(LIST2, ensure_ascii=False).encode("UTF-8"))

with open("output/main_regions_alt.json", "r", encoding="UTF-8") as f:
    TH_TITLEIDS = json.load(f)

for titleid in LIST_REGIONS:
    try:
        LIST_REGIONS[titleid] += TH_TITLEIDS[titleid]["True"]
    except: print(f"{titleid} not found in main_regions_alt!")

with open("output2/main_regions_alt.json", "r", encoding="UTF-8") as f:
    TH_TITLEIDS = json.load(f)

for titleid in LIST2_REGIONS:
    try:
        LIST2_REGIONS[titleid] += TH_TITLEIDS[titleid]["True"]
    except: print(f"{titleid} not found in main_regions_alt!")
    
new_file = open("output/main_regions.json", "w", encoding="UTF-8")
json.dump(LIST_REGIONS, new_file, ensure_ascii=False)
new_file.close()
with lzma.open("output/main_regions.json.xz", "w", format=lzma.FORMAT_XZ) as f:
    f.write(json.dumps(LIST_REGIONS, ensure_ascii=False).encode("UTF-8"))
new_file = open("output2/main_regions.json", "w", encoding="UTF-8")
json.dump(LIST2_REGIONS, new_file, ensure_ascii=False)
new_file.close()
with lzma.open("output2/main_regions.json.xz", "w", format=lzma.FORMAT_XZ) as f:
    f.write(json.dumps(LIST2_REGIONS, ensure_ascii=False).encode("UTF-8"))
print("Done.")
