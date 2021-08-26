import requests
import pandas as pd
import pymongo
import json
import discord
import math
import datetime

class fart:
    def requestget(URL):
        r = requests.get(URL)
        byte_str = r.content
        dict_str = byte_str.decode("UTF-8")
        content = json.loads(dict_str)
        return content

    def mongtodf(mongUser, mongPass, database, collection):
        mongClient = pymongo.MongoClient('mongodb+srv://' + mongUser + ':' + mongPass + '@cluster0.mqiqi.mongodb.net/fartbase?retryWrites=true&w=majority')
        call = 'mongClient.' + database + '.' + collection
        col = eval(call)
        cursor = col.find()
        list_cur = list(cursor)
        df = pd.DataFrame(list_cur)
        return df

    def mongtolist(mongUser, mongPass, database, collection):
        mongClient = pymongo.MongoClient('mongodb+srv://' + mongUser + ':' + mongPass + '@cluster0.mqiqi.mongodb.net/fartbase?retryWrites=true&w=majority')
        call = 'mongClient.' + database + '.' + collection
        col = eval(call)
        cursor = col.find()
        list_cur = list(cursor)
        return list_cur

    def dftomong(mongUser, mongPass, database, collection, dataframe, drop:bool):
        mongClient = pymongo.MongoClient('mongodb+srv://' + mongUser + ':' + mongPass + '@cluster0.mqiqi.mongodb.net/fartbase?retryWrites=true&w=majority')
        mongDb = mongClient[database]
        mongCol = mongDb[collection]
        if drop == True:
            mongCol.drop()
        dataframe.reset_index(inplace=True)
        df_dict = dataframe.to_dict(orient='records')
        mongCol.insert_many(df_dict)
        return

    def extractxpandlvl(guildName, guildDatabase):
        guild = guildDatabase.loc[guildDatabase['name'] == guildName]
        d = dict();
        d['xp'] = guild.iloc[0]['xp']
        d['lvl'] = guild.iloc[0]['level']
        return(d)

    def extractmembers(guildData):
        members = guildData.get('members')
        remove = ('rank', 'joined', 'joinedFriendly')
        for entry in members:
            for key in remove:
                entry.pop(key, None)
        membersdf = pd.DataFrame.from_dict(members)
        return(membersdf)

    def terrlistget(guildFullName):
        URL = 'https://api.wynncraft.com/public_api.php?action=territoryList'
        fullTerrList = fart.requestget(URL)
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

    def terrtimeandtreasury(terrList, terrName):
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

    def terrresandem(terrResource:list, terrEmerald):
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

    def pullupgradecost(mongUser, mongPass):
        upgradeCostsMess = fart.mongtolist(mongUser, mongPass, 'guildWars', 'upgradeCosts')
        upgradeCosts = {}
        for item in upgradeCostsMess:
            del item['_id']
            upgradeCosts.update(item)
        return(upgradeCosts)