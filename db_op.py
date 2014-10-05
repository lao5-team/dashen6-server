#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# author: yafei
# mongodb operations
import pymongo
from gateway_config import *
from bson.objectid import ObjectId


class DBOp:
    def __init__(self):
        self.connection = pymongo.Connection(dbHostname, dbPort)
        self.db = self.connection[dbName]
        self.user = self.db[dbUserTable]
        self.activity = self.db[dbActivityTable]
        self.msg_queue = self.db[dbMsgQueueTable]
        self.read_msg_queue = self.db[dbReadMsgQueueTable]

    def __del__(self):
        self.close()

    def close(self):
        if self.connection:
            self.connection.close()
            self.connection = None

    @staticmethod
    def _pull(queue, user):
        cursor = queue.find(
            {'user': user}
        )
        if cursor and cursor.count() == 1:
            queue = cursor[0].get('queue')
            if queue:
                return queue
        return None

    @staticmethod
    def _push(queue, user, message):
        if isinstance(message, list):
            queue.find_and_modify(
                query={'user': user},
                update={'$push': {'queue': {'$each': message}}},
                upsert=True
            )
        elif isinstance(message, str):
            queue.find_and_modify(
                query={'user': user},
                update={'$push': {'queue': message}},
                upsert=True
            )
        else:
            raise TypeError("message should be an instance of list or str")

    @staticmethod
    def new_id(queue):
        post = queue.insert({'status': 'allocated'})
        if post:
            return str(post)
        raise Exception('''couldn't create new id.''')

    @staticmethod
    def save_id(queue, _id, data):
        post = queue.find_and_modify(
            query={'_id': ObjectId(_id)},
            update={'$set': {'status': 'saved', 'data': data}},
            fields=['_id'])

        if post:
            _id = post.get('_id')
            if _id:
                return str(_id)

        raise Exception('''couldn't save id=%s, maybe it doesn't exist.''' % _id)

    @staticmethod
    def load_id(queue, _id):
        post = queue.find_one({'_id': ObjectId(_id)})
        if post is None:
            raise Exception('''couldn't load id=%s, maybe it doesn't exist.''' % _id)

        status = post.get('status')
        if status is None or status != 'saved':
            raise Exception('''couldn't load id=%s, it is uninitialized.''' % _id)

        data = post.get('data')
        if data is None:
            raise Exception('''couldn't load id=%s, couldn't find its data.''' % _id)

        return data
