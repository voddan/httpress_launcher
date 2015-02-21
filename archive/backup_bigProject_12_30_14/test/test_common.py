#!/usr/bin/python
# coding=utf-8
# test_common
#
__author__ = 'voddan'
__package__ = None
__project_root__ = '/home/voddan/Program/Parallels/httpress_launcher/'
# TODO: do not use a constant
# TODO: test it somewhere

import unittest
import logging
import helper
import StringIO

from src.hostline import parse_host_lines
from src.common import GlobalEnvironment
from src.common import Environment
from src.common import load_host_lines_from_single_file
from src.common import Comparable

class Test_Comparable(unittest.TestCase):
    def test_sample_class(self):
        class TestComparable(Comparable):
            def __eq__(self, other):
                return other == 0

        obj = TestComparable()
        self.assertTrue(obj.__eq__(0))
        self.assertFalse(obj.__eq__(1))

        self.assertTrue(obj.__ne__(1))
        self.assertFalse(obj.__ne__(0))

        self.assertTrue(obj == 0)
        self.assertFalse(obj == 1)

        self.assertTrue(obj != 1)
        self.assertFalse(obj != 0)


class Test_Environment(unittest.TestCase):
    def test_SHHKEY_repr(self):
        obj = Environment.SHHKEY()
        self.assertEqual(str(obj), 'SHHKEY')

    def test_SHHKEY_eq(self):
        self.assertEqual(Environment.SHHKEY(), Environment.SHHKEY())

    # TODO: add logging to unit-tests after implementing
    def test_init(self):
        stream = StringIO.StringIO()
        obj = Environment(httpress_bin_path='bin_path',
                          version='0.0.1',
                          default_user='me',
                          default_password='123456',
                          logger=logging.getLogger(),
                          text_stream=stream)

        self.assertEqual(obj.httpress_bin_path, 'bin_path')
        self.assertEqual(obj.version, '0.0.1')
        self.assertEqual(obj.default_user, 'me')
        self.assertEqual(obj.default_password, '123456')
        self.assertEqual(obj._logger, logging.getLogger())
        self.assertEqual(obj.text_stream, stream)



env = helper.TestingEnvironment('../bin/httpress_mock.py')

class Test_load_host_lines_from_file(unittest.TestCase):
    def test_simple_running(self):
        filename = __project_root__ + 'bin/hostlist/simple.hostlist'
        host_list = load_host_lines_from_single_file(filename)
        self.assertGreaterEqual(len(host_list), 9)

    def test_running_with_parsing(self):
        filename = __project_root__ + 'bin/hostlist/simple.hostlist'
        host_lines = [
            'localhost',
            'en.wikipedia.org',
            'my_user@en.wikipedia.org',
            'some_password:en.wikipedia.org',
            'my_user@some_password:en.wikipedia.org',
            '198.35.26.96',
            'my_user@198.35.26.96',
            'some_password:198.35.26.96',
            'my_user@some_password:198.35.26.96',
        ]
        host_list = load_host_lines_from_single_file(filename)
        self.assertEqual(parse_host_lines(env, host_list),
                         parse_host_lines(env, host_lines))

    def test_single_with_parsing(self):
        filename = __project_root__ + 'bin/hostlist/single.hostlist'
        host_lines = ['myuser@mypass:mylocalhost']
        host_list = load_host_lines_from_single_file(filename)
        self.assertEqual(parse_host_lines(env, host_list),
                         parse_host_lines(env, host_lines))

    def test_empty_file_with_parsing(self):
        filename = __project_root__ + 'bin/hostlist/empty.hostlist'
        host_list = load_host_lines_from_single_file(filename)
        self.assertEqual(parse_host_lines(env, host_list),
                         parse_host_lines(env, []))

    def test_syntax_errors_with_parsing(self):
        filename = __project_root__ + 'bin/hostlist/errors.hostlist'
        host_lines = [
            'localhost',
            'en.wikipedia.org',
            'my_user@en.wikipedia.org',
            'some_password:en.wikipedia.org',
            'my_user@some_password:en.wikipedia.org',
            '198.35.26.96',
            'my_user@198.35.26.96',
            'some_password:198.35.26.96',
            'my_user@some_password:198.35.26.96',
        ]
        host_list = load_host_lines_from_single_file(filename)
        self.assertEqual(parse_host_lines(env, host_list),
                         parse_host_lines(env, host_lines))


#========================
if __name__ == '__main__':  # pragma: no cover
    unittest.main(exit=False, failfast=False)
