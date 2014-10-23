#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# author: yafei
# HTTP Gateway
import web
import hashlib
import urlparse
from db_op import DBOp
from gateway_config import *

USER = 'user'
TOKEN = 'token'
ID = 'id'
db = None
statusMap = {400: '400 Bad Request',
             401: '401 Unauthorized',
             500: '500 Internal Server Error'}


def gen_token(user, agent):
    """
    Token是下面字段的MD5的16进制字符串:
    1.用户名
    2.HTTP头部的"User-Agent"字段
    """
    m = hashlib.md5()
    m.update(user)
    if agent:
        m.update(agent)
    return m.hexdigest()


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


def id_data_template(_id, data):
    template = '{"result":"success","id":"%s","data":%s}'
    return template % (_id, data)

def username_data_template(username, data):
    template = '{"result":"success","username":"%s","data":%s}'
    return template % (username, data)

def exception_template(e):
    template = '{"result":"exception occurred","exception":"%s"}'
    return template % str(e)


def set_status_code(_web, code):
    status = statusMap.get(code)
    if status is None:
        status = '200 OK'
    _web.ctx.status = status


class Login:
    """
    HTTP gateway的登录流程
    1.客户端访问"/login",传入"user"参数(必须),填充HTTP头部的"User-Agent"字段(可选)
        例如"/login?user=laowu"
    2.HTTP gateway返回status code "200 OK",
    在HTTP头部通过"Set-Cookie"字段给客户端种Cookie,
    在接下来的所有接口访问中,客户端均需要在HTTP头部的"Cookie"字段携带这些Cookie.
    目前的Cookie包含下面字段:
        user
        token

    如果客户端重复登录,仍然返回status code "200 OK",但不会再设置Cookie.

    如果没有传入"user"参数,返回status code "401 Unauthorized"
    """

    def __init__(self):
        pass

    def GET(self):
        web.header('Content-Type', 'text/json')

        cookie = web.cookies()
        login, user, token = check_login(cookie)
        if login:
            return result_template('''Already login, User: %s, Token: %s''' % (user, token))

        qs = web.ctx.env.get('QUERY_STRING')
        if qs:
            qs_dict = urlparse.parse_qs(qs)
            user = qs_dict.get(USER)
            if user:
                user = ''.join(user)
                agent = web.ctx.env.get('HTTP_USER_AGENT')
                token = gen_token(user, agent)
                web.setcookie(USER, user, cookie_expires)
                web.setcookie(TOKEN, token, cookie_expires)
                if debug:
                    web.debug('Login user=%s, token=%s' % (user, token))
                return result_template('''Login OK, User: %s, Token: %s''' % (user, token))

        set_status_code(web, 401)
        return result_template('''Not login. Please use "?user=username" in query string''')


class NewId:
    """
    获取一个新的活动Id

    正常情况下返回返回status code "200 OK"
    结果格式如下:
        {"result":"success","id":"xxx"}
    """

    def __init__(self):
        pass

    def GET(self):
        web.header('Content-Type', 'text/json')

        cookie = web.cookies()
        login, user, token = check_login(cookie)
        if not login:
            set_status_code(web, 401)
            return not_login_template()

        try:
            _id = db.new_id(db.activity)
            if debug:
                web.debug('NewId id=%s' % _id)
            return id_template(_id)
        except Exception, e:
            web.debug(str(e))
            set_status_code(web, 500)
            return exception_template(e)


class SaveId:
    """
    保存活动信息

    使用POST method
    POST数据为: id + '\r\n' + data + '\r\n'

    正常情况下返回返回status code "200 OK"
    结果格式如下:
        {"result":"success","id":"xxx"}
    """

    def __init__(self):
        pass

    def POST(self):
        web.header('Content-Type', 'text/json')

        cookie = web.cookies()
        login, user, token = check_login(cookie)
        if not login:
            set_status_code(web, 401)
            return not_login_template()

        body = web.data()
        if body is None:
            set_status_code(web, 400)
            return result_template('Empty body')
        split = body.find('\r\n')
        end = body.rfind('\r\n')
        if split == -1 or end == -1 or split == end:
            set_status_code(web, 400)
            return result_template('Invalid body')

        _id = body[0:split]
        data = body[split + 2:end]
        if debug:
            web.debug('SaveId id=%s, data=%s' % (_id, data))

        try:
            _id = db.save(db.activity, _id, {'data': data})
            return id_template(_id)
        except Exception, e:
            web.debug(str(e))
            set_status_code(web, 500)
            return exception_template(e)


