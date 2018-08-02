#!/usr/bin/env python

from __future__ import print_function

try:
    import httplib
    import urlparse
except ImportError:
    import http.client as httplib
    import urllib.parse as urlparse
import os
import random
import socket
import subprocess
import unittest
import urllib
import ssl

import yaml

def rand_num():
    return random.randint(1000, 10000)


def do_get(url):
    parsed = urlparse.urlparse(url)
    path = parsed.path
    if parsed.query:
        path = '%s?%s' % (path, parsed.query)
    if parsed.scheme == 'http':
        conn = httplib.HTTPConnection(TARGET_IP)
    elif parsed.scheme == 'https':
        conn = httplib.HTTPSConnection(TARGET_IP, timeout=8, context=ssl._create_unverified_context())
    conn.request('GET', path, headers={'Host': parsed.netloc})
    resp = conn.getresponse()
    body = resp.read().decode('utf8')
    resp.close()
    conn.close()
    return resp, body


class RedirTest(unittest.TestCase):
    def assert_code(self, url, expected_code):
        print('GET: %s => %s' % (url, expected_code))
        resp, body = do_get(url)
        self.assertEqual(resp.status, expected_code)

    def assert_scheme_redirect(self, url, expected_loc, expected_code, **kwargs):
        for k, v in kwargs.items():
            k = '$%s' % k
            v = '%s' % v
            url = url.replace(k, v)
            expected_loc = expected_loc.replace(k, v)
        print('REDIR: %s => %s' % (url, expected_loc))
        resp, body = do_get(url)
        self.assertEqual(resp.status, expected_code)
        self.assertEqual(resp.getheader('location'), expected_loc)

    def assert_redirect(self, url, expected_loc, expected_code, **kwargs):
        self.assert_scheme_redirect(
            url, expected_loc, expected_code, **kwargs)

class ContentTest(unittest.TestCase):
    def assert_body_url(self, url, expected_content_url):
        print('GET', url)
        resp, body = do_get(url)
        self.assertEqual(resp.status, 200)
        expected_body = urllib.urlopen(expected_content_url).read()
        self.assertMultiLineEqual(body, expected_body)

if __name__ == '__main__':
    TARGET_IP = os.environ.get('TARGET_IP')
    if not TARGET_IP:
        print('Attempting to autodiscover service TARGET_IP, set env var to override...')
        TARGET_IP = socket.gethostbyname('istio.io')
        print('Testing against service at', TARGET_IP)
    unittest.main()
