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
pictureInfo = db['picture_info']
comment = db['comment']
'''
user_message.remove()
message.remove()
activity.remove()
user_activity.remove();
'''
print "user table"
print "\n"
for item in user.find():
    print item
print "\n"

print "activity_table"
print "\n"
for item in activity.find():
    print item
print "\n"

print "user_activity table"
print "\n"
for item in user_activity.find():
    print item
print "\n"

print "user_message table"
print "\n"
for item in user_message.find():
    print item
print "\n"

print "message table"
print "\n"
for item in message.find():
    print item
print "\n"

print "comment table"
print "\n"
for item in comment.find():
    print item
print "\n"

print "picture table"
for item in pictureInfo.find():
    print item
