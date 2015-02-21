#!/usr/bin/python
# coding=utf-8
# test_launching.py
#
__author__ = 'voddan'
__package__ = None

import unittest
import logging
import helper

from src.common import GlobalEnvironment
from src.hostline import LocalHost

env = helper.TestingEnvironment('../bin/httpress_mock.py',
                                logger_level=logging.DEBUG)

@unittest.skip("Splitting launching and communication. In progress")
class Test_launchLocalBinExecs(unittest.TestCase):
    def test_bin_path(self):
        (output_list, failed_list) = launch_local_bin_execs(env, [LocalHost()], 'echo', ['Hello', '!!'])
        self.assertEqual(output_list, ['Hello !!\n'])
        self.assertEqual(failed_list, [])

    @unittest.skip("deprecated")
    def test_environment_bin_path(self):
        env_echo = helper.TestingEnvironment('echo', version='01')
        (output_list, failed_list) = launch_local_bin_execs(env_echo, [LocalHost()],
                                                            bin_path=None, args=['Hello', '!!'])
        self.assertEqual(output_list, ['Hello !!\n'])
        self.assertEqual(failed_list, [])

    def test_multi_hosts(self):
        (output_list, failed_list) = launch_local_bin_execs(env, [LocalHost()] * 5, 'echo', ['Hello', '!!'])
        self.assertEqual(output_list, ['Hello !!\n'] * 5)
        self.assertEqual(failed_list, [])

    def test_printing(self):
        N = 5
        host_list = [LocalHost()] * N
        host_list_str = str(host_list)

        env.clean_output()  # DEBUG level
        (output_list, failed_list) = launch_local_bin_execs(env, host_list, 'echo', ['Hello', '!!'])
        (out, err) = env.get_output()

        self.assertEqual(output_list, ['Hello !!\n'] * N)
        self.assertRegexpMatches(out, r".*%s.*" % host_list_str)
        self.assertEqual(failed_list, [])

    def test_failed_list(self):
        N = 2
        (output_list, failed_list) = launch_local_bin_execs(env, [LocalHost()] * N,
                                                            'ls', ['--a'])
        self.assertEqual(output_list, [])
        self.assertEqual([host for host, time in failed_list],
                         [(LocalHost())] * N)


# ========================
if __name__ == '__main__':  # pragma: no cover
    unittest.main(exit=False, failfast=False)
