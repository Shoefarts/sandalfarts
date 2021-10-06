import requests
import pandas as pd
import pymongo
import json
import datetime

class gen:
    def requestget(self, URL):
        r = requests.get(URL)
        byte_str = r.content
        dict_str = byte_str.decode("UTF-8")
        content = json.loads(dict_str)
        return content

    def mongtodf(self, mongUser, mongPass, database, collection):
        mongClient = pymongo.MongoClient('mongodb+srv://' + mongUser + ':' + mongPass + '@cluster0.mqiqi.mongodb.net/fartbase?ssl=true&ssl_cert_reqs=CERT_NONE&retryWrites=true&w=majority')
        call = 'mongClient.' + database + '.' + collection
        col = eval(call)
        cursor = col.find()
        list_cur = list(cursor)
        df = pd.DataFrame(list_cur)
        return df

    def mongtolist(self, mongUser, mongPass, database, collection):
        mongClient = pymongo.MongoClient('mongodb+srv://' + mongUser + ':' + mongPass + '@cluster0.mqiqi.mongodb.net/fartbase?ssl=true&ssl_cert_reqs=CERT_NONE&retryWrites=true&w=majority')
        call = 'mongClient.' + database + '.' + collection
        col = eval(call)
        cursor = col.find()
        list_cur = list(cursor)
        return list_cur

    def dftomong(self, mongUser, mongPass, database, collection, dataframe, drop:bool):
        mongClient = pymongo.MongoClient('mongodb+srv://' + mongUser + ':' + mongPass + '@cluster0.mqiqi.mongodb.net/fartbase?ssl=true&ssl_cert_reqs=CERT_NONE&retryWrites=true&w=majority')
        mongDb = mongClient[database]
        mongCol = mongDb[collection]
        if drop == True:
            mongCol.drop()
        dataframe.reset_index(inplace=True)
        df_dict = dataframe.to_dict(orient='records')
        mongCol.insert_many(df_dict)
        return

class xpcomp:
    def extractxpandlvl(self, guildName, guildDatabase):
        guild = guildDatabase.loc[guildDatabase['name'] == guildName]
        d = dict()
        d['xp'] = guild.iloc[0]['xp']
        d['lvl'] = guild.iloc[0]['level']
        return(d)

    def extractmembers(self, guildData):
        members = guildData.get('members')
        remove = ('rank', 'joined', 'joinedFriendly')
        for entry in members:
            for key in remove:
                entry.pop(key, None)
        membersdf = pd.DataFrame.from_dict(members)
        return(membersdf)

