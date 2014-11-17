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
activity = db['activity']
user_activity = db['user_activity']
user_message = db['user_message']
message = db['message']
'''
user_message.remove()
message.remove()
activity.remove()
user_activity.remove();
'''
print "user table"
for item in user.find():
    print item

print "activity_table"
for item in activity.find():
    print item


print "user_activity table"
for item in user_activity.find():
    print item

print "user_message table"
for item in user_message.find():
    print item

print "message table"
for item in message.find():
    print item
