#!/usr/bin/python
# coding=utf-8
#
# main.py
# Lunches external bin 'httpress' (httpress_rh6)
#
__author__ = 'voddan'
__package__ = None
# from common import __version__

import os
import sys
import logging

__file_path__ = os.path.dirname(os.path.realpath(__file__))
__project_root__ = __file_path__ + '/../'

from common import GlobalEnvironment
from test.helper import TestingEnvironment
from common import Environment
from common import load_host_lines_from_single_file
from report import HttpressReport
from report import HttpressReportCollector
from comline import argparse_parse_args
from hostline import parse_host_lines
from hostline import LocalHost
from launching import launch_localhost
from launching import launch_localhost_life
from launching import collect_output

import subprocess


def main(env, comline_argv):
    """
    :type env: Environment
    :type comline_argv: list[str]
    """
    env.debug(comline_argv)

    options = argparse_parse_args(env, comline_argv)

    env.debug('options: %s' % str(options))
    # ----------------------------------
    # COMBINING host_lines
    host_lines = options.host_line_list

    for filename in options.filename_list:
        env.info('loading a hostlist from: %s' % filename)
        host_lines.extend(load_host_lines_from_single_file(filename))

    env.debug('host_lines: %s' % str(host_lines))
    # --------------------
    hosts = parse_host_lines(env, host_lines)

    env.debug('hosts: %s' % str(hosts))
    # ----------------
    # LUNCHING httpress

    # TODO: unit tests
    # assuming LocalHost if no hosts are provided
    if not hosts:
        hosts.append(LocalHost())

    environment.info("ready to launch on hosts: %s" % str(hosts))

    # TODO: unit tests
    # using one LocalHost for a better process control (starts from 0)
    if LocalHost() in hosts:
        hosts.remove(LocalHost())  # ValueError
        launch_special_child = True
    else:
        launch_special_child = False

    # LAUNCHING THE REST (starts from 1)
    # TODO: support remote launching
    # TODO: print stderr if a task has failed
    children_list = []
    for host in hosts:
        (child, millitime) = launch_localhost(env, args=options.parameters_to_pass)
        children_list.append((child, host, millitime))

    if launch_special_child:
        env.text('=========== life =============')
        (special_child, special_milliseconds, special_output, special_err) = \
            launch_localhost_life(env, env.text_stream, args=options.parameters_to_pass)

    # WAITING FOR THE REST
    (output_list, failed_list) = collect_output(env, children_list)

    for i, output in enumerate(output_list):
        env.text('===========%4d =============' % (i + 1))
        env.text(output)

    # APPENDING THE SPECIAL CHILD
    if launch_special_child:
        if special_err or not special_child:
            failed_list.append((LocalHost(), special_milliseconds))
        else:
            output_list.append(special_output)

    env.text('=== FAILED:         %4d =================' % len(failed_list))
    for (host, millitime) in failed_list:
        env.text('Task on %s at %f FAILED' % (str(host), millitime))

    report_list = [HttpressReport().parse(output) for output in output_list]

    collector = HttpressReportCollector()
    for report in report_list:
        collector.collect(report)

    main_report = collector.report()

    if launch_special_child:
        env.text('=== TOTAL LAUNCHED: %4d + 1 (life) ======' % len(hosts))
    else:
        env.text('=== TOTAL LAUNCHED: %4d =================' % len(hosts))
    env.text('==========================================')

    try:
        env.text(main_report.__str__())
    except HttpressReport.EmptyReportError:
        env.text('no report')
    except HttpressReport.StructureError:
        env.error('Total report can not be printed. '
                         'Please consider: %s' %
                         main_report.__repr__())


#========================
# USE the mock version if your connection is slow

# environment = TestingEnvironment(__project_root__ + 'bin/httpress_mock.py')  # print stderr,
# environment = TestingEnvironment(__project_root__ + 'bin/httpress_mock_slow.py')  # print stderr,
environment = GlobalEnvironment(__project_root__ + 'bin/httpress_mock_slow.py', version='testing')
# environment = GlobalEnvironment(__project_root__ + 'bin/httpress_rh6', version='0.1')

if __name__ == '__main__':  # pragma: no cover
    main(environment, sys.argv)

def main_launcher(comline_argv):
    """
    :type comline_argv: list[str]
    """
    main(environment, comline_argv)