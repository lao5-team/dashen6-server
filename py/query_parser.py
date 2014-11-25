#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# author: yihao

import web
import hashlib
import urlparse
import json
from gateway_config import *
USER = 'user'
TOKEN = 'token'
ID = 'id'

statusMap = {400: '400 Bad Request',
             401: '401 Unauthorized',
             500: '500 Internal Server Error'}

def check_login(cookie):
    """
    检查用户是否登录
    """
    if cookie:
        user = cookie.get(USER)
        if user:
            token = cookie.get(TOKEN)
            if token:
                return True, user, token
    return False, None, None

def not_login_template():
    return '{"result":"not login"}'


def result_template(message):
    template = '{"result":"%s"}'
    return template % message


def id_template(_id):
    template = '{"result":"success","id":"%s"}'
    return template % _id

def data_template(data):
    template = '{"result":"success","data":%s}'
    return template % data

def id_data_template(_id, data):
    template = '{"result":"success","id":"%s","data":%s}'
    return template % (_id, data)

def username_data_template(username, data, _id):
    # TODO
    template = '{"result":"success", "username":"%s", "data":%s, "_id":"%s"}'
    return template % (username, data, _id)

def message_template(_id, data):
    # TODO
    template = '{"result":"success", "_id":"%s", "data":%s}'
    return template % (_id, data)

def user_activity_template(username, doing_activity, finish_activity):
    """
    for index,item in enumerate(doing_activity):
        doing_activity[index] = str(doing_activity[index])
    for index,item in enumerate(finish_activity):
        finish_activity[index] = str(finish_activity[index])
    """
    template = '{"result":"success","username":"%s","doing_activity":%s,"finish_activity":%s}'
    if doing_activity is None:
        doing_activity = ''
    if finish_activity is None:
        finish_activity = ''
    return template % (username, json.dumps(doing_activity), json.dumps(finish_activity))

def exception_template(e):
    template = '{"result":"exception occurred","exception":"%s"}'
    return template % str(e)

def set_status_code(_web, code):
    status = statusMap.get(code)
    if status is None:
        status = '200 OK'
    _web.ctx.status = status

class QueryParser:
    def __init__(self):
        self.actions = []
        self.qs_dict = None
    def parse_action(self, web, db):

        web.header('Content-Type', 'text/json')
        cookie = web.cookies()
        login, user, token = check_login(cookie)
        if not login:
            set_status_code(web, 401)
            return not_login_template()

        qs = web.ctx.env.get('QUERY_STRING')
        if not qs:
            set_status_code(web, 400)
            return result_template('''No parameters''')
        self.qs_dict = urlparse.parse_qs(qs)

        action = self.qs_dict.get('action')
        table = self.qs_dict.get('table')
        if not action or not table:
            set_status_code(web, 400)
            return result_template('''Illegal parameters: no "action" nor "table"''')
        action = ''.join(action)
        table = ''.join(table)
        if action in self.actions:
            try:
                return self.parse_action_impl(action, table, db)
            except Exception, e:
                web.debug(str(e))
                set_status_code(web, 500)
                return exception_template(e)
        else:
            return None

    def parse_action_impl(self, action, table, db):
        pass


