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

valid_tables = [db_user_table, db_activity_table, db_unit_test_table]


def check_table(table):
    """
    检查是否是有效表名
    """
    for t in valid_tables:
        if table.name == t:
            return
    raise Exception('''couldn't operation on table %s.''' % table)