class wars:
    def terrlistget(self, guildFullName):
        URL = 'https://api.wynncraft.com/public_api.php?action=territoryList'
        fullTerrList = gen().requestget(URL)
        allTerrs = fullTerrList.get('territories')
        guildName = ''
        terrGuild = {}
        terrCount = 0
        for terr in allTerrs:
            if allTerrs[terr]['guild'].lower() == guildFullName.lower():
                guildName = allTerrs[terr]['guild']
                terrGuild[terr] = allTerrs[terr]
                terrCount += 1
        return([guildName, terrGuild, terrCount])

    def terrtimeandtreasury(self, terrList, terrName):
        terrDate = datetime.datetime.fromisoformat(terrList[terrName]['acquired']) - datetime.timedelta(hours=5)
        terrHold = datetime.datetime.now() - terrDate
        terrHour, remainder = divmod(terrHold.seconds, 3600)
        terrMinute, terrSecond = divmod(remainder, 60)
        terrHold_Str = ''
        if terrHold.days != 0:
            terrHold_Str += str(terrHold.days)
            if terrHold.days > 1:
                terrHold_Str += ' days, '
            else:
                terrHold_Str += ' day, '
        if terrHour != 0:
            terrHold_Str += str(terrHour)
            if terrHour > 1:
                terrHold_Str += ' hours, '
            else:
                terrHold_Str += ' hour, '
        if terrMinute != 0:
            terrHold_Str += str(terrMinute)
            if terrMinute > 1:
                terrHold_Str += ' minutes, '
            else:
                terrHold_Str += ' minute, '
        if terrSecond != 0:
            terrHold_Str += 'and ' + str(terrSecond)
            if terrSecond > 1:
                terrHold_Str += ' seconds'
            else:
                terrHold_Str += ' second'
        treasurylvl = 0
        if terrHold.days >= 1:
            treasurylvl = 2
            if terrHold.days >= 5:
                treasurylvl = 3
                if terrHold.days >= 12:
                    treasurylvl = 4
        else:
            if terrHour >= 1:
                treasurylvl = 1
        return(terrHold_Str, treasurylvl)

    def terrresandem(self, terrResource:list, terrEmerald):
        ore = 0
        crops = 0
        fish = 0
        wood = 0
        for res in terrResource:
            if res == 'ore':
                ore += 3600
            elif res == 'crops':
                crops += 3600
            elif res == 'fish':
                fish += 3600
            elif res == 'wood':
                wood += 3600
            elif res == 'oasis':
                ore += 900
                crops += 900
                fish += 900
                wood += 900
        emerald = 0
        if terrEmerald == 'normal':
            emerald += 9000
        elif terrEmerald == 'town':
            emerald += 18000
        elif terrEmerald == 'oasis':
            emerald += 1800
        return([ore, crops, fish, wood, emerald])

    def pullupgradecost(self, mongUser, mongPass):
        upgradeCostsMess = gen().mongtolist(mongUser, mongPass, 'guildWars', 'upgradeCosts')
        upgradeCosts = {}
        for item in upgradeCostsMess:
            del item['_id']
            upgradeCosts.update(item)
        return(upgradeCosts)

    def pullterrdata(self, mongUser, mongPass):
        terrData_df = gen().mongtodf(mongUser, mongPass, 'guildWars', 'terrData')
        terrData_df = terrData_df.drop(columns=['_id', 'index'])
        terrData_dict = terrData_df.set_index('territory').T.to_dict('dict')
        return terrData_dict

    def calcconnbonus(self, terrName, pullterrdata, liveTerrDict):
        terrInfo = pullterrdata[terrName]
        conns = []
        for border in terrInfo['borders'][1]:
            if border in liveTerrDict:
                conns.append(border)
        connBonus = len(conns)*.30
        return([connBonus, conns])

    def calchqbonus(self, terrName, pullterrdata, liveTerrDict, useGuild:bool):
        connsT1 = self.calcconnbonus(terrName, pullterrdata, liveTerrDict)[1]
        terrInfo = pullterrdata[terrName]
        bordersT1 = terrInfo['borders'][1]
        connsT2 = []
        bordersT2 = []
        for hqConn in bordersT1:
            terrInfo = pullterrdata[hqConn]
            for border in terrInfo['borders'][1]:
                if (border not in bordersT2) and (border not in bordersT1) and (border != terrName):
                    bordersT2.append(border)
                if (border in liveTerrDict) and (border not in connsT2) and (border not in connsT1) and (border != terrName):
                    connsT2.append(border)
        connsT3 = []
        bordersT3 = []
        for conn in bordersT2:
            terrInfo = pullterrdata[conn]
            for border in terrInfo['borders'][1]:
                if (border not in bordersT3) and (border not in bordersT2) and (border not in bordersT1) and (border != terrName):
                    bordersT3.append(border)
                if (border in liveTerrDict) and (border not in connsT3) and (border not in connsT2) and (border not in connsT1) and (border != terrName):
                    connsT3.append(border)
        if useGuild:
            hqBonus = ((len(connsT1)+len(connsT2)+len(connsT3))*.25)+.50
            return[terrName, hqBonus, connsT1, connsT2, connsT3]
        else:
            hqBonus = ((len(bordersT1) + len(bordersT2) + len(bordersT3)) * .25) + .50
            return[terrName, hqBonus, bordersT1, bordersT2, bordersT3]

    def lochighesthqbonus(self, allTerrInfo, liveTerrDict):
        hqbuff = 0
        hqloc = []
        for terr in list(liveTerrDict):
            terrName = terr
            hqconnsinfo = self.calchqbonus(terrName, allTerrInfo, liveTerrDict, True)

            if hqconnsinfo[1] > hqbuff:
                hqbuff = hqconnsinfo[1]
                hqloc = [hqconnsinfo]
            elif hqconnsinfo[1] == hqbuff:
                hqloc.append(hqconnsinfo)
        return(hqloc)