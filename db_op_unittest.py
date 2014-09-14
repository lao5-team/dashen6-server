#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# author: yafei
# mongodb operations unit test
import unittest
from db_op import DBOp


class DBOpTest(unittest.TestCase):
    def testPushPull(self):
        db = DBOp()
        collection = db.db['temp']
        collection.remove()
        db._push(collection, 'user', '001')
        db._push(collection, 'user', ['002', '003'])

        self.assertListEqual(db._pull(collection, 'user'), ['001', '002', '003'])
        self.assertIsNone(db._pull(collection, 'user2'))
        self.assertIsNone(db._pull(collection, 'user3'))
        db.close()


if __name__ == "__main__":
    unittest.main()