class GenericQP(QueryParser):
    def __init__(self):
        QueryParser.__init__(self)
        self.actions = ['new','set', 'get', 'del']

    def parse_action_impl(self, action, table, db):
        if action == 'new':
            _id = db.new_id(table)
            if debug:
                web.debug('DB action=new, table=%s, id=%s' % (table, _id))
            return id_template(_id)
        elif action == 'set':
            _id = self.qs_dict.get('id')
            data = web.data()
            if not data:
                set_status_code(web, 400)
                return result_template('''Illegal parameters: no "data"''')
            if _id:
                _id = ''.join(_id)
                if debug:
                    web.debug('DB action=set, table=%s, id=%s' % (table, _id))
                _id = db.save(table, _id, {'data': data})
            else:
                if debug:
                    web.debug('DB action=set, table=%s' % table)
                _id = db.new_and_save(table, {'data': data})
            web.debug('DB data = %s', data)
            return id_template(_id)
        elif action == 'get':
            _id = self.qs_dict.get('id')
            if not _id:
                set_status_code(web, 400)
                return result_template('''Illegal parameters: no "id"''')
            _id = ''.join(_id)
            if debug:
                web.debug('DB action=get, table=%s, id=%s' % (table, _id))
            data = db.load(table, _id)
            return id_data_template(_id, data['data'])
        elif action == 'del':
            _id = self.qs_dict.get('id')
            if not _id:
                set_status_code(web, 400)
                return result_template('''Illegal parameters: no "id"''')
            _id = ''.join(_id)
            if debug:
                web.debug('DB action=del, table=%s, id=%s' % (table, _id))
            db.delete(table, _id)
            return id_template(_id)
        else:
            return result_template('''Illegal parameters: "action=%s"''' % action)


class ActivityQP(QueryParser):
    def __init__(self):
        QueryParser.__init__(self)
        self.actions = ['get_all_activity']

    def parse_action_impl(self, action, table, db):
        data = db.get_all_activity()
        return data_template(data)

class UserQP(QueryParser):
    def __init__(self):
        QueryParser.__init__(self)
        self.actions = ['set_user', 'get_user']

    def parse_action_impl(self, action, table, db):
        if action == 'set_user':
            username = self.qs_dict.get('username')
            if not username:
                set_status_code(web, 400)
                return result_template('''Illegal parameters: no "username"''')
            username = ''.join(username)

            data = web.data()
            # TODO

            if debug:
                web.debug('DB action=set_user, username=%s' % username)
            username = db.set_user(username, {'data': data})
            return username
        if action == 'get_user':
            username = self.qs_dict.get('username')
            if not username:
                set_status_code(web, 400)
                return result_template('''Illegal parameters: no "username"''')
            username = ''.join(username)

            if debug:
                web.debug('DB action=get_user, username=%s' % username)
            data = db.load_user(username)
            return username_data_template(username, data['data'], data['_id'])

