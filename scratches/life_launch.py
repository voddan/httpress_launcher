#!/usr/bin/python
# coding=utf-8
# life_launch.py
#
import logging
import subprocess
import sys
import time

__author__ = 'voddan'
__package__ = None
# ---------------------------------------
def launch_localhost(_bin_path, args=()):
    """
    Launches one instance of the bin file on LocalHost

    :type _bin_path: str | None
    :type args: list[str]
    :rtype: (POpen|None, float)
    """
    comline_list = [_bin_path] + args

    millitime = time.time() * 1000
    logging.info("launching LocalHost at time[millisec]: %f" % millitime)
    try:
        child = subprocess.Popen(comline_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        logging.debug("subprocess.Popen: %f", time.time())
    except:
        logging.error("Unable to launch an instance on LocalHost at %f with '%s'" %
                          (millitime, ' '.join(comline_list)))
        child = None

    return child, millitime


def launch_localhost_life(_bin_path, args=()):
    """
    Launches one instance of the bin file on LocalHost
    Prints the result to text_stream instantly right while processing

    :type _bin_path: str | None
    :type args: list[str]

    :rtype: (POpen|None, float, str, str)
    """
    (_child, _milli) = launch_localhost(_bin_path, args)

    if not _child:
        return None, _milli, "", ""

    _out = _child.stdout
    _err = _child.stderr

    _output_text = ""
    logging.debug("output_text: %f", time.time())
    while True:
        _out_line = _out.readline()
        logging.debug("readline: %f", time.time())
        _output_text += _out_line
        sys.stdout.write(_out_line)
        if _out_line == '':
            break

    _error_text = ''.join(_err.readlines())
    print >> sys.stdout, _error_text

    return _child, _milli, _output_text, _error_text

# ---------------------------------------
logging.getLogger().setLevel(logging.DEBUG)

# bin_path = "../bin/httpress_rh6"
bin_path = "../bin/httpress_mock_slow_error.py"
# bin_path = "../bin/httpress_mock_slow.py"

args_val = "-n 100 -c 10 http://www.mit.edu/".split()
logging.debug(args_val)
# ---------------------------------------


# (child, milli) = launch_localhost(bin_path, args_val)
# comline_list = [bin_path] + args_val
comline_list = ["/home/voddan/Program/Parallels/httpress_launcher/bin/httpress_rh6"] + args_val

logging.info("launching LocalHost at time: %f" % time.time())

child = subprocess.Popen(comline_list, stdout=subprocess.PIPE)
# logging.debug("subprocess.Popen: %f", time.time())

assert child

# logging.debug("output_text: %f", time.time())

out = iter(child.stdout.readline, "")
child.stdout.flush()
for line in out:
    child.stdout.flush()
    print line,


# while True:
#         nextline = child.stdout.readline()
#         if not nextline:
#             break
#         sys.stdout.write(nextline)
#         sys.stdout.flush()

# while child.poll() is None:
#     out = child.stdout.read(1)
#     sys.stdout.write(out)
#     sys.stdout.flush()


# TODO: making a simplified version