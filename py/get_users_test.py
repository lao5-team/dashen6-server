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
activity = db['user']
user_activity = db['user_activity']

for item in activity.find():
    print item

for item in user_activity.find():
    print item

