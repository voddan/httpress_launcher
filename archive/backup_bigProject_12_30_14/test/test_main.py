#!/usr/bin/python
# coding=utf-8
# test_main
#
__author__ = 'voddan'
__package__ = None

import unittest
import helper
import logging
import sys

from src.main import main
from src.main import main_launcher

from src.main import environment
from test.helper import TestingEnvironment

class Test_main(unittest.TestCase):
    def test_empty_comline(self):
        env = helper.TestingEnvironment('../bin/httpress_mock.py')
        env.clean_output()

        self.assertRaises(SystemExit, main, env, [])

        (out, err) = env.get_output()
        self.assertRegexpMatches(err.lower(), '.*command line.*')

    def test_only_bin(self):
        env = helper.TestingEnvironment('../bin/httpress_mock.py')
        env.clean_output()
        res = main(env, r'-n 100 -c 10 http://www.yandex.ru/'.split(' '))
        (out, err) = env.get_output()
        self.assertIsNone(res)
        self.assertEqual(err, '')

    def test_combined_help(self):
        env = helper.TestingEnvironment('../bin/httpress_mock.py')
        env.clean_output()

        res = None
        try:
            res = main(env, ['--help'])
        except SystemExit:
            pass

        (out, err) = env.get_output()
        self.assertIsNone(res)
        self.assertEqual(err, '')
        self.assertRegexpMatches(out, r'.{10,}======.{10,}')

    def test_bin_help(self):
        env = helper.TestingEnvironment('../bin/httpress_mock.py')
        env.clean_output()

        res = None
        try:
            res = main(env, ['-h'])
        except SystemExit:
            pass

        (out, err) = env.get_output()
        self.assertIsNone(res)
        self.assertEqual(err, '')
        self.assertNotRegexpMatches(out, r'.{10,}======.{10,}')

    def test_simple_hostlist(self):
        env = helper.TestingEnvironment('../bin/httpress_mock.py')
        env.clean_output()
        res = main(env, ' -n 100 -c 10 http://www.yandex.ru/ '
                        '--hosts localhost --file ../bin/hostlist/simple.hostlist'.split(' '))
        (out, err) = env.get_output()

        self.assertIsNone(res)
        self.assertEqual(err, '')

        # very specific test because of bugs in 're.match'
        self.assertRegexpMatches(out, r'.*'
                                      r'=+\s*life\s*=+[^=]*'
                                      r'=+\s*1\s*=+[^=]*'
                                      r'=+\s*2\s*=+[^=]*'
                                      r'=+\s*3\s*=+[^=]*'
                                      r'=+\s*4\s*=+[^=]*'
                                      r'=+\s*5\s*=+[^=]*'
                                      r'=+\s*6\s*=+[^=]*'
                                      r'=+\s*7\s*=+[^=]*'
                                      r'=+\s*8\s*=+[^=]*'
                                      r'=+\s*9\s*=+[^=]*'
                                      r'.*'
                                      r'=+\s*FAILED:\s*0\s*=+\s'
                                      r'={2,}'
                                      r'.*')

    # TODO: output is leaking
    def test_two_files(self):
        env = helper.TestingEnvironment('../bin/httpress_mock.py')
        env.clean_output()
        res = main(env, r'-n 100 -f ../bin/hostlist/single.hostlist '
                   r'-c 10 http://www.yandex.ru/ '
                   r'--file ../bin/hostlist/simple.hostlist -v'.split(' '))
        (out, err) = env.get_output()

        self.assertIsNone(res)
        self.assertRegexpMatches(err, r'.*WARNING.*Content is taken from all sources.*')


@unittest.skipUnless(isinstance(environment, TestingEnvironment),
                     "in the 'main' module the default environment is not TestingEnvironment")
class Test_main_launcher(unittest.TestCase):
    # TODO: output is leaking
    def test_empty_comline(self):
        (res, out, err, exc) = helper.test_procedure(main_launcher, [])
        self.assertIsNone(res)
        self.assertEqual(err, '')
        self.assertIsInstance(exc, SystemExit)

    # TODO: output is leaking
    def test_only_bin(self):
        (res, out, err, exc) = helper.test_procedure(main_launcher,
                                                     r'-n 100 -c 10 http://www.yandex.ru/'.split(' '))
        self.assertIsNone(res)
        self.assertEqual(err, '')
        self.assertIsNone(exc)

    @unittest.skip("interception of stdout or environment.text(stdout) doesn't work for some reason")
    def test_simple_hostlist(self):
        # (out, err, res) = helper.capture_output(main_launcher,
        #                                              r'-n 100 -c 10 http://www.yandex.ru/ '
        #                                              r'--hosts localhost'.split(' '))

        with helper.Capturing() as output:
            res = main_launcher(r'-n 100 -c 10 http://www.yandex.ru/ --hosts localhost'.split(' '))

        out = ' '.join(output.stdout)
        err = ' '.join(output.stderr)

        self.assertIsNone(res)
        self.assertEqual(err, '')

        print '+++++++++++'
        print res
        print out
        print err
        self.assertRegexpMatches(out, r'.*'
                                      # r'=+\s*1\s*=+[^=]*'
                                      # r'=+\s*FAILED:\s*0\s*=+\s'
                                      r'={5,}'
                                      r'.*')

# ========================
if __name__ == '__main__':  # pragma: no cover
    unittest.main(exit=False, failfast=False)
