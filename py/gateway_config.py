#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# author: yafei
# HTTP Gateway configurations

"""
debug开关
"""
debug = True
"""
Cookie的超时时间(单位:秒)
"""
cookie_expires = 3600
"""
mongodb的hostname
"""
db_hostname = 'localhost'
"""
mongodb的端口
"""
db_port = 27017
"""
mongodb的数据库名
"""
db_name = 'db'
"""
mongodb的"用户"表名(表对应mongodb中的collection,下同)
"""
db_user_table = 'user'
"""
mongodb的"活动"表名
"""
db_activity_table = 'activity'
"""
单元测试使用的表名
"""
db_unit_test_table = 'ut'

"""
mongodb的"用户，活动"表名
"""
db_user_activity_table = 'user_activity'

"""
mongodb的"消息"表名
"""
db_message_table = 'message'

"""
mongodb的"用户，消息"表名
"""
db_user_message_table = 'user_message'

"""
mongodb的"图片信息"表名
"""
db_picture_info_table = 'picture_info'