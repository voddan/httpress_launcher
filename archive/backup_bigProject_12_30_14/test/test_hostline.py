#!/usr/bin/python
# coding=utf-8
# test_common
#
__author__ = 'voddan'
__package__ = None

import unittest
import logging
import helper

from src.common import Environment
from src.hostline import Host
from src.hostline import LocalHost
from src.hostline import parse_host_lines


env = helper.TestingEnvironment('../bin/httpress_mock.py',
                                logger_level=logging.DEBUG)


class Test_Host(unittest.TestCase):
    def test_init(self):
        obj = Host('user', 'pass', '127.0.0.1')
        self.assertEqual(obj.login, 'user')
        self.assertEqual(obj.password, 'pass')
        self.assertEqual(obj.hostname, '127.0.0.1')

    def test_init_SHHKEY(self):
        obj = Host('user', Environment.SHHKEY(), '127.0.0.1')
        self.assertEqual(obj.login, 'user')
        self.assertEqual(obj.password, Environment.SHHKEY())
        self.assertEqual(obj.hostname, '127.0.0.1')

    def test_eq(self):
        self.assertEqual(Host('user', 'pass', '127.0.0.1'),
                         Host('user', 'pass', '127.0.0.1'))

        self.assertEqual(Host('user', Environment.SHHKEY(), '127.0.0.1'),
                         Host('user', Environment.SHHKEY(), '127.0.0.1'))

        self.assertNotEqual(Host('user1', 'pass', '127.0.0.1'),
                            Host('user2', 'pass', '127.0.0.1'))

        self.assertNotEqual(Host('user', 'pass1', '127.0.0.1'),
                            Host('user', 'pass2', '127.0.0.1'))

        self.assertNotEqual(Host('user', 'pass', '127.0.1.1'),
                            Host('user', 'pass', '127.0.2.1'))

        self.assertNotEqual(Host('user', 'pass', '127.0.0.1'),
                            Host('user', Environment.SHHKEY(), '127.0.0.1'))

    def test_repr(self):
        self.assertRegexpMatches(str(Host('me', '123', 'test.host')),
                                 r'Host.*me.*123.*test\.host.*')


class Test_LocalHost(unittest.TestCase):
    def test_init(self):
        obj = LocalHost()
        # in order to support '__eq__(Host(..), LocalHost()) == False'
        self.assertIsNot(obj.login, str)
        self.assertIsNot(obj.password, str)
        self.assertEqual(obj.hostname, 'localhost')

    def test_eq(self):
        self.assertEqual(LocalHost(), LocalHost())
        self.assertNotEqual(LocalHost(), Host('', '', 'localhost'))
        self.assertNotEqual(Host('', '', 'localhost'), LocalHost())

    def test_repr(self):
        self.assertRegexpMatches(str(LocalHost()),
                                 r'.*(localhost|Localhost|LocalHost).*')


