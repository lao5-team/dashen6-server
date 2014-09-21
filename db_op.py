#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# author: yafei
# mongodb operations
import pymongo
from gateway_config import *


class DBOp:
    def __init__(self):
        self.connection = pymongo.Connection(dbHostname, dbPort)
        self.db = self.connection[dbName]
        self.user = self.db[dbUserTable]
        self.activity = self.db[dbActivityTable]
        self.msgQuene = self.db[dbMsgQueueTable]
        self.readMsgQuene = self.db[dbReadMsgQueueTable]

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
    def _newId(queue):
        post = queue.insert({'status': 'allocated'})
        if post:
            return str(post)
        else:
            return None
