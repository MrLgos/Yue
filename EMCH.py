import requests

def Query_Unallied():
    nation = input("请输入你想查询的国家名:")
    cnt=0

    allNationsLookup = requests.get("https://api.earthmc.net/v1/aurora/nations/").json()
    try:
        nationsLookup = requests.get(f"https://api.earthmc.net/v1/aurora/nations/{nation}").json()
    except:
        print("错误的输入请重试.")
        return

    allyList = nationsLookup["allies"]
    allNations = allNationsLookup["allNations"]
    allNations.remove(nationsLookup["strings"]["nation"])

    unalliedList = list(set(allNations).difference(set(allyList)))
    unalliedList.sort()
    for name in unalliedList:
        print(name)
        cnt += 1
    print("[%s 有上述 %d 个国家尚未结盟.]"%(nation,cnt))
    return

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
                print ("国家名: %s\n国王: %s\n已经离线 %d 天 %d 小时 %d 分钟 %d 秒." % (nation, king, d, h, m, s))
                cnt += 1
    # AuroraLookup = requests.get("https://api.earthmc.net/v1/aurora/").json()
    # time = AuroraLookup["world"]["fullTime"]
    print("将有 %d 个国家即将倒闭. 请在游戏中使用/seen指令进一步明确!" % cnt)

def Query_Falling_Towns():
    import time
    from datetime import datetime
    from time import strftime
    from time import gmtime
    from dateutil.parser import parse
    cnt = 0 # 计算将要倒闭的城镇总数
    sum = 0 # 计算已经遍历了多少个城镇
    allTownsLookup = requests.get("https://api.earthmc.net/v1/aurora/towns/").json()
    numTowns = allTownsLookup["numTowns"]
    allTowns = allTownsLookup["allTowns"]
    for town in allTowns:
        try:
            townsLookup = requests.get(f"https://api.earthmc.net/v1/aurora/towns/{town}").json()
            mayor = townsLookup['strings']['mayor']
            x = townsLookup['spawn']['x']
            y = townsLookup['spawn']['y']
            z = townsLookup['spawn']['z']
            town_size = townsLookup['stats']['numTownBlocks']
            is_ruined = townsLookup['status']['isRuined']
            resNum = townsLookup['stats']['numResidents']
        except:
            continue
        sum += 1
        print("%s %.2lf%%" % (town,sum / numTowns * 100))
        if resNum == 1:
            try:
                mayorLookup = requests.get(f"https://api.earthmc.net/v1/aurora/residents/{mayor}").json()
            except:
                continue
            lastOnline_TimeStamp = mayorLookup['timestamps']['lastOnline']/1000
            # lastOnline_TimeTuple = time.localtime(lastOnline_TimeStamp)
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            last = datetime.fromtimestamp(lastOnline_TimeStamp).strftime('%Y-%m-%d %H:%M:%S')
            date_now = parse(now)
            date_last = parse(last)
            result = (date_now - date_last).total_seconds()
            m, s = divmod(result, 60)
            h, m = divmod(m, 60)
            d, h = divmod(h, 24)
            if d >= 41 and is_ruined == False:
                with open('结果.txt','a+',encoding="utf-8") as f: 
                    f.write("城镇名字: %s 城镇区块数: %d\n市长: %s\n已经离线 %d 天 %d 小时 %d 分钟 %d 秒.\ndynmap链接：https://earthmc.net/map/aurora/?worldname=earth&mapname=flat&zoom=5&x=%d&z=%d\n是否是废弃状态: %s\n\n" % (town, town_size, mayor, d, h, m, s, x, z, is_ruined))
                f.close()
                cnt += 1
    # AuroraLookup = requests.get("https://api.earthmc.net/v1/aurora/").json()
    # time = AuroraLookup["world"]["fullTime"]
    print("将有 %d 个城镇即将倒闭. 请在游戏中使用/seen指令进一步明确!" % cnt)


if __name__ == '__main__':
    print("1代表查询未结盟的国家\n2代表查询将要倒闭的国家或城镇\n3代表退出该程序")
    while True:
        index = input("请输入上述的一个数字:")
        if index == "1":
            Query_Unallied()
        elif index == "2":
            q = input("1代表查询将要倒闭的国家 2代表查询将要倒闭的城镇\n请输入上述的一个数字:")
            if q == "1":
                Query_Falling_Nations()
            elif q == "2":
                Query_Falling_Towns()
        elif index == "3":
            break
