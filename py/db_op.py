#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# author: yafei
# mongodb operations
import pymongo
from gateway_config import *
from bson.objectid import ObjectId
from pymongo.collection import Collection
import json
STATUS_OK = 'ok'
STATUS_DELETED = 'deleted'


class DBOp:
    def __init__(self):
        self.connection = pymongo.Connection(db_hostname, db_port)
        self.db = self.connection[db_name]
        self.user = self.db[db_user_table]
        self.user.ensure_index('username', unique=True)
        self.activity = self.db[db_activity_table]
        self.unit_test = self.db[db_unit_test_table]
        self.user_activity = self.db[db_user_activity_table]
        self.message = self.db[db_message_table]
        self.user_message = self.db[db_user_message_table]
        self.TABLE_MAP = {
            db_user_table: self.user,
            db_activity_table: self.activity,
            db_unit_test_table: self.unit_test,
            db_user_activity_table: self.user_activity,
            db_message_table: self.message,
            db_user_message_table: self.user_message
        }
        self.VALID_TABLES = self.TABLE_MAP.keys()
        self.web = None

    def __del__(self):
        self.close()

    def set_web(self, web):
        """
        设置web，以方便打印日志
        :param web:
        :return:
        """
        self.web = web

    def check_table(self, table):
        """
        检查是否是有效表名
        """
        for t in self.VALID_TABLES:
            if table.name == t:
                return
        raise Exception('''Couldn't operation on table %s.''' % table.name)

    def table2obj(self, table):
        """
        由表名得到表对象
        """
        obj = self.TABLE_MAP.get(table)
        if obj:
            return obj
        raise Exception('''Couldn't operation on table %s.''' % table)

    def get_safe_table(self, table):
        if isinstance(table, Collection):
            self.check_table(table)
            return table
        elif isinstance(table, str):
            return self.table2obj(table)
        else:
            raise TypeError('''"table" should be an instance of pymongo.collection.Collection or str.''')

    def close(self):
        if self.connection:
            self.connection.close()
            self.connection = None

    def new_id(self, table):
        """
        在table中,创建一条记录,返回id
        """
        table = self.get_safe_table(table)
        post = table.insert({'status': STATUS_OK})
        if post:
            return str(post)
        raise Exception('''Couldn't create new id.''')

    def save(self, table, _id, data_map):
        """
        在table中,更新/保存_id的数据,返回id
        """
        table = self.get_safe_table(table)
        data_map['status'] = STATUS_OK
        post = table.find_and_modify(
            query={'_id': ObjectId(_id)},
            update={'$set': data_map},
            fields=['_id'])

        if post:
            _id = post.get('_id')
            if _id:
                return str(_id)
        raise Exception('''Couldn't save id=%s, it doesn't exist.''' % _id)


    def new_and_save(self, table, data_map):
        """
        在table中,创建数据,返回id
        """
        table = self.get_safe_table(table)
        data_map['status'] = STATUS_OK
        post = table.insert(data_map)
        if post:
            return str(post)
        raise Exception('''Couldn't create new id and data record.''')

    def load(self, table, _id, fields=None):
        """
        在table中,读取_id的数据并返回
        """
        table = self.get_safe_table(table)
        post = table.find_one({'_id': ObjectId(_id), 'status': STATUS_OK}, fields=fields)
        if post is None:
            raise Exception('''Couldn't load id=%s, it doesn't exist or deleted.''' % _id)
        if not post.get('data'):
            raise Exception('''Couldn't load data for id=%s, it is a newly created id.''' % _id)
        return post

    def delete(self, table, _id):
        """
        在table中,删除_id的数据,返回id
        注意,没有真正删除数据,而是将status置为deleted
        """
        table = self.get_safe_table(table)
        post = table.find_and_modify(
            query={'_id': ObjectId(_id)},
            update={'$set': {'status': STATUS_DELETED}},
            fields=['_id'])

        if post:
            _id = post.get('_id')
            if _id:
                return str(_id)
        raise Exception('''Couldn't delete id=%s, it doesn't exist.''' % _id)

    def set_user(self, username, data_map):
        """
        在table user中，创建数据，并返回username
        """
        table = self.get_safe_table(db_user_table)
        post = table.find_and_modify(
            query={'username': username},
            update={'$set': data_map},
            upsert=True,
            fields={'username': True, '_id': False}
            )
        if post:
            username = post.get('username')
            if username:
                return username
        raise Exception('''Couldn't save user with username=%s, it doesn't exist.''' % username)

    def load_user(self, username, fields=None):
        """
        在table user中,读取username的数据并返回$
        """
        table = self.get_safe_table(db_user_table)
        post = table.find_one({'username': username}, fields=fields)
        if post is None:
            raise Exception('''Couldn't load username=%s, it doesn't exist or deleted.''' % username)
        if not post.get('data'):
            raise Exception('''Couldn't load data for username=%s.''' % username)
        return post


    def push(self, table, _ids, field, values):
        """
        在table中,向_ids的field字段对应的队列中中添加一条或多条数据
        """
        table = self.get_safe_table(table)
        if isinstance(values, list):
            update = {'$addToSet': {field: {'$each': values}}}
        elif isinstance(values, str):
            update = {'$addToSet': {field: values}}
        else:
            raise TypeError('''"values" should be an instance of list or str.''')

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

    def pop(self, table, _ids, field, values):
        """
        在table中,从_ids的field字段对应的队列中中删除一条或多条数据
        """
        table = self.get_safe_table(table)
        #web.debug(values)
        if isinstance(values, list):
            update = {'$pullAll': {field: values}}
            #web.debug('values is list')
        elif isinstance(values, str):
            update = {'$pullAll': {field: [values]}}
            #web.debug('values is str')
        else:
            raise TypeError('''"values" should be an instance of list or str.''')

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

    def add_user_activity(self, _ids, field, activity):
        """
        在user_activity 集合中，对应的field字段，添加一条或多条活动数据
        :param _ids:
        :param field:
        :param values:
        :return:
        """
        activity = str(activity)
        self.push(db_user_activity_table, _ids, field, activity)

    def remove_user_activity(self, _ids, field, activity):
        """
        在user_activity 集合中，对应的field字段，移除一条或多条数据
        :param _ids:
        :param field:
        :param values:
        :return:
        """
        activity = str(activity)
        self.pop(db_user_activity_table, _ids, field, activity)

    def get_user_activity(self, user_id, fields=None):
        """
        在user_activity 集合中，获取其所有的activity id，即doing_activity, finish_activity
        :return:
        """
        table = self.get_safe_table(db_user_activity_table)
        post = table.find_one({'_id': ObjectId(user_id)}, fields=fields)
        if not 'doing_activity' in post:
            post['doing_activity'] = []
        if not 'finish_activity' in post:
            post['finish_activity'] = []
        if post is None:
            raise Exception('''Couldn't load user_id=%s, it doesn't exist or deleted.''' % user_id)
        return post

    def add_message(self, data):
        """
        在message集合中，添加一条message
        :param data: message 数据
        :return: message id
        """
        self.web.debug('add_message')
        jData = json.loads(data)
        self.web.debug('jData is %s' % str(jData))
        id = self.new_and_save(db_message_table, {'data':jData})
        return id

    def add_user_message(self, _ids, data):
        """
        在user_message 集合中，对应的field字段，移除一条或多条message
        :param _ids:
        :param data: 消息数据
        :return:
        """
        self.web.debug('add_user_message')
        id = self.add_message(data)
        self.push(db_user_message_table, _ids, "user_message", id)

    def remove_user_message(self, _ids, message_ids):
        """
        在user_message 集合中，对应的field字段，移除一条或多条message
        :param _ids:
        :param data: 消息数据
        :return:
        """
        self.pop(db_user_message_table, _ids, "user_message", message_ids)

    def get_user_message(self, user_id, fields=None):
        """
        在user_message 集合中，获取其所有的message
        :return:
        """
        #table = self.get_safe_table(db_user_message_table)
        post = self.user_message.find_one({'_id': ObjectId(user_id)}, fields=fields)
        self.web.debug('post is %s' % str(post))
        if post is None:
            raise Exception('''Couldn't load user_id=%s, it doesn't exist or deleted.''' % user_id)
        result = '{"messages":['
        for message_id in post['user_message']:
            message = self.message.find_one({'_id': ObjectId(message_id)}, fields={'status':False, '_id':False})
            self.web.debug('messge %s' % str(message))
            message = message['data']
            result = result + json.dumps(message) + ' ,'
        result = result[0:len(result)-1] + ']}'
        self.web.debug('result %s' % result)
        self.pop('user_message', user_id, 'user_message', post['user_message'])
        return result
