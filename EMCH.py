import requests
import threading
import time
import Utils
from datetime import datetime
from time import strftime
from time import gmtime
from dateutil.parser import parse
from concurrent.futures import ThreadPoolExecutor

MAX_REQUESTS_PER_SECOND = 10
REQUEST_INTERVAL = 1 / MAX_REQUESTS_PER_SECOND

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
    allNationsLookup = requests.get("https://api.earthmc.net/v1/aurora/nations/").json()
    allNations = allNationsLookup["allNations"]
    total_requests = len(allNations)
    print("Running now, pls wait...")
    with ThreadPoolExecutor(max_workers=total_requests) as executor:
        for nation in allNations:
            try:
                executor.submit(Utils.nationRequest, nation)
                time.sleep(REQUEST_INTERVAL)
            except:
                continue
    print("Check done. Use /seen in game to check more details!")

def Query_Falling_Towns():
    allTownsLookup = requests.get("https://api.earthmc.net/v1/aurora/towns/").json()
    allTowns = allTownsLookup["allTowns"]
    total_requests = len(allTowns)
    print("Running now, pls wait...")
    with ThreadPoolExecutor(max_workers=total_requests) as executor:
        for town in allTowns:
            try:
                executor.submit(Utils.townRequest, town)
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
