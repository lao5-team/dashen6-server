#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# author: yafei
# HTTP Gateway
import web
import hashlib
import urlparse
from gateway_config import *

urls = (
    '/login', 'Login',
    '/pull', 'PullMsg',
    '/delete', 'DeleteMsg',
)
app = web.application(urls, globals())
USER = 'user'
TOKEN = 'token'

'''
Token是下面字段的MD5的16进制字符串:
1.用户名
2.HTTP头部的"User-Agent"字段
'''


def genToken(user, agent):
    m = hashlib.md5()
    m.update(user)
    if agent:
        m.update(agent)
    return m.hexdigest()


'''
检查用户是否登录
'''


def checkLogin(cookie):
    if cookie:
        user = cookie.get(USER)
        if user:
            token = cookie.get(TOKEN)
            if token:
                return True, user, token
    return False, None, None


def loginJsonTemplate(message):
    template='''
{
    "result":"%s"
}
    '''
    return template % message


'''
HTTP gateway的登录流程
1.客户端访问"/login",传入"user"参数(必须),填充HTTP头部的"User-Agent"字段(可选)
    例如"/login?user=laowu"
2.HTTP gateway返回status code "200 OK",
在HTTP头部通过"Set-Cookie"字段给客户端种Cookie,
在接下来的所有访问中,客户端均需要在HTTP头部的"Cookie"字段携带这些Cookie.
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
        login, user, token = checkLogin(cookie)
        if login:
            return loginJsonTemplate('Already login, User: %s, Token: %s' % (user, token))

        qs = web.ctx.env.get('QUERY_STRING')
        if qs:
            qsDict = urlparse.parse_qs(qs)
            user = qsDict.get(USER)
            if user:
                user = ''.join(user)
                agent = web.ctx.env.get('HTTP_USER_AGENT')
                token = genToken(user, agent)
                web.setcookie(USER, user, cookieExpires)
                web.setcookie(TOKEN, token, cookieExpires)
                return loginJsonTemplate('Login OK, User: %s, Token: %s' % (user, token))

        web.ctx.status = '401 Unauthorized'
        return loginJsonTemplate('Not login. Please use "?user=username" in query string')


'''
客户端拉取消息
'''


class PullMsg:
    def GET(self, param):
        print 'PullMsg'
        return str(param)


'''
客户端删除消息
'''


class DeleteMsg:
    def GET(self, param):
        print 'PullMsg'
        return str(param)


if __name__ == '__main__':
    app.run()
