#!/usr/bin/python
# coding=utf-8
# launching.py
#
__author__ = 'voddan'
__package__ = None

import time
import subprocess
import common

# TODO: separate launching and collection of the information

def collect_output(environment, children_list):
    """
    Collects output from child processes

    :type environment: common.Environment
    :type children_list: list[(POpen|None, Host, float)]
    :rtype: (list[str], list[(Host, float)])
    """
    output_list = []
    failed_list = []
    for (child, host, millitime) in children_list:
        if child is None:
            failed_list.append((host, millitime))

        (out, err) = child.communicate()
        if not err:
            output_list.append(out)
        else:
            failed_list.append((host, millitime))

    return output_list, failed_list


# TODO: add unit tests
def launch_localhost(environment, bin_path=None, args=()):
    """
    Launches one instance of the bin file on LocalHost

    :type environment: common.Environment
    :type bin_path: str | None
    :type args: list[str]
    :rtype: (POpen|None, float)
    """
    if bin_path is None:
        bin_path = environment.httpress_bin_path

    comline_list = [bin_path] + args

    millitime = time.time() * 1000
    environment.info("launching LocalHost at time[millisec]: %f" % millitime)
    try:
        child = subprocess.Popen(comline_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except:
        environment.error("Unable to launch test instance on LocalHost at %f with '%s'" %
                          (millitime, ' '.join(comline_list)))
        child = None

    return child, millitime

# TODO: add unit tests
def launch_localhost_life(environment, text_stream, bin_path=None, args=()):
    """
    Launches one instance of the bin file on LocalHost
    Prints the result to text_stream instantly right while processing

    :type environment: common.Environment
    :type text_stream: Stream
    :type bin_path: str | None
    :type args: list[str]

    :rtype: (POpen|None, float, str, str)
    """
    (child, milli) = launch_localhost(environment, bin_path, args)

    if not child:
        return child, milli, "", ""

    output = ""
    while True:
        out_line = child.stdout.readline()
        output += out_line
        text_stream.write(out_line)
        if out_line == '':
            break

    err = child.stdout.readlines()
    err = ''.join(err)
    print >> text_stream, err

    return child, milli, output, err