class LoadId:
    """
    加载活动信息

    参数
        id=[id]

    正常情况下返回返回status code "200 OK"
    结果格式如下:
        {"result":"success","id":"xxx","data":{...}}
    """

    def __init__(self):
        pass

    def GET(self):
        web.header('Content-Type', 'text/json')

        cookie = web.cookies()
        login, user, token = check_login(cookie)
        if not login:
            set_status_code(web, 401)
            return not_login_template()

        qs = web.ctx.env.get('QUERY_STRING')
        if qs:
            qs_dict = urlparse.parse_qs(qs)
            _id = qs_dict.get(ID)
            if _id:
                _id = ''.join(_id)
                if debug:
                    web.debug('LoadId id=%s' % _id)
                try:
                    data = db.load(db.activity, _id)
                    return id_data_template(_id, data['data'])
                except Exception, e:
                    web.debug(str(e))
                    set_status_code(web, 500)
                    return exception_template(e)

        set_status_code(web, 400)
        return result_template('''Please use "?id=xxx" in query string''')


class DB:
    """
    数据库增删改查功能

    使用POST method

    1.增
        参数
            action=new&table=[table]
        正常情况下返回返回status code "200 OK"
        结果格式如下:
            {"result":"success","id":"xxx"}
    2.改
        参数
            action=set&table=[table]
            action=set&table=[table]&id=[id]
            如果传入了id参数,则将更新对应的记录,否则新插入一条记录
        POST数据
            为数据,它将被保存到数据库
        正常情况下返回返回status code "200 OK"
        结果格式如下:
            {"result":"success","id":"xxx"}
    3.查
        参数
            action=get&table=[table]&id=[id]
        正常情况下返回返回status code "200 OK"
        结果格式如下:
            {"result":"success","id":"xxx","data":{...}}
    4.删
        参数
            action=del&table=[table]&id=[id]
        正常情况下返回返回status code "200 OK"
        结果格式如下:
            {"result":"success","id":"xxx"}
    """

    def __init__(self):
        pass

    def POST(self):
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
        qs_dict = urlparse.parse_qs(qs)

        action = qs_dict.get('action')
        table = qs_dict.get('table')
        if not action or not table:
            set_status_code(web, 400)
            return result_template('''Illegal parameters: no "action" nor "table"''')
        action = ''.join(action)
        table = ''.join(table)

        try:
            if action == 'new':
                _id = db.new_id(table)
                if debug:
                    web.debug('DB action=new, table=%s, id=%s' % (table, _id))
                return id_template(_id)
            elif action == 'set':
                _id = qs_dict.get('id')
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
                return id_template(_id)
            elif action == 'get':
                _id = qs_dict.get('id')
                if not _id:
                    set_status_code(web, 400)
                    return result_template('''Illegal parameters: no "id"''')
                _id = ''.join(_id)
                if debug:
                    web.debug('DB action=get, table=%s, id=%s' % (table, _id))
                data = db.load(table, _id)
                return id_data_template(_id, data['data'])
            elif action == 'del':
                _id = qs_dict.get('id')
                if not _id:
                    set_status_code(web, 400)
                    return result_template('''Illegal parameters: no "id"''')
                _id = ''.join(_id)
                if debug:
                    web.debug('DB action=del, table=%s, id=%s' % (table, _id))
                db.delete(table, _id)
                return id_template(_id)
            elif action == 'set_user':
                username = qs_dict.get('username')
                data = web.data()
                if not username:
                    set_status_code(web, 400)
                    return result_template('''Illegal parameters: no "username"''')
                if debug:
                    web.debug('DB action=get, username=%s' % (username))
                username = db.set_user(username, {'data': data})
                return username
                
            elif action == 'get_user':
                username = qs_dict.get('username')
                if not username:
                    set_status_code(web, 400)
                    return result_template('''Illegal parameters: no "username"''')
                if debug:
                    web.debug('DB action=get_user, username=%s' % (username))
                data = db.load_user(username)
                return username_data_template(username, data['data'])    
            else:
                return result_template('''Illegal parameters: "action=%s"''' % action)
        except Exception, e:
            web.debug(str(e))
            set_status_code(web, 500)
            return exception_template(e)


if __name__ == '__main__':
    db = DBOp()
    urls = (
        '/login', 'Login',
        '/newid', 'NewId',
        '/saveid', 'SaveId',
        '/loadid', 'LoadId',
        '/db', 'DB',
    )
    app = web.application(urls, globals())
    app.run()
