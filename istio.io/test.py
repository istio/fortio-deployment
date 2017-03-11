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
        # Vanity domains.
        for url in ('istio.io', 'kubernet.es'):
            self.assert_perm_redirect(url + path, 'https://istio.io' + path)

    def test_go_get(self):
        self.assert_perm_redirect('istio.io/istio?go-get=1',
                'https://istio.io/istio?go-get=1')
        self.assert_code('https://istio.io/istio?go-get=1', 200)

    def test_go(self):
        for base in ('go.istio.io/', 'go.istio.io/'):
            self.assert_temp_redirect(base + 'bounty',
                'https://github.com/istio/istio.github.io/'
                'issues?q=is%3Aopen+is%3Aissue+label%3ABounty')
            self.assert_temp_redirect(base + 'help-wanted',
                'https://github.com/istio/istio/labels/help-wanted')
            self.assert_temp_redirect(
                base + 'oncall',
                'https://storage.googleapis.com/istio-jenkins/oncall.html')
            self.assert_temp_redirect(
                base + 'partner-request',
                'https://docs.google.com/forms/d/e/1FAIpQLSdN1KtSKX2VAOPGABFlShkSd6CajQynoL4QCVtY0dj76MNDKg/viewform')
            self.assert_temp_redirect(base + 'start',
                'http://istio.io/docs/getting-started-guides/')
            self.assert_temp_redirect(
                base + 'test-history',
                'https://storage.googleapis.com/istio-test-history/static/index.html')
            self.assert_temp_redirect(
                base + 'triage',
                'https://storage.googleapis.com/istio-gubernator/triage/index.html')

    def test_yum_test(self):
        for base in ('yum.istio.io', 'yum.istio.io'):
            self.assert_temp_redirect(base, 'https://packages.cloud.google.com/yum/')
            self.assert_temp_redirect(base + '/$id',
                'https://packages.cloud.google.com/yum/$id', id=rand_num())

    def test_apt_test(self):
        for base in ('apt.istio.io', 'apt.istio.io'):
            self.assert_temp_redirect(base, 'https://packages.cloud.google.com/apt/')
            self.assert_temp_redirect(base + '/$id',
                'https://packages.cloud.google.com/apt/$id', id=rand_num())

    def test_ci_test(self):
        base = 'ci-test.istio.io'
        self.assert_temp_redirect(base, 'https://console.developers.google.com/storage/browser/istio-jenkins/logs')

        # trailing slash
        self.assert_temp_redirect(base + '/',
            'https://console.developers.google.com/storage/browser/istio-jenkins/logs')

        # trailing slash
        self.assert_temp_redirect(base + '/e2e/',
            'https://console.developers.google.com/storage/browser/istio-jenkins/logs/e2e')

        num = rand_num()
        # numeric with trailing slash
        self.assert_temp_redirect(base + '/e2e/$num/',
            'https://istio-gubernator.appspot.com/build/istio-jenkins/logs/e2e/$num',
            num=num)
        # numeric without trailing slash
        self.assert_temp_redirect(base + '/e2e/$num',
            'https://istio-gubernator.appspot.com/build/istio-jenkins/logs/e2e/$num',
            num=num)

        # no trailing slash
        self.assert_temp_redirect(base + '/e2e/$num/file',
            'https://storage.cloud.google.com/istio-jenkins/logs/e2e/$num/file',
            num=num)

    def test_code(self):
        path = rand_num()
        for base in ('changelog.istio.io', 'changelog.istio.io'):
            self.assert_temp_redirect(base + '/$path',
                'https://github.com/istio/istio/releases/tag/$path',
                path=path)
        for base in ('code.istio.io', 'code.istio.io'):
            self.assert_temp_redirect(base + '/$path',
                'https://github.com/istio/istio/tree/master/$path',
                path=path)

    def test_dl(self):
        for base in ('dl.istio.io', 'dl.istio.io'):
            # Valid release version numbers
            for extra in ('', '-alpha.$rc_ver', '-beta.$rc_ver'):
                self.assert_temp_redirect(
                    base + '/v$major_ver.$minor_ver.$patch_ver' + extra + '/$path',
                    'https://storage.googleapis.com/istio-release/release/v$major_ver.$minor_ver.$patch_ver' + extra + '/$path',
                    major_ver=rand_num(), minor_ver=rand_num(), patch_ver=rand_num(), rc_ver=rand_num(), path=rand_num())
            # Not a release version
            self.assert_temp_redirect(
                base + '/v8/engine',
                'https://storage.googleapis.com/istio-release/v8/engine')
            # Not a valid release version (gamma)
            self.assert_temp_redirect(
                base + '/v1.2.3-gamma.4/istio.tar.gz',
                'https://storage.googleapis.com/istio-release/v1.2.3-gamma.4/istio.tar.gz')
            # A few /ci/ tests
            self.assert_temp_redirect(
                base + '/ci/v$ver/$path',
                'https://storage.googleapis.com/istio-release-dev/ci/v$ver/$path',
                ver=rand_num(), path=rand_num())
            self.assert_temp_redirect(
                base + '/ci/latest-$ver.txt',
                'https://storage.googleapis.com/istio-release-dev/ci/latest-$ver.txt',
                ver=rand_num())
            self.assert_temp_redirect(
                base + '/ci-cross/v$ver/$path',
                'https://storage.googleapis.com/istio-release-dev/ci-cross/v$ver/$path',
                ver=rand_num(), path=rand_num())
            # Base case
            self.assert_temp_redirect(
                base + '/$path',
                'https://storage.googleapis.com/istio-release/$path',
                path=rand_num())

    def test_docs(self):
        for base in ('docs.istio.io', 'docs.istio.io'):
            self.assert_temp_redirect(base, 'http://istio.io/docs/')
            ver = '%d.%d' % (rand_num(), rand_num())
            self.assert_temp_redirect(base + '/v$ver', 'http://istio.io/docs', ver=ver)
            path = rand_num()
            self.assert_temp_redirect(base + '/v$ver/$path', 'http://istio.io/docs/$path', ver=ver, path=path)
            self.assert_temp_redirect(base + '/$path', 'http://istio.io/docs/$path', path=path)

    def test_examples(self):
        for base in ('examples.istio.io', 'examples.istio.io'):
            self.assert_temp_redirect(base, 'https://github.com/istio/istio/tree/master/examples/')

            ver = '%d.%d' % (rand_num(), rand_num())
            self.assert_temp_redirect(base + '/v$ver',
                'https://github.com/istio/istio/tree/release-$ver/examples',
                ver=ver)
            self.assert_temp_redirect(base + '/v$ver/$path',
                'https://github.com/istio/istio/tree/release-$ver/examples/$path',
                ver=ver, path=rand_num())

    def test_features(self):
        for base in ('features.istio.io', 'feature.istio.io',
                     'features.istio.io', 'feature.istio.io'):
            self.assert_temp_redirect(base,
                'https://github.com/istio/features/issues/',
                path=rand_num())
            self.assert_temp_redirect(base + '/$path',
                'https://github.com/istio/features/issues/$path',
                path=rand_num())

    def test_issues(self):
        for base in ('issues.istio.io', 'issue.istio.io',
                     'issues.istio.io', 'issue.istio.io'):
            self.assert_temp_redirect(base + '/$path',
                'https://github.com/istio/istio/issues/$path',
                path=rand_num())

    def test_prs(self):
        for base in ('prs.istio.io', 'pr.istio.io',
                     'prs.istio.io', 'pr.istio.io'):
            self.assert_temp_redirect(base, 'https://github.com/istio/istio/pulls')
            self.assert_temp_redirect(base + '/$path',
                'https://github.com/istio/istio/pull/$path',
                path=rand_num())

    def test_pr_test(self):
        base = 'pr-test.istio.io'
        self.assert_temp_redirect(base, 'https://istio-gubernator.appspot.com')
        self.assert_temp_redirect(base + '/$id',
            'https://istio-gubernator.appspot.com/pr/$id', id=rand_num())

    def test_release(self):
        for base in ('releases.istio.io', 'rel.istio.io',
                     'releases.istio.io', 'rel.istio.io'):
            self.assert_temp_redirect(base, 'https://github.com/istio/istio/releases')
            self.assert_temp_redirect(base + '/$ver/$path',
                'https://github.com/istio/istio/tree/$ver/$path',
                ver=rand_num(), path=rand_num())

    def test_reviewable(self):
        base = 'reviewable.istio.io'
        self.assert_temp_redirect(base, 'https://reviewable.istio.io/')
        self.assert_temp_redirect(base + '/$path', 'https://reviewable.istio.io/$path',
            path=rand_num())

    def test_testgrid(self):
        for base in ('testgrid.istio.io', 'testgrid.istio.io'):
            self.assert_temp_redirect(base, 'https://istio-testgrid.appspot.com/')
            self.assert_temp_redirect(base + '/$path', 'https://istio-testgrid.appspot.com/$path',
                path=rand_num())


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
        for pkg in ('istio', 'heapster', 'kube-ui'):
            self.assert_body_configmap('%s/%s/%s' % (base, pkg, suff),
                'golang/%s.html' % pkg)
        resp, body = do_get(base + '/foobar/123?go-get=1')
        self.assertEqual(resp.status, 404)

    def test_get(self):
        for base in ('http://get.istio.io', 'http://get.istio.io'):
            self.assert_body_configmap(base, 'get/get-kube-insecure.sh')

        for base in ('https://get.istio.io', 'https://get.istio.io'):
          self.assert_body_url(
              base,
              'https://raw.githubusercontent.com/istio/istio/master/cluster/get-kube.sh')


if __name__ == '__main__':
    TARGET_IP = os.environ.get('TARGET_IP')
    if not TARGET_IP:
        print('Attempting to autodiscover service TARGET_IP, set env var to override...')
        TARGET_IP = socket.gethostbyname('istio.io')
        print('Testing against service at', TARGET_IP)
    unittest.main()
