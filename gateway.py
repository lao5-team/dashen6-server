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

urls = (
    '/login', 'Login',
    '/pull', 'PullMsg',
    '/delete', 'DeleteMsg',
    '/newid', 'NewId',
    '/saveid', 'SaveId',
    '/loadid', 'LoadId',
)
app = web.application(urls, globals())
USER = 'user'
TOKEN = 'token'
ID = 'id'

db = DBOp()

statusMap = {400: '400 Bad Request',
             401: '401 Unauthorized',
             500: '500 Internal Server Error',
             }

'''
Token是下面字段的MD5的16进制字符串:
1.用户名
2.HTTP头部的"User-Agent"字段
'''


def gen_token(user, agent):
    m = hashlib.md5()
    m.update(user)
    if agent:
        m.update(agent)
    return m.hexdigest()


'''
检查用户是否登录
'''


def check_login(cookie):
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
    template = '{"result":"success","id":"%s","data":{%s}}'
    return template % (_id, data)


def exception_template(e):
    template = '{"result":"exception occurred","exception":"%s"}'
    return template % str(e)


def set_status_code(_web, code):
    status = statusMap.get(code)
    if status is None:
        status = '200 OK'
    _web.ctx.status = status


'''
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
'''


class Login:
    def GET(self):
        web.header('Content-Type', 'text/json')

        cookie = web.cookies()
        login, user, token = check_login(cookie)
        if login:
            return result_template('Already login, User: %s, Token: %s' % (user, token))

        qs = web.ctx.env.get('QUERY_STRING')
        if qs:
            qs_dict = urlparse.parse_qs(qs)
            user = qs_dict.get(USER)
            if user:
                user = ''.join(user)
                agent = web.ctx.env.get('HTTP_USER_AGENT')
                token = gen_token(user, agent)
                web.setcookie(USER, user, cookieExpires)
                web.setcookie(TOKEN, token, cookieExpires)
                return result_template('Login OK, User: %s, Token: %s' % (user, token))

        set_status_code(web, 401)
        return result_template('''Not login. Please use '?user=username' in query string''')


'''
客户端从消息队列拉取消息
'''


class PullMsg:
    def GET(self):
        web.header('Content-Type', 'text/json')

        cookie = web.cookies()
        login, user, token = check_login(cookie)
        if not login:
            set_status_code(web, 401)
            return not_login_template()

        print 'PullMsg'
        return ''


'''
客户端删除消息队列消息,通常是删除已读消息
'''


class DeleteMsg:
    def GET(self):
        web.header('Content-Type', 'text/json')

        cookie = web.cookies()
        login, user, token = check_login(cookie)
        if not login:
            set_status_code(web, 401)
            return not_login_template()

        print 'DeleteMsg'
        return ''


'''
获取一个新的活动Id

正常情况下返回返回status code "200 OK"
结果格式如下:
{"result":"success","id":"xxx"}
'''


class NewId:
    def GET(self):
        web.header('Content-Type', 'text/json')

        # cookie = web.cookies()
        # login, user, token = check_login(cookie)
        # if not login:
        #     set_status_code(web, 401)
        #     return not_login_template()

        try:
            _id = db.new_id(db.activity)
            if debug:
                print 'NewId id=%s' % _id
            return id_template(_id)
        except Exception, e:
            set_status_code(web, 500)
            return exception_template(e)


'''
保存活动信息

使用POST method
POST数据为: id + '\r\n' + data + '\r\n'

正常情况下返回返回status code "200 OK"
结果格式如下:
{"result":"success","id":"xxx"}
'''


class SaveId:
    def POST(self):
        web.header('Content-Type', 'text/json')

        # cookie = web.cookies()
        # login, user, token = check_login(cookie)
        # if not login:
        #     set_status_code(web, 401)
        #     return not_login_template()

        body = web.data()
        if body is None:
            set_status_code(web, 400)
            return result_template('empty body')
        split = body.find('\r\n')
        end = body.rfind('\r\n')
        if split == -1 or end == -1 or split == end:
            set_status_code(web, 400)
            return result_template('invalid body')

        _id = body[0:split]
        data = body[split + 2:end]
        if debug:
            print 'SaveId id=%s, data=%s' % (_id, data)

        try:
            _id = db.save_id(db.activity, _id, data)
            return id_template(_id)
        except Exception, e:
            set_status_code(web, 500)
            return exception_template(e)


'''
加载活动信息

本接口需要传入"id"参数(必须)
    例如"/loadid?id=xxx"

正常情况下返回返回status code "200 OK"
结果格式如下:
{"result":"success","id":"xxx","data":{...}}
'''


class LoadId:
    def GET(self):
        web.header('Content-Type', 'text/json')

        # cookie = web.cookies()
        # login, user, token = check_login(cookie)
        # if not login:
        #     set_status_code(web, 401)
        #     return not_login_template()

        qs = web.ctx.env.get('QUERY_STRING')
        if qs:
            qs_dict = urlparse.parse_qs(qs)
            _id = qs_dict.get(ID)
            if _id:
                _id = ''.join(_id)
                if debug:
                    print 'LoadId id=%s' % _id
                try:
                    data = db.load_id(db.activity, _id)
                    return id_data_template(_id, data)
                except Exception, e:
                    set_status_code(web, 500)
                    return exception_template(e)

        set_status_code(web, 400)
        return result_template('''Please use '?id=xxx' in query string''')


if __name__ == '__main__':
    app.run()
