import pymongo
from pymongo import MongoClient
from bson.json_util import dumps
import json
from datetime import datetime
from datetime import timedelta
import time
import math

import os
class MongoDb:
    def __init__(self, port=27017, database="db", collection="jobs"):
        self.portnumber = port
        self.dbname = database
        self.collectionname = collection
        #self.client = MongoClient(os.environ["TODO_DB_1_PORT_27017_TCP_ADDR"],self.portnumber)
        self.client = MongoClient(self.dbname, self.portnumber)
        self.database = self.client[self.dbname]
        self.collection = self.database[self.collectionname]
        print("Connected!")

    def disconnect(self):
        self.database.logout()


    def fetch_main(self, date, hours, lsearch, csearch, tsearch, limit, page, portal):
        params = {}
        if hours != None:
            current_time = datetime.now()
            filtered_time = current_time - timedelta(hours = int(hours))
            str_time = filtered_time.strftime("%Y-%m-%d-%H-%M-%S")
            datelist = str_time.split("-")
            after = datetime(int(datelist[0]), int(datelist[1]), int(datelist[2]), int(datelist[3]), int(datelist[4]), int(datelist[5]))
            params["Posted_On"] = {"$gte": after}
        elif date != None:
            datelist = date.split("-")
            after = datetime(int(datelist[0]), int(datelist[1]), int(datelist[2]), int(datelist[3]), int(datelist[4]), int(datelist[5]))
            params["Posted_On"] = {"$gte": after}

        if portal != None:
            params["Portal"] = {"$regex":str(portal), "$options" :'i'}
        if csearch != None:
            csearch = "(" + csearch.replace("-","|") + ")"
            cs = [{"Company": {"$regex":csearch, "$options" :'i'}}, {"Description": {"$regex":csearch, "$options" :'i'}}]
            params["$or"] = cs
        if lsearch != None:
            lsearch = "(" + lsearch.replace("-","|") + ")"
            params["Location"] = {"$regex":lsearch, "$options" :'i'}
        if tsearch != None:
            tsearch = "(" + tsearch.replace("-","|") + ")"
            params["Title"] = {"$regex":tsearch, "$options" :'i'}

        if limit == None:
            limit = 20
        else:
            limit = int(limit)
        if page == None:
            page = 1
        else:
            page = int(page)

        cursor = self.collection.find(params)
        count = cursor.count()
        records = []
        for record in cursor.sort('Posted_On', -1):
            records.append(record)

        tpages = math.ceil(count/limit)
        records = records[(page-1)*limit:((page-1)*limit)+limit]
        result = str(dumps({"count": count, "total_pages": tpages, "result": records}, indent=2))
        py_object = json.loads(result)

        return py_object



    def fetch_some(self, number=10, all = False):
        cursor = self.collection.find()
        total = cursor.count()
        if all == False:
            number = min(total, number)
        else:
            number = total
        cursor = cursor[:number]
        records = []
        for record in cursor:
            records.append(record)
        return records

    def fetch_by_date(self, date):
        datelist = date.split("-")
        after = datetime(int(datelist[0]), int(datelist[1]), int(datelist[2]), int(datelist[3]), int(datelist[4]), int(datelist[5]))
        cursor = self.collection.find({"Posted_On" : {"$gte": after}})
        records = []
        for record in cursor:
            records.append(record)
        return records

    def fetch_by_hours(self, hours):
        current_time = datetime.now()
        filtered_time = current_time - timedelta(hours = hours)
        str_time = filtered_time.strftime("%Y-%m-%d-%H-%M-%S")
        datelist = str_time.split("-")
        after = datetime(int(datelist[0]), int(datelist[1]), int(datelist[2]), int(datelist[3]), int(datelist[4]), int(datelist[5]))
        cursor = self.collection.find({"Posted_On" : {"$gte": after}})
        records = []
        for record in cursor:
            records.append(record)
        return records

    def search_string(self, search):
        search_list = search.split("-")
        cursor = self.collection.find({ "$text" : {"$search": " ".join(search_list)}})
        records = []
        for record in cursor:
            records.append(record)
        return records

    def insert_df(self, df):
        df_json = df.to_dict(orient="records")
        self.collection.insert_many(df_json)
        return

    def check_duplicate(self, portal, portal_id):
        # Returns 1 is duplicate is present
        if self.collection.count_documents({"Portal":portal, "Portal_Id":portal_id}) > 0:
            return 1
        return 0

    def delete_all(self):
        self.collection.delete_many({})
        return
