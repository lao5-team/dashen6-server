#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os

from com.hws.s3.client.huawei_s3 import HuaweiS3
from com.hws.s3.models.owner import Owner
from com.hws.s3.models.s3object import S3Object
from com.hws.s3.models.grantee import Grantee
from com.hws.s3.models.grantee import Group
from com.hws.s3.models.grant import Grant
from com.hws.s3.models.grant import Permission
from com.hws.s3.models.acl import ACL


def hws_test():
    AK = "F7160B480A5E67431C75"
    SK = "19oGfWwCbvSpmPfwiGxYOjl1EKUAAAFJCl5nQ/S6"
    s3 = HuaweiS3(AK, SK, is_secure=False, server='s3.hwclouds.com')
    bucket_name = "galneryus"

    # print 'name: %s' % s3.get_canonical_username()
    # print 'id: %s' % s3.get_canonical_userid()

    headers = {'x-amz-acl': ['public-read']}

    # bucket
    if not s3.check_bucket_exists(bucket_name):
        bucket = s3.create_bucket(bucket_name, headers=headers)
        print bucket.status, bucket.reason

    # ===========================================================================
    # list buckets
    # ===========================================================================
    lmb = s3.list_buckets()
    bucket_list = lmb.entries

    print "buckets:"
    for bk in bucket_list:
        print '    %s' % bk.name

    print "putting %s" % __file__
    file_path = __file__
    objkey = os.path.basename(file_path)

    metadata = {}  # 元数据用字典表示，其中的value必须使用列表类型
    metadata["a"] = ["1"]
    metadata["b"] = ["2"]

    s3b = S3Object(file_path, metadata)
    obj = s3.create_object(bucket_name, objkey, s3b, headers=headers)
    print obj.status, obj.reason
    print 'URL: %s' % s3.get_object_url(bucket_name, objkey)


if __name__ == '__main__':
    hws_test()
