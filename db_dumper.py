#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# author: yafei
# dump mongodb collections
from db_op import DBOp

if __name__ == '__main__':
    db = DBOp()

    print 'dumping collection "user"'
    for u in db.user.find():
        print u

    print 'dumping collection "activity"'
    for a in db.activity.find():
        print a
