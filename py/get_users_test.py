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
user_message = db['user_message']
message = db['message']
#user_message.remove()
#message.remove()

for item in user.find():
    print item

for item in user_activity.find():
    print item

for item in user_message.find():
    print item

for item in message.find():
    print item
