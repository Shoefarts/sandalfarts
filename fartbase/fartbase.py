import pymongo
import pandas as pd
import os
import time
import sys
sys.path.append("..")
from packages.fart import fart
from datetime import datetime


# MongoDB Login
mongUser = os.getenv('mongUser')
mongPass = os.getenv('mongPass')
mongClient = pymongo.MongoClient('mongodb+srv://' + mongUser + ':' + mongPass + '@cluster0.mqiqi.mongodb.net/fartbase?retryWrites=true&w=majority')

i = 1
while i == 1:
    pullList = fart.mongtodf(mongUser, mongPass, 'wynnAPI', 'toDownload')

    for entry in pullList.itertuples(index=False):
        today = datetime.today()
        todayFormat = today.strftime("%Y/%m/%d")


        data = fart.requestget(entry.URL)
        data_df = pd.json_normalize(data)
        data_df.insert(0, 'date', todayFormat)
        fart.dftomong(mongUser, mongPass, 'wynnAPI', entry.col, data_df, False)
        print('Updated: ' + entry.col)

    myFile = open('updatelog.txt', 'a')
    myFile.write('\nUpdate ran on ' + str(datetime.now()))

    time.sleep(10800)

