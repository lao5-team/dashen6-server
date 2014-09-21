#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# author: yafei
# HTTP Gateway configurations


'''
debug开关
'''
debug = True

'''
Cookie的超时时间(单位:秒)
'''
cookieExpires = 3600

'''
mongodb的hostname
'''
dbHostname = 'localhost'
'''
mongodb的端口
'''
dbPort = 27017
'''
mongodb的数据库名
'''
dbName = 'db'
'''
mongodb的"用户"表名(表对应mongodb中的collection,下同)
'''
dbUserTable = 'user'
'''
mongodb的"活动"表名
'''
dbActivityTable = 'activity'
'''
mongodb的"消息队列"表名
'''
dbMsgQueueTable = 'msg'
'''
mongodb的"已读消息队列"表名
'''
dbReadMsgQueueTable = 'read_msg'
