#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# author: yihao
# HTTP Gateway

import pymongo
from bson.objectid import ObjectId

STATUS_DELETED = 'deleted'
con = pymongo.Connection('localhost', 27017)
db = con['db']
user = db['user']
user_activity = db['user_activity']
user.remove({"username":"kimi1"})

for item in user.find():
    print item

for item in user_activity.find():
    print item

