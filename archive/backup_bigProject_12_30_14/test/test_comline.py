#!/usr/bin/python
# coding=utf-8
# test_argparse_parse_args
#
__author__ = 'voddan'
__package__ = None

import unittest
import re
import helper
import os

from src.comline import argparse_parse_args
from src.comline import httpress_get_help_msg
from src.comline import HttpressComLine


env = helper.TestingEnvironment('../bin/httpress_mock.py')

httpress_help_msg_stripped = httpress_get_help_msg(env).strip()


class Test_HttpressComLine(unittest.TestCase):
    def test_init(self):
        obj = HttpressComLine(['localhost'], ['./test', 'folder'], ['http://yandex.ru', '-c', '100'])
        self.assertEqual(obj.host_line_list, ['localhost'])
        self.assertEqual(obj.filename_list, ['./test', 'folder'])
        self.assertEqual(obj.parameters_to_pass, ['http://yandex.ru', '-c', '100'])

    def test_eq(self):
        self.assertEqual(HttpressComLine([], [], []),
                         HttpressComLine([], [], []))

        self.assertEqual(HttpressComLine(['localhost'], ['./test', 'folder'], ['http://yandex.ru', '-c', '100']),
                         HttpressComLine(['localhost'], ['./test', 'folder'], ['http://yandex.ru', '-c', '100']))

        self.assertEqual(HttpressComLine(['localhost'], [], ['http://yandex.ru', '-c', '100']),
                         HttpressComLine(['localhost'], [], ['http://yandex.ru', '-c', '100']))

        self.assertNotEqual(HttpressComLine(['localhost1'], ['./test'], ['http://yandex.ru', '-c', '100']),
                            HttpressComLine(['localhost2'], ['./test'], ['http://yandex.ru', '-c', '100']))

        self.assertNotEqual(HttpressComLine(['localhost'], ['./test1'], ['http://yandex.ru', '-c', '100']),
                            HttpressComLine(['localhost'], ['./test2'], ['http://yandex.ru', '-c', '100']))

        self.assertNotEqual(HttpressComLine(['localhost'], ['./test'], ['http://yandex.ru', '-c', '101']),
                            HttpressComLine(['localhost'], ['./test'], ['http://yandex.ru', '-c', '102']))

        self.assertNotEqual(HttpressComLine(['localhost'], ['./test'], ['http://yandex.ru', '-c', '100']),
                            HttpressComLine(['localhost'], ['./test'], ['http://yandex.ru', '100', '-c']))

    def test_repr(self):
        self.assertRegexpMatches(str(HttpressComLine(['localhost'], ['./test', 'folder'],
                                                     ['http://yandex.ru', '-c', '100'])),
                                 r'.*localhost.*\./test.*folder.*http://yandex\.ru.*-c.*100.*')


class Test_argparseParseArgs(unittest.TestCase):
    def test_empty_comline(self):
        env.clean_output()
        self.assertRaises(SystemExit, argparse_parse_args, env, [])

        (out, err) = env.get_output()
        self.assertEqual(out, '')
        self.assertRegexpMatches(err.lower(), r'.*command line.*')

    def test_httpress_args_only(self):
        comline = '-n 100 http://www.yandex.ru/ -c 10'
        res = HttpressComLine([], [], '-n 100 http://www.yandex.ru/ -c 10'.split())
        argparse_parse_args(env, comline.split())
        self.assertEqual(argparse_parse_args(env, comline.split()), res)

    def test_hosts_and_file(self):
        comline = '--hosts mytesthost,localhost --file ./test http://www.yandex.ru/'
        res = HttpressComLine(['mytesthost', 'localhost'], ['./test'], ['http://www.yandex.ru/'])
        self.assertEqual(argparse_parse_args(env, comline.split()), res)

    def test_mixed(self):
        comline = '-n 100 --hosts localhost,user@23.23.23.13,root@pass:mytesthost ' \
                  '-f ./../somefile -c 10 http://www.yandex.ru/ --file ./test'
        res = HttpressComLine(['localhost', 'user@23.23.23.13', 'root@pass:mytesthost'],
                                 ['./../somefile', './test'], '-n 100 -c 10 http://www.yandex.ru/'.split())
        self.assertEqual(argparse_parse_args(env, comline.split()), res)


