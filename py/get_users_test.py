#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# author: yihao
# HTTP Gateway

import pymongo

con = pymongo.Connection('localhost', 27017)
db = con['db']
activity = db['user']

for item in activity.find():
    print item

post = activity.find_and_modify(
    query={'_id': ObjectId('54492c4e42a953444a74450f')},
    update={'$set': {'status': STATUS_DELETED}},
    fields=['_id'])
