#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# author: yafei
# print field from json result

import json
import sys


CHARSET_LIST = ['utf-8', 'gb18030']


def main():
    json_str = ''
    while 1:
        line = sys.stdin.readline()
        if not line:
            break
        json_str = json_str + line


    # check UTF-8 BOM header
    if json_str.startswith('\xef\xbb\xbf'):
        json_str = json_str[3:]
    # check UCS-2 BE BOM header
    elif json_str.startswith('\xfe\xff'):
        json_str = json_str[2:]
        json_str = json_str.decode('utf-16-be')
    # check UCS-2 LE BOM header
    elif json_str.startswith('\xff\xfe'):
        json_str = json_str[2:]
        json_str = json_str.decode('utf-16-le')
    else:
        charset = None
        for cs in CHARSET_LIST:
            try:
                json_str.decode(cs)
                charset = cs
                break
            except:
                pass
        if charset is None:
            print >> sys.stderr, 'this json string can\'t be parsed for encoding reasons'
            sys.exit(1)
        json_str = json_str.decode(charset)

    obj = json.loads(json_str)

    if len(sys.argv) == 1:
        json_str = json.dumps(obj, indent=4, ensure_ascii=False, sort_keys=False)
    else:
        for arg in sys.argv[1:]:
            o = obj.get(arg)
            if o is None:
                print >> sys.stderr, '''couldn't find field %s''' % arg
            else:
                json_str = str(o)

    out_encoding = sys.stdout.encoding
    if out_encoding is None:
        out_encoding = 'utf-8'
    json_str = json_str.encode(out_encoding)
    sys.stdout.write(json_str)
    sys.stdout.flush()


if __name__ == '__main__':
    main()
