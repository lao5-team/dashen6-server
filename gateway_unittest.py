#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# author: yafei
# HTTP Gateway unit test
import unittest
from gateway import app


class GateWayTest(unittest.TestCase):
    def test_login_not_login(self):
        response = app.request('/login', method='GET')
        self.assertIn('Not login', response.data)
        self.assertEquals(response.status, '401 Unauthorized')

    def test_login_login(self):
        response = app.request('/login?user=123', method='GET')
        self.assertIn('Login OK', response.data)
        self.assertEquals(response.status, '200 OK')
        self.assertEquals(response.header_items[1][0], 'Set-Cookie')
        self.assertEquals(response.header_items[2][0], 'Set-Cookie')

    def test_login_already_login(self):
        response = app.request(
            '/login?user=123',
            method='GET',
            headers={
                'Cookie': 'user=test; token=9527'
            }
        )
        self.assertIn('Already login', response.data)
        self.assertEquals(response.status, '200 OK')


if __name__ == '__main__':
    unittest.main()