class Test_parseHostLines(unittest.TestCase):
    def test_running(self):
        host_lines = [
            'localhost',
            'Localhost',
            'LocalHost',
            'loCAlhoST',

            'en.wikipedia.org',
            'my_user@en.wikipedia.org',
            'some_password:en.wikipedia.org',
            'my_user@some_password:en.wikipedia.org',

            '198.35.26.96',
            'my_user@198.35.26.96',
            'some_password:198.35.26.96',
            'my_user@some_password:198.35.26.96',
        ]

        hosts = [
            LocalHost(),
            LocalHost(),
            LocalHost(),
            LocalHost(),

            Host('root', Environment.SHHKEY(), 'en.wikipedia.org'),
            Host('my_user', Environment.SHHKEY(), 'en.wikipedia.org'),
            Host('root', 'some_password', 'en.wikipedia.org'),
            Host('my_user', 'some_password', 'en.wikipedia.org'),

            Host('root', Environment.SHHKEY(), '198.35.26.96'),
            Host('my_user', Environment.SHHKEY(), '198.35.26.96'),
            Host('root', 'some_password', '198.35.26.96'),
            Host('my_user', 'some_password', '198.35.26.96'),
        ]

        get_hosts = parse_host_lines(env, host_lines)
        self.assertEqual(get_hosts, hosts)

    def test_syntax_errors(self):
        host_lines = [
            ':localhost',
            ':localhost',
            'localhost:',
            'localhost@',

            'en.wikipedia.org:',
            'en.wikipedia.org@',
            '@en.wikipedia.org',
            ':en.wikipedia.org',
            '@:en.wikipedia.org',

            '198.35.26.96:',
            '198.35.26.96@',
            '@198.35.26.96',
            ':198.35.26.96',
            '@:198.35.26.96',
        ]
        self.assertEqual(parse_host_lines(env, host_lines), [])

    def test_permitted_symbols_in_password(self):
        # password_characters = r'[\w!\)\(-.?\]\[`~]'
        host_lines = [
            'pass#word:hostname'
            'pass$word:hostname'
            'pass%word:hostname'
            'pass^word:hostname'
            'pass&word:hostname'
            'pass*word:hostname'
            'pass+word:hostname'
            'pass{word:hostname'
            'pass}word:hostname'
            'pass\'word:hostname'
            'pass\"word:hostname'
            'pass/word:hostname'
            'pass|word:hostname'
            'pass\\word:hostname'
            'pass\\word:hostname'
            'pass>word:hostname'
            'pass<word:hostname'
            'pass,word:hostname'
        ]
        self.assertEqual(parse_host_lines(env, host_lines), [])

    def test_running_permitted_symbols_in_hostname(self):
        # hostname_characters = r'[a-zA-Z0-9_-]'
        host_lines = [
            'en.wikipe`dia.org',
            'en.wikipe~dia.org',
            'en.wikipe!dia.org',
            'en.wikipe#dia.org',
            'en.wikipe$dia.org',
            'en.wikipe%dia.org',
            'en.wikipe^dia.org',
            'en.wikipe&dia.org',
            'en.wikipe*dia.org',
            'en.wikipe(dia.org',
            'en.wikipe)dia.org',
            'en.wikipe+dia.org',
            'en.wikipe=dia.org',
            'en.wikipe[dia.org',
            'en.wikipe]dia.org',
            'en.wikipe{dia.org',
            'en.wikipe}dia.org',
            'en.wikipe\'dia.org',
            'en.wikipe\"dia.org',
            'en.wikipe?dia.org',
            'en.wikipe/dia.org',
            'en.wikipe<dia.org',
            'en.wikipe>dia.org',
            'en.wikipe,dia.org',
        ]
        self.assertEqual(parse_host_lines(env, host_lines), [])

    def test_running_permitted_symbols_in_login(self):
        host_lines = [
            'my`user@hostname',
            'my~user@hostname',
            'my!user@hostname',
            'my#user@hostname',
            'my$user@hostname',
            'my%user@hostname',
            'my^user@hostname',
            'my&user@hostname',
            'my*user@hostname',
            'my(user@hostname',
            'my)user@hostname',
            'my+user@hostname',
            'my=user@hostname',
            'my[user@hostname',
            'my]user@hostname',
            'my{user@hostname',
            'my}user@hostname',
            'my\'user@hostname',
            'my\"user@hostname',
            'my?user@hostname',
            'my/user@hostname',
            'my<user@hostname',
            'my>user@hostname',
            'my,user@hostname',
            'my.user@hostname',
        ]
        self.assertEqual(parse_host_lines(env, host_lines), [])

    def test_localhost(self):
        # env_local = helper.TestingEnvironment()
        result = parse_host_lines(env, ['user@localhost'])
        (output, stderr) = env.get_output()
        self.assertEqual(result, [LocalHost()])
        # tried to describe the message as general as possible
        self.assertRegexpMatches(stderr, r'.*((ignored.*localhost)|(localhost.*ignored)).*')


#========================
if __name__ == '__main__':  # pragma: no cover
    unittest.main(exit=False, failfast=False)