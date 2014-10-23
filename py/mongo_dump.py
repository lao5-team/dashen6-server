#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# author: yafei
# mongodb dumper
import pymongo

con = pymongo.Connection('localhost', 27017)
db = con['db']

print 'dumping table user:'
table = db['user']
for item in table.find():
    print item

print 'dumping table activity:'
table = db['activity']
for item in table.find():
    print item
