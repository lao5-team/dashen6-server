#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# author: yafei
# dump mongodb collections
import json
import sys
from db_op import DBOp

if __name__ == '__main__':
    db = DBOp()

    print 'dumping collection "user"'
    for u in db.user.find():
        print u

    print 'dumping collection "activity"'
    for a in db.activity.find():
        print a

        # if a has 'data' field, try to parse it
        data = a.get('data')
        if data:
            try:
                json.loads(data)
            except ValueError:
                print >> sys.stderr, '''couldn't decode data'''