class UserActivityQP(QueryParser):
    def __init__(self):
        QueryParser.__init__(self)
        self.actions = ['add_user_activity', 'remove_user_activity', 'move_user_activity', 'get_user_activity']

    def parse_action_impl(self, action, table, db):
        if action == 'add_user_activity':
            user_id = self.qs_dict.get('user_id')
            if not user_id:
                set_status_code(web, 400)
                return result_template('''Illegal parameters: no "user_id"''')
            user_id = ''.join(user_id)
            field = self.qs_dict.get('field')
            if not field:
                set_status_code(web, 400)
                return result_template('''Illegal parameters: no "field"''')
            field = ''.join(field)
            activity_id = self.qs_dict.get('activity_id')
            if not activity_id:
                set_status_code(web, 400)
                return result_template('''Illegal parameters: no "activity_id"''')
            activity_id = ''.join(activity_id)
            if debug:
                web.debug(
                    'DB action=add_user_activity, user_id=%s, field=%s, activity_id=%s' % (user_id, field, activity_id))
            db.add_user_activity(user_id, field, activity_id)
            data = db.get_user_activity(user_id)
            return user_activity_template(user_id, data['doing_activity'], data['finish_activity'])

        elif action == 'remove_user_activity':
            user_id = self.qs_dict.get('user_id')
            if not user_id:
                set_status_code(web, 400)
                return result_template('''Illegal parameters: no "user_id"''')
            user_id = ''.join(user_id)
            field = self.qs_dict.get('field')
            if not field:
                set_status_code(web, 400)
                return result_template('''Illegal parameters: no "field"''')
            field = ''.join(field)
            activity_id = self.qs_dict.get('activity_id')
            if not activity_id:
                set_status_code(web, 400)
                return result_template('''Illegal parameters: no "activity_id"''')
            activity_id = ''.join(activity_id)
            if debug:
                web.debug('DB action=remove_user_activity, user_id=%s, field=%s, activity_id=%s' % (
                user_id, field, activity_id))
            db.remove_user_activity(user_id, field, activity_id)
            data = db.get_user_activity(user_id)
            return user_activity_template(user_id, data['doing_activity'], data['finish_activity'])

        elif action == 'move_user_activity':
            user_id = self.qs_dict.get('user_id')
            if not user_id:
                set_status_code(web, 400)
                return result_template('''Illegal parameters: no "user_id"''')
            user_id = ''.join(user_id)
            field_source = self.qs_dict.get('field_source')
            if not field_source:
                set_status_code(web, 400)
                return result_template('''Illegal parameters: no "field_source"''')
            field_source = ''.join(field_source)
            field_dest = self.qs_dict.get('field_dest')
            if not field_dest:
                set_status_code(web, 400)
                return result_template('''Illegal parameters: no "field_dest"''')
            field_dest = ''.join(field_dest)
            activity_id = self.qs_dict.get('activity_id')
            if not activity_id:
                set_status_code(web, 400)
                return result_template('''Illegal parameters: no "activity_id"''')
            activity_id = ''.join(activity_id)
            if debug:
                web.debug('DB action=move_user_activity, user_id=%s, field_source=%s, field_dest=%s, activity_id=%s' % (
                user_id, field_source, field_dest, activity_id))
            db.remove_user_activity(user_id, field_source, activity_id)
            db.add_user_activity(user_id, field_dest, activity_id)
            data = db.get_user_activity(user_id)
            return user_activity_template(user_id, data['doing_activity'], data['finish_activity'])

        elif action == 'get_user_activity':
            user_id = self.qs_dict.get('user_id')
            if not user_id:
                set_status_code(web, 400)
                return result_template('''Illegal parameters: no "user_id"''')
            user_id = ''.join(user_id)
            if debug:
                web.debug('DB action=get_user_activity, user_id=%s' % user_id)
            data = db.get_user_activity(user_id)
            return user_activity_template(user_id, data['doing_activity'], data['finish_activity'])

class UserMessageQP(QueryParser):
    def __init__(self):
        QueryParser.__init__(self)
        self.actions = ['add_user_message', 'get_user_message', 'remove_user_message']

    def parse_action_impl(self, action, table, db):
        if action == 'add_user_message':
            user_id = self.qs_dict.get('user_id')
            if not user_id:
                set_status_code(web, 400)
                return result_template('''Illegal parameters: no "user_id"''')
            user_id = ''.join(user_id)
            if debug:
                web.debug('DB action=add_user_message, user_id=%s' % (user_id))
            data = web.data()
            db.add_user_message(user_id, data)
            return ''
        elif action == 'get_user_message':
            user_id = self.qs_dict.get('user_id')
            if not user_id:
                set_status_code(web, 400)
                return result_template('''Illegal parameters: no "user_id"''')
            user_id = ''.join(user_id)
            if debug:
                web.debug('DB action=get_user_message, user_id=%s' % (user_id))
            data = db.get_user_message(user_id)
            return message_template(user_id, data)
        elif action == 'remove_user_message':
            user_id = self.qs_dict.get('user_id')
            if not user_id:
                set_status_code(web, 400)
                return result_template('''Illegal parameters: no "user_id"''')
            user_id = ''.join(user_id)
            if debug:
                web.debug('DB action=get_user_message, user_id=%s' % (user_id))
            data = web.data()
            list1 = json.loads(data);
            db.remove_user_message(user_id, list1, web)
            return ''


class PictureInfoQP(QueryParser):
    def __init__(self):
        QueryParser.__init__(self)
        self.actions = ['get_all_picture_info']

    def parse_action_impl(self, action, table, db):
        data = db.get_all_picture_info()
        return data_template(data)