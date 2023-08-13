import requests
import threading
import time
from datetime import datetime
from time import strftime
from time import gmtime
from dateutil.parser import parse
from concurrent.futures import ThreadPoolExecutor

MAX_REQUESTS_PER_SECOND = 10
REQUEST_INTERVAL = 1 / MAX_REQUESTS_PER_SECOND

def send_request(town):
    url = f"https://api.earthmc.net/v1/aurora/towns/{town}"
    print(town)
    resNum = 0
    try:
        townsLookup = requests.get(url).json()
        mayor = townsLookup['strings']['mayor']
        x = townsLookup['spawn']['x']
        z = townsLookup['spawn']['z']
        town_size = townsLookup['stats']['numTownBlocks']
        is_ruined = townsLookup['status']['isRuined']
        resNum = townsLookup['stats']['numResidents']
    except Exception as e:
        print(e)
    if resNum == 1:
        try:
            mayorLookup = requests.get(f"https://api.earthmc.net/v1/aurora/residents/{mayor}").json()
        except Exception as e:
            print(e)
        lastOnline_TimeStamp = mayorLookup['timestamps']['lastOnline'] / 1000
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        last = datetime.fromtimestamp(lastOnline_TimeStamp).strftime('%Y-%m-%d %H:%M:%S')
        date_now = parse(now)
        date_last = parse(last)
        result = (date_now - date_last).total_seconds()
        m, s = divmod(result, 60)
        h, m = divmod(m, 60)
        d, h = divmod(h, 24)
        if d == 42 and is_ruined == False:
            with open('towns.txt', 'a+', encoding="utf-8") as f:
                f.write(
                    "Town: %s \nChunks: %d\nMayor: %s\nOffline since %d days %d hours %d minutes %d seconds.\ndynmap URL：https://earthmc.net/map/aurora/?worldname=earth&mapname=flat&zoom=5&x=%d&z=%d\n\n" % (
                    town, town_size, mayor, d, h, m, s, x, z))
            f.close()

def Query_Unallied(nation):
    allNationsLookup = requests.get("https://api.earthmc.net/v1/aurora/nations/").json()
    try:
        nationsLookup = requests.get(f"https://api.earthmc.net/v1/aurora/nations/{nation}").json()
    except:
        print("Invalid Input.")
        return

    allyList = nationsLookup["allies"]
    allNations = allNationsLookup["allNations"]
    allNations.remove(nationsLookup["strings"]["nation"])

    unalliedList = list(set(allNations).difference(set(allyList)))
    unalliedList.sort()
    return unalliedList

def Query_Falling_Nations():
    import time
    from datetime import datetime
    from time import strftime
    from time import gmtime
    from dateutil.parser import parse
    cnt = 0 
    allNationsLookup = requests.get("https://api.earthmc.net/v1/aurora/nations/").json()
    allNations = allNationsLookup["allNations"]
    for nation in allNations:
        nationsLookup = requests.get(f"https://api.earthmc.net/v1/aurora/nations/{nation}").json()
        capital = nationsLookup['strings']['capital']
        king = nationsLookup['strings']['king']
        capitalLookup = requests.get(f"https://api.earthmc.net/v1/aurora/towns/{capital}").json()
        resNum = capitalLookup['stats']['numResidents']
        if resNum == 1:
            kingLookup = requests.get(f"https://api.earthmc.net/v1/aurora/residents/{king}").json()
            lastOnline_TimeStamp = kingLookup['timestamps']['lastOnline']/1000
            # lastOnline_TimeTuple = time.localtime(lastOnline_TimeStamp)
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            last = datetime.fromtimestamp(lastOnline_TimeStamp).strftime('%Y-%m-%d %H:%M:%S')
            date_now = parse(now)
            date_last = parse(last)
            result = (date_now - date_last).total_seconds()
            m, s = divmod(result, 60)
            h, m = divmod(m, 60)
            d, h = divmod(h, 24)
            if d >= 35:
                print ("Nation: %s\nKing: %s\nOffline since %d days %d hours %d minutes %d seconds." % (nation, king, d, h, m, s))
                cnt += 1
    # AuroraLookup = requests.get("https://api.earthmc.net/v1/aurora/").json()
    # time = AuroraLookup["world"]["fullTime"]
    print(" %d nations about to fall. Use /seen in game to check more details!" % cnt)

def Query_Falling_Towns():
    allTownsLookup = requests.get("https://api.earthmc.net/v1/aurora/towns/").json()
    # numTowns = allTownsLookup["numTowns"]
    allTowns = allTownsLookup["allTowns"]
    total_requests = len(allTowns)
    with ThreadPoolExecutor(max_workers=total_requests) as executor:
        for town in allTowns:
            try:
                executor.submit(send_request, town)
                time.sleep(REQUEST_INTERVAL)
            except:
                continue
    print("Check done. Use /seen in game to check more details!")

def Query_leaders():
    myNation = input("Your Nation:")
    onlineLookup = requests.get("https://emctoolkit.vercel.app/api/aurora/onlineplayers").json()
    nationLookup = requests.get("https://api.earthmc.net/v2/aurora/nations").json()
    unalliedNation = Query_Unallied(myNation)
    leader_nation = {}
    for n in nationLookup:
        nation = n["name"]
        leader_nation[n["king"]] = nation
        if "ranks" in n:
            if "Chancellor" in n["ranks"]:
                for chancellor in n["ranks"]["Chancellor"]:
                    leader_nation[chancellor] = nation
            if "Diplomat" in n["ranks"]:
                for diplomat in n["ranks"]["Diplomat"]:
                    if diplomat not in leader_nation:
                        leader_nation[diplomat] = nation
    for player in onlineLookup:
        if player["name"] in leader_nation:
            if leader_nation[player["name"]] in unalliedNation:
                print("%s %s" % (player["name"], leader_nation[player["name"]]))

if __name__ == '__main__':
    print("1.Query unallied nations\n2.Query falling nations/towns\n3.Query online kings/chancellors/diplomats\n4.quit")
    while True:
        index = input("Input:")
        if index == "1":
            myNation = input("Your Nation:")
            unallied = Query_Unallied(myNation)
            cnt = 0
            for name in unallied:
                print(name)
                cnt += 1
            print("[%s have %d nations not allied.]" % (myNation, cnt))
        elif index == "2":
            q = input("1.Query nations 2.Query towns\nInput:")
            if q == "1":
                Query_Falling_Nations()
            elif q == "2":
                Query_Falling_Towns()
        elif index == "3":
            Query_leaders()
        elif index == "4":
            break
