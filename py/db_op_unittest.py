#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# author: yafei
# mongodb operations unit test
import unittest
from db_op import DBOp


class DBOpTest(unittest.TestCase):
    def test_id_operations(self):
        db = DBOp()
        table = db.unit_test
        table.remove()

        _id1 = db.new_id(table)
        self.assertTrue(_id1 is not None)
        self.assertTrue(isinstance(_id1, str))
        print 'new generated id: %s' % _id1

        _id2 = db.save(table, _id1, {'data': 'test data'})
        self.assertTrue(_id2 is not None)
        self.assertTrue(isinstance(_id2, str))
        print 'new updated id: %s' % _id2

        self.assertEqual(db.load(table, _id1)['data'], 'test data')

        _id3 = db.delete(table, _id1)
        self.assertTrue(_id3 is not None)
        print 'deleted id: %s' % _id3

        try:
            db.load(table, _id1)
            self.assertFalse('unreachable for exception')
        except Exception, e:
            self.assertIn('''couldn't load''', e.message)
            self.assertIn('''it doesn't exist or deleted''', e.message)

        self.assertEqual(_id1, _id2)
        self.assertEqual(_id1, _id3)
        db.close()

    def test_queue_operations(self):
        db = DBOp()
        table = db.unit_test
        table.remove()

        _id1 = db.new_id(table)
        _id2 = db.new_id(table)
        _id3 = db.new_id(table)

        db.push(table, _id1, 'notify', 'a')
        db.push(table, _id1, 'notify', 'b')
        db.push(table, _id1, 'notify', ['c', 'd'])
        db.push(table, [_id1, _id2, _id3], 'notify', ['a', 'e'])

        data = db.load(table, _id1, fields={'_id': False, 'notify': True})
        print data
        self.assertEqual(data['notify'], ['a', 'b', 'c', 'd', 'e'])

        db.pop(table, _id1, 'notify', ['a', 'b'])
        db.pop(table, _id1, 'notify', 'c')

        data = db.load(table, _id1, fields={'_id': False, 'notify': True})
        self.assertEqual(data['notify'], ['d', 'e'])

        db.pop(table, [_id1, _id2, _id3], 'notify', 'e')

        data = db.load(table, _id1, fields={'_id': False, 'notify': True})
        self.assertEqual(data['notify'], ['d'])
        data = db.load(table, _id2, fields={'_id': False, 'notify': True})
        self.assertEqual(data['notify'], ['a'])
        data = db.load(table, _id3, fields={'_id': False, 'notify': True})
        self.assertEqual(data['notify'], ['a'])

        db.close()


if __name__ == '__main__':
    unittest.main()
