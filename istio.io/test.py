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
        conn = httplib.HTTPSConnection(TARGET_IP)
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

    def assert_redirect(self, partial_url, expected_loc, expected_code, **kwargs):
        for scheme in ('http', 'https'):
            self.assert_scheme_redirect(
                    scheme + '://' + partial_url, expected_loc, expected_code, **kwargs)

    def assert_temp_redirect(self, partial_url, expected_loc, **kwargs):
        self.assert_redirect(partial_url, expected_loc, 302, **kwargs)

    def assert_perm_redirect(self, partial_url, expected_loc, **kwargs):
        self.assert_redirect(partial_url, expected_loc, 301, **kwargs)

    def test_main(self):
        # Main URL.
        self.assert_code('https://istio.io', 200)
        # Protocol upgrade.
        self.assert_scheme_redirect(
                'http://istio.io', 'https://istio.io/', 301)
        path = '/%s' % rand_num()
        # Protocol upgrade and path.
        self.assert_scheme_redirect(
                'http://istio.io' + path, 'https://istio.io' + path, 301)

    def test_go_get(self):
        self.assert_perm_redirect('istio.io/istio?go-get=1',
                'https://istio.io/istio?go-get=1')
        self.assert_code('https://istio.io/istio?go-get=1', 200)


class ContentTest(unittest.TestCase):
    def assert_body_configmap(self, url, filename):
        print('GET', url)
        resp, body = do_get(url)
        self.assertEqual(resp.status, 200)
        configmap = 'configmap-www-%s.yaml' % os.path.dirname(filename)
        with open(configmap) as f:
            expected_body = yaml.load(f)['data'][os.path.basename(filename)]
        self.assertMultiLineEqual(body, expected_body)

    def assert_body_url(self, url, expected_content_url):
        print('GET', url)
        resp, body = do_get(url)
        self.assertEqual(resp.status, 200)
        expected_body = urllib.urlopen(expected_content_url).read()
        self.assertMultiLineEqual(body, expected_body)

    def test_go_get(self):
        base = 'https://istio.io' # because everything ends up there
        suff = '%d?go-get=1' % rand_num()
        for pkg in ('manager', 'mixer', 'proxy'):
            self.assert_body_configmap('%s/%s/%s' % (base, pkg, suff),
                'golang/%s.html' % pkg)
        resp, body = do_get(base + '/foobar/123?go-get=1')
        self.assertEqual(resp.status, 404)


if __name__ == '__main__':
    TARGET_IP = os.environ.get('TARGET_IP')
    if not TARGET_IP:
        print('Attempting to autodiscover service TARGET_IP, set env var to override...')
        TARGET_IP = socket.gethostbyname('istio.io')
        print('Testing against service at', TARGET_IP)
    unittest.main()
