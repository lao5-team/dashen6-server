#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# author: yafei
# mongodb operations
import pymongo
from gateway_config import *
from bson.objectid import ObjectId

STATUS_OK = 'ok'
STATUS_DELETED = 'deleted'


class DBOp:
    def __init__(self):
        self.connection = pymongo.Connection(db_hostname, db_port)
        self.db = self.connection[db_name]
        self.user = self.db[db_user_table]
        self.activity = self.db[db_activity_table]
        self.unit_test = self.db[db_unit_test_table]

    def __del__(self):
        self.close()

    def close(self):
        if self.connection:
            self.connection.close()
            self.connection = None

    @staticmethod
    def new_id(table):
        """
        在table中,创建一条记录,返回id
        """
        check_table(table)
        post = table.insert({'status': STATUS_OK})
        if post:
            return str(post)
        raise Exception('''couldn't create new id.''')

    @staticmethod
    def save(table, _id, data_map):
        """
        在table中,更新/保存_id的数据,返回id
        """
        check_table(table)
        data_map['status'] = STATUS_OK
        post = table.find_and_modify(
            query={'_id': ObjectId(_id)},
            update={'$set': data_map},
            fields=['_id'])

        if post:
            _id = post.get('_id')
            if _id:
                return str(_id)
        raise Exception('''couldn't save id=%s, it doesn't exist.''' % _id)

    @staticmethod
    def delete(table, _id):
        """
        在table中,删除_id的数据,返回id
        注意,没有真正删除数据,而是将status置为deleted
        """
        check_table(table)
        post = table.find_and_modify(
            query={'_id': ObjectId(_id)},
            update={'$set': {'status': STATUS_DELETED}},
            fields=['_id'])

        if post:
            _id = post.get('_id')
            if _id:
                return str(_id)
        raise Exception('''couldn't delete id=%s, it doesn't exist.''' % _id)

    @staticmethod
    def load(table, _id, fields=None):
        """
        在table中,读取_id的数据并返回
        """
        check_table(table)
        post = table.find_one({'_id': ObjectId(_id), 'status': STATUS_OK}, fields=fields)
        if post is None:
            raise Exception('''couldn't load id=%s, it doesn't exist or deleted.''' % _id)

        return post

    @staticmethod
    def push(table, _ids, field, values):
        """
        在table中,向_ids的field字段对应的队列中中添加一条或多条数据
        """
        if isinstance(values, list):
            update = {'$addToSet': {field: {'$each': values}}}
        elif isinstance(values, str):
            update = {'$addToSet': {field: values}}
        else:
            raise TypeError("values should be an instance of list or str")

        if isinstance(_ids, list):
            for _id in _ids:
                table.find_and_modify(
                    query={'_id': ObjectId(_id)},
                    update=update,
                    fields=['_id'],
                    upsert=True
                )
        elif isinstance(_ids, str):
            table.find_and_modify(
                query={'_id': ObjectId(_ids)},
                update=update,
                fields=['_id'],
                upsert=True
            )

    @staticmethod
    def pop(table, _ids, field, values):
        """
        在table中,从_ids的field字段对应的队列中中删除一条或多条数据
        """
        if isinstance(values, list):
            update = {'$pullAll': {field: values}}
        elif isinstance(values, str):
            update = {'$pullAll': {field: [values]}}
        else:
            raise TypeError("values should be an instance of list or str")

        if isinstance(_ids, list):
            for _id in _ids:
                table.find_and_modify(
                    query={'_id': ObjectId(_id)},
                    update=update,
                    fields=['_id'],
                    upsert=True
                )
        elif isinstance(_ids, str):
            table.find_and_modify(
                query={'_id': ObjectId(_ids)},
                update=update,
                fields=['_id'],
                upsert=True
            )

