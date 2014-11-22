#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# author: yafei
# photo server
import web
from gateway import set_status_code, result_template, exception_template
from com.hws.s3.client.huawei_s3 import HuaweiS3
from com.hws.s3.utils.utils import Utils
from com.hws.s3.utils.request_format import PathFormat

"""
debug开关
"""
debug = True
"""
hws的配置
"""
hws_AK = 'F4B00892050916A70207' #'F7160B480A5E67431C75'
hws_SK = 'vJCIP5JRd0xM7t1F9NfmrSQZDs4AAAFJBQkWp+z5' #'19oGfWwCbvSpmPfwiGxYOjl1EKUAAAFJCl5nQ/S6'
hws_ssl = False
hws_server = 's3.hwclouds.com'
hws_bucket_name = "galneryus"
hws_headers = {'x-amz-acl': ['public-read']}


def url_template(_id):
    template = '{"result":"success","url":"%s"}'
    return template % _id


def initialize_bucket():
    s3 = HuaweiS3(hws_AK, hws_SK, is_secure=hws_ssl, server=hws_server)
    if not s3.check_bucket_exists(hws_bucket_name):
        print 'Bucket %s does not exist, create it.' % hws_bucket_name
        result = s3.create_bucket(hws_bucket_name, headers=hws_headers)
        print result.status, result.reason
    else:
        print 'Bucket %s exists' % hws_bucket_name


class MyHuaweiS3(HuaweiS3):
    def make_request2(self, method, bucket, key, data, headers):
        calling_format = Utils.get_callingformat_for_bucket(self.calling_format, bucket)

        if self.is_secure and not isinstance(calling_format, PathFormat) and bucket.find(".") != -1:
            raise Exception("You are making an SSL connection, however, the bucket contains periods and \
                            the wildcard certificate will not match by default. Please consider using HTTP.")

        path = calling_format.get_url(self.is_secure, self.server, self.port, bucket, key, None)
        connect_server = calling_format.get_server(self.server, bucket)
        head = self.add_headers(headers, "")
        header_config = self.add_auth_headers(head, method, bucket, key, None)
        header_config["Content-Length"] = str(len(data))
        return self.send_request(connect_server, method, path, header_config)

    def create_object2(self, bucket, key, data, headers=None):
        conn = self.make_request2("PUT", bucket, Utils.urlencode(key), data, headers)
        conn.send(data)
        return conn.getresponse()


def hws_upload(filename, data):
    s3 = MyHuaweiS3(hws_AK, hws_SK, is_secure=hws_ssl, server=hws_server)
    if debug:
        print 'Putting "%s" to bucket "%s"' % (filename, hws_bucket_name)
    result = s3.create_object2(hws_bucket_name, filename, data, headers=hws_headers)
    if debug:
        print result.status, result.reason
    url = s3.get_object_url(hws_bucket_name, filename)
    if debug:
        print 'URL: %s' % url
    return url


class Upload:
    """
    上传文件

    使用POST method
    POST数据为: 文件名 + '\r\n' + 文件内容 + '\r\n'

    正常情况下返回返回status code "200 OK"
    结果格式如下:
    {"result":"success","url":"xxx"}
    """

    def __init__(self):
        pass

    def POST(self):
        web.header('Content-Type', 'text/json')

        body = web.data()
        if body is None:
            set_status_code(web, 400)
            return result_template('empty body')
        split = body.find('\r\n')
        end = body.rfind('\r\n')
        if split == -1 or end == -1 or split == end:
            set_status_code(web, 400)
            return result_template('invalid body')

        filename = body[0:split]
        data = body[split + 2:end]
        try:
            url = hws_upload(filename, data)
            return url_template(url)
        except Exception, e:
            set_status_code(web, 500)
            return exception_template(e)


class UploadFile:
    def __init__(self):
        pass

    def GET(self):
        return '''<html>
<head>
<title>Upload File</title>
</head>
<body>
<form method="POST" enctype="multipart/form-data" action="">
<input type="file" name="myfile"/><br/>
<input type="submit"/>
</form>
</body>
</html>'''

    def POST(self):
        x = web.input(myfile={})
        filename = x['myfile'].filename
        data = x['myfile'].value
        try:
            url = hws_upload(filename, data)
            return url_template(url)
        except Exception, e:
            web.debug(str(e))
            set_status_code(web, 500)
            return exception_template(e)


if __name__ == '__main__':
    initialize_bucket()
    urls = (
        '/upload_file', 'UploadFile',
        '/upload', 'Upload',
    )
    app = web.application(urls, globals())
    app.run()
