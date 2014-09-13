#! /usr/bin/env python
#
# author: yafei
# HTTP Gateway
import web
import hashlib
import urlparse

# configurations
cookieExpires = 3600
# end of configurations

urls = (
        '/login', 'Login',
        )
app = web.application(urls, globals())

def genToken(user, agent):
    m = hashlib.md5()
    m.update(user)
    if agent is not None:
        m.update(agent)
    return m.hexdigest()

def checkLogin(cookie):
    user = cookie.get('user')
    if user is not None:
        token = cookie.get('token')
        if token is not None:
            return True,user,token
    return False,None,None

class Login:
    def GET(self):
        web.header('Content-Type', 'text/plain')

        cookie = web.cookies()
        login,user,token = checkLogin(cookie)
        if login:
            return 'Already login\nUser: %s\nToken: %s\n' % (user, token)

        qs = web.ctx.env.get('QUERY_STRING')
        if qs is not None:
            qsDict = urlparse.parse_qs(qs)
            user = qsDict.get('user')
            if user is not None:
                user = ''.join(user)
                agent = web.ctx.env.get('HTTP_USER_AGENT')
                token = genToken(user, agent)
                web.setcookie('user', user, cookieExpires)
                web.setcookie('token', token, cookieExpires)
                return 'Login OK\nUser: %s\nToken: %s\n' % (user, token)

        web.ctx.status = '401 Unauthorized'
        return 'Not login. Please use "?user=username" in query string\n'

#class Default:
#    def GET(self, param):
#        print 'Default'
#        return str(param)

if __name__ == '__main__':
    app.run()
