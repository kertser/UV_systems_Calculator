# -*- coding: utf-8 -*-
"""
Created on Mon Jan  4 13:54:33 2021

@author: Mike
"""

from pymongo import MongoClient
import pandas as pd

client = MongoClient("mongodb+srv://Mike:Atlantium@cluster0.xyexc.mongodb.net/<dbname>?retryWrites=true&w=majority")
db = client.get_database('CalcUsers')
records = db.Calculator
print(records.count_documents({}))
users = list(records.find({}))
data = pd.DataFrame(users)

uname = users[0].get('UserName')
users[0].get('Password')
#u1 = list(records.find({'Username':'Guest1'},{'Password':'Guest1'}))