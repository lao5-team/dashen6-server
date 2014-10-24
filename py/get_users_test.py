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
