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

"""
返回值格式
{
    "result": "success",
    "_id": "547be4086243577273ccc2de",
    "data": [
        {
            "action": "post",
            "type": "comment",
            "comment_id": "547f0f5a2d3a8c01a48fa054",
            "from": {
                "sex": "male",
                "name": "rlk_local",
                "imgUrl": "",
                "id": "547b48d46243577273ccc2dc"
            }
        }
    ]
}
"""
def message_template(_id, data):
    # TODO
    template = '{"result":"success", "_id":"%s", "data":%s}'
    return template % (_id, json.dumps(data))

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

def activity_comment_template(activity_id, comments):
    template = '{"result":"success","activity_id":"%s","comment_ids":%s}'
    return template % (activity_id, json.dumps(comments))

def comment_template(comment):
    template = '{"result":"success", "data":%s}'
    return template % comment

def comment_list_template(comment_list):
    result = []
    for item in comment_list:
        comment = item['data']
        result.append(comment)
    template = '{"result":"success", "data":%s}'
    return template % json.dumps(result)

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
        self.actions = ['get_all_activity', 'get_activity_comment']

    """
    获取某个活动的评论
        参数
            action=get_activity_comment&table=[table]&activity_id=[id]
        正常情况下返回返回status code "200 OK"
        结果格式如下:
            {"result":"success","activity_id":"%s","comment_ids":%s}
    """
    def parse_action_impl(self, action, table, db):
        if action == 'get_all_activity':
            data = db.get_all_activity()
            return data_template(data)
        elif action == 'get_activity_comment':
            activity_id = self.qs_dict.get('activity_id')
            if not activity_id:
                set_status_code(web, 400)
                return result_template('''Illegal parameters: no "activity_id"''')
            activity_id = ''.join(activity_id)
            if debug:
                web.debug('DB action=get_activity_comment, activity_id=%s' % activity_id)
            post = db.load(db_activity_table, activity_id)
            return activity_comment_template(activity_id, post['comments'])

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

class CommentQP(QueryParser):
    def __init__(self):
        QueryParser.__init__(self)
        self.actions = ['addComment', 'removeComment', 'getComment',  'getCommentList']

    """
    添加评论
        参数
            action=addComment&table=[table]
        正常情况下返回返回status code "200 OK"
        结果格式如下:
            {"result":"success","id":"xxx"}

    读取某一条评论
        参数
            action=getComment&table=[table]&id=[id]
        正常情况下返回返回status code "200 OK"
        结果格式如下:
            {"result":"success","data":"xxx"}

    读取一组评论
        参数
            action=getCommentList&table=[table]
        正常情况下返回返回status code "200 OK"
        结果格式如下:
            {"result":"success","data":"xxx"}

    删除评论
        参数
            action=removeComment&table=[table]&id=[id]
        正常情况下返回返回status code "200 OK"

    """
    def parse_action_impl(self, action, table, db):
        if action == 'addComment':
            # 字符串转化为map
            comment = json.loads(web.data())
            # 检查activity_id, user_id是否有效
            activity_id = comment['activity_id']
            user_name = comment['user_name']
            db.load(db_activity_table, activity_id)
            user = db.load_user(user_name)
            #comment集合中添加数据
            _id = db.new_and_save(table, {'data': comment})
            web.debug('DB data = %s'%comment)
            #Activity中添加'comments'
            db.push(db_activity_table, str(activity_id), 'comments', str(_id))
            #User中添加'comments'
            db.push(db_user_table, str(user['_id']), 'comments', str(_id))
            return id_template(_id)
        elif action == 'getComment':
            _id = self.qs_dict.get('id')
            if not _id:
                set_status_code(web, 400)
                return result_template('''Illegal parameters: no "id"''')
            _id = ''.join(_id)
            comment = db.load(db_comments_table, _id, {'status':False, '_id':False})
            comment['data']['id'] = _id
            web.debug("comment is %s" % comment)
            return comment_template(json.dumps(comment['data']))
        elif action == 'getCommentList':
            ids = json.loads(web.data())['ids']
            comment_list = db.load_list(db_comments_table, ids, {'status':False, '_id':False})
            web.debug("comment_list is %s" % comment_list)
            return comment_list_template(comment_list)
        elif action == 'removeComment':
            #检查id和对应的数据是否存在
            _id = self.qs_dict.get('id')
            if not _id:
                set_status_code(web, 400)
                return result_template('''Illegal parameters: no "id"''')
            _id = ''.join(_id)
            comment = db.load(db_comments_table, _id)
            #删除数据
            db.delete(db_comments_table, _id)
            #删除Activity中的评论
            db.pop(db_activity_table, comment['activity_id'], 'comments', _id)
            #删除User中的评论
            user = db.load_user(comment['user_name'])
            db.pop(db_user_table, user['_id'], 'comments', _id)
            return result_template('success')