class Test_argparseParseArgs_help(unittest.TestCase):
    def test_help_only(self):
        env.clean_output()
        self.assertRaises(SystemExit, argparse_parse_args, env, ['--help'])
        (out, err) = env.get_output()

        self.assertEqual(err, '')

        pattern = re.compile(r'={5,}\s*')
        match = pattern.search(out)
        self.assertIsNotNone(match)
        self.assertEqual(out[match.end():].strip(), httpress_help_msg_stripped)

    def test_help_mixed(self):
        env.clean_output()
        self.assertRaises(SystemExit, argparse_parse_args, env,
                          '--hosts mytesthost,localhost --help '
                          '--file ./test http://www.yandex.ru/'.split())

        (out, err) = env.get_output()

        self.assertEqual(err, '')

        pattern = re.compile(r'={5,}\s*')
        match = pattern.search(out)
        self.assertIsNotNone(match)

        rest = out[match.end():]
        self.assertEqual(rest.strip(), httpress_help_msg_stripped)

    def test_httpress_help_only(self):
        env.clean_output()
        self.assertRaises(SystemExit, argparse_parse_args, env, ['-h'])

        (out, err) = env.get_output()
        self.assertEqual(err, '')
        self.assertEqual(out.strip(), httpress_help_msg_stripped)


class Test_argparseParseArgs_hosts(unittest.TestCase):
    def test_hosts_only(self):
        comline = '--hosts localhost,root@pass:mytesthost,mytesthost,239.0.0.1 http://www.yandex.ru/'
        res = HttpressComLine(['localhost', 'root@pass:mytesthost', 'mytesthost', '239.0.0.1'],
                                 [], ['http://www.yandex.ru/'])
        self.assertEqual(argparse_parse_args(env, comline.split()), res)

    def test_hosts_only_multi(self):
        comline = '--hosts localhost,root@pass:mytesthost http://www.yandex.ru/ --hosts mytesthost --hosts 239.0.0.1'
        res = HttpressComLine(['localhost', 'root@pass:mytesthost', 'mytesthost', '239.0.0.1'],
                                 [], ['http://www.yandex.ru/'])
        self.assertEqual(argparse_parse_args(env, comline.split()), res)


class Test_argparseParseArgs_file(unittest.TestCase):
    def test_file_only(self):
        comline = 'http://www.yandex.ru/ --file ./test'
        res = HttpressComLine([], ['./test'], ['http://www.yandex.ru/'])
        self.assertEqual(argparse_parse_args(env, comline.split()), res)

    def test_file_only_multi(self):
        comline = '-f some_file --file ./../text2 http://www.yandex.ru/ --file ./test'
        res = HttpressComLine([], ['some_file', './../text2', './test'], ['http://www.yandex.ru/'])
        self.assertEqual(argparse_parse_args(env, comline.split()), res)

    def test_file_options(self):
        self.assertEqual(argparse_parse_args(env, '--file ./test'.split()),
                         HttpressComLine([], ['./test'], []))
        self.assertEqual(argparse_parse_args(env, '-f ./test'.split()),
                         HttpressComLine([], ['./test'], []))

    def test_no_file_warning(self):
        # the message should be reimplemented with logging later
        comline = 'http://www.yandex.ru/'
        expected_result = HttpressComLine([], [], ['http://www.yandex.ru/'])
        (out, err, res) = helper.capture_output(argparse_parse_args, env, comline.split())
        self.assertEqual(res, expected_result)
        self.assertEqual(out, '')

    def test_one_file_warning(self):
        # the message should be reimplemented with logging later
        comline = '-f ./../text2 http://www.yandex.ru/'
        expected_result = HttpressComLine([], ['./../text2'], ['http://www.yandex.ru/'])
        (out, err, res) = helper.capture_output(argparse_parse_args, env, comline.split())
        self.assertEqual(res, expected_result)
        self.assertEqual(out, '')

    def test_multi_file_warning_msg(self):
        comline = '-f ./../text2 http://www.yandex.ru/ --file ./test'
        expected_result = HttpressComLine([], ['./../text2', './test'], ['http://www.yandex.ru/'])

        res = argparse_parse_args(env, comline.split())
        (out, err) = env.get_output()

        self.assertEqual(res, expected_result)
        # a relatively broad pattern for the message
        self.assertRegexpMatches(err, r'.*[Mm]ore than one\s.*--file/-f\s.*from all sources.*')


class Test_argparseParseArgs_verbose(unittest.TestCase):
    def test_verbose_only(self):
        comline = 'http://www.yandex.ru/ --verbose'
        res = HttpressComLine([], [], ['http://www.yandex.ru/'])
        self.assertEqual(argparse_parse_args(env, comline.split()), res)

    def test_verbose_options(self):
        self.assertEqual(argparse_parse_args(env, ['--verbose']),
                         HttpressComLine([], [], []))
        self.assertEqual(argparse_parse_args(env, ['-v']),
                         HttpressComLine([], [], []))


class Test_httpress_bin_help(unittest.TestCase):
    def test_h_option(self):
        res = os.system(env.httpress_bin_path + ' -h' + ' > /dev/null')
        self.assertEqual(res, 0)

    def test_help_option(self):
        res = os.system(env.httpress_bin_path + ' --help' + ' > /dev/null')
        self.assertNotEquals(res, 0)

#========================
if __name__ == '__main__':  # pragma: no cover
    unittest.main(exit=False, failfast=False)