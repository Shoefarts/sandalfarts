import pymongo
import pandas as pd
import os
import requests
import json
from datetime import datetime


# MongoDB Login
mongUser = os.getenv('mongUser')
mongPass = os.getenv('mongPass')
mongClient = pymongo.MongoClient('mongodb+srv://' + mongUser + ':' + mongPass + '@cluster0.mqiqi.mongodb.net/fartbase?retryWrites=true&w=majority')

col = mongClient.wynnAPI.toDownload
cursor = col.find()
list_cur = list(cursor)
pullList = pd.DataFrame(list_cur)

for entry in pullList.itertuples(index=False):
    today = datetime.today()
    todayFormat = today.strftime("%Y/%m/%d")


    r = requests.get(entry.URL)
    byte_str = r.content
    dict_str = byte_str.decode("UTF-8")
    data = json.loads(dict_str)
    data_df = pd.json_normalize(data)
    data_df.insert(0, 'date', todayFormat)

    mongDb = mongClient['wynnAPI']
    mongCol = mongDb[entry.col]
    data_df.reset_index(inplace=True)
    df_dict = data_df.to_dict(orient='records')
    mongCol.insert_many(df_dict)

    print('Updated: ' + entry.col)

myFile = open('updatelog.txt', 'a')
myFile.write('\nUpdate ran on ' + str(datetime.now()))

