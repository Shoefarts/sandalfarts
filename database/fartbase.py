import pymongo
import pandas as pd
import os
import time
import sys
sys.path.append("..")
from packages.fart import gen
from datetime import datetime


# MongoDB Login
mongUser = os.getenv('mongUser')
mongPass = os.getenv('mongPass')
mongClient = pymongo.MongoClient('mongodb+srv://' + mongUser + ':' + mongPass + '@cluster0.mqiqi.mongodb.net/fartbase?retryWrites=true&w=majority')

# Class Initialization
gen = gen()

# Constant loop
i = 1
while i == 1:

    # Pulls list of data to cache
    pullList = gen.mongtodf(mongUser, mongPass, 'wynnAPI', 'toDownload')

    # Saves a copy of API and uploads to database
    for entry in pullList.itertuples(index=False):
        today = datetime.today()
        todayFormat = today.strftime("%Y/%m/%d")


        data = gen.requestget(entry.URL)
        data_df = pd.json_normalize(data)
        data_df.insert(0, 'date', todayFormat)
        gen.dftomong(mongUser, mongPass, 'wynnAPI', entry.col, data_df, False)
        print('Updated: ' + entry.col)

    # Prints log
    myFile = open('updatelog.txt', 'a')
    myFile.write('\nUpdate ran on ' + str(datetime.now()))

    # Sleeps for 3 hours
    time.sleep(10800)

