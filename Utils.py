import requests
import threading
import time
from datetime import datetime
from time import strftime
from time import gmtime
from dateutil.parser import parse
from concurrent.futures import ThreadPoolExecutor

def timeTransfer(TimeStamp):
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    last = datetime.fromtimestamp(TimeStamp).strftime('%Y-%m-%d %H:%M:%S')
    date_now = parse(now)
    date_last = parse(last)
    result = (date_now - date_last).total_seconds()
    m, s = divmod(result, 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)
    return d, h, m, s

def townRequest(town):
    url = f"https://api.earthmc.net/v1/aurora/towns/{town}"
    resNum = 0
    try:
        townsLookup = requests.get(url).json()
        mayor = townsLookup['strings']['mayor']
        x = townsLookup['spawn']['x']
        z = townsLookup['spawn']['z']
        town_size = townsLookup['stats']['numTownBlocks']
        is_ruined = townsLookup['status']['isRuined']
        is_open = townsLookup['status']['isOpen']
        resNum = townsLookup['stats']['numResidents']
    except Exception as e:
        print(e)
    if resNum == 1:
        try:
            mayorLookup = requests.get(f"https://api.earthmc.net/v1/aurora/residents/{mayor}").json()
        except Exception as e:
            print(e)
        lastOnline_TimeStamp = mayorLookup['timestamps']['lastOnline'] / 1000
        d, h, m, s = timeTransfer(lastOnline_TimeStamp)
        if d >= 42 and d <= 45 and is_ruined == False:
            with open('towns.txt', 'a+', encoding="utf-8") as f:
                f.write(
                    "Town: %s 【Open: %s】\nChunks: %d\nMayor: %s\nOffline since %d days %d hours %d minutes %d seconds.\ndynmap URL：https://earthmc.net/map/aurora/?worldname=earth&mapname=flat&zoom=5&x=%d&z=%d\n\n" % (
                    town, is_open, town_size, mayor, d, h, m, s, x, z))
            f.close()


def nationRequest(nation):
    nurl = f"https://api.earthmc.net/v1/aurora/nations/{nation}"
    try:
        nationsLookup = requests.get(nurl).json()
        capital = nationsLookup['strings']['capital']
        king = nationsLookup['strings']['king']
        turl = f"https://api.earthmc.net/v1/aurora/towns/{capital}"
        capitalLookup = requests.get(turl).json()
        resNum = capitalLookup['stats']['numResidents']
        kurl = f"https://api.earthmc.net/v1/aurora/residents/{king}"
        if resNum == 1:
            kingLookup = requests.get(kurl).json()
            lastOnline_TimeStamp = kingLookup['timestamps']['lastOnline'] / 1000
            d, h, m, s = timeTransfer(lastOnline_TimeStamp)
            if d >= 35 and d <= 45:
                with open('nations.txt', 'a+', encoding="utf-8") as f:
                    f.write("Nation: %s\nKing: %s\nOffline since %d days %d hours %d minutes %d seconds.\n\n" % (
                    nation, king, d, h, m, s))
                f.close()
    except Exception as e:
        print(e)