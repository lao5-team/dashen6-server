#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# author: yafei
# mongodb operations unit test
import unittest
from db_op import DBOp


class DBOpTest(unittest.TestCase):
    def test_push_pull(self):
        db = DBOp()
        collection = db.db['temp']
        collection.remove()
        db._push(collection, 'user', '001')
        db._push(collection, 'user', ['002', '003'])

        self.assertListEqual(db._pull(collection, 'user'), ['001', '002', '003'])
        self.assertIsNone(db._pull(collection, 'user2'))
        self.assertIsNone(db._pull(collection, 'user3'))
        db.close()

    def test_new_save_load_id(self):
        db = DBOp()
        collection = db.db['temp']
        collection.remove()
        _id1 = db.new_id(collection)
        assert _id1 is not None
        assert isinstance(_id1, str)
        print 'new generated id: %s' % _id1
        _id2 = db.save_id(collection, _id1, 'test data')
        assert _id2 is not None
        assert isinstance(_id2, str)
        print 'new updated id: %s' % _id2

        self.assertEqual(_id1, _id2)
        self.assertEqual(db.load_id(collection, _id1), 'test data')
        db.close()


if __name__ == '__main__':
    unittest.main()
