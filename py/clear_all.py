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
picture_info = db['picture_info']
comment = db['comment']
user_message.remove()
message.remove()
activity.remove()
#activity.remove({'_id':ObjectId('546c95e9e138236804e093f5')})
user_activity.remove()
comment.remove()
