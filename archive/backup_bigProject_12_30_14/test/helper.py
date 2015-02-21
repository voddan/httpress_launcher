#!/usr/bin/python
# coding=utf-8
# helper
#
__author__ = 'voddan'
__package__ = None

from StringIO import StringIO
import sys
import logging
import random
import time
from src.common import Environment
from src.common import logger_basic_config


# USAGE:
# 
# with Capturing() as output:
#     do_something(my_object)
# 
# with Capturing(output) as output:
#     print 'hello world2'

# TODO: write unit tests
# TODO: consider the .splitlines() following '\n'.join(..)
class Capturing(list):
    """
    Special class for capturing stdout and strerr
    http://stackoverflow.com/questions/16571150/how-to-capture-stdout-output-from-a-python-function-call
    """
    def __enter__(self):
        self._stringio_stdout = StringIO()
        self._stringio_stderr = StringIO()

        self._save_stdout = sys.stdout
        self._save_stderr = sys.stderr

        sys.stdout = self._stringio_stdout
        sys.stderr = self._stringio_stderr
        return self
    
    def __exit__(self, *args):
        """
        :type self: Capturing
        """
        self.stdout = []
        self.stderr = []

        self.stdout.extend(self._stringio_stdout.getvalue().splitlines())
        self.stderr.extend(self._stringio_stderr.getvalue().splitlines())

        sys.stdout = self._save_stdout
        sys.stderr = self._save_stderr


def capture_output(callableObj, *args, **kwargs):
    """
    Captures the stdout of a function
    Returns stdout as a multi-line string
    Returns the return value or None

    :rtype: tuple(str, str, Object)
    """
    result = None
    with Capturing() as output:
        try:
            result = callableObj(*args, **kwargs)
        except:
            pass
            # may be anything, I care about stdout
    return '\n'.join(output.stdout), '\n'.join(output.stderr), result

def test_procedure(callableObj, *args, **kwargs):
    """
    Returns the return value,
    stdout and stderr as multi-line strings
    and exception if have been raised

    :rtype: tuple(Object, str, str, Exception | None)
    """
    result = None
    with Capturing() as output:
        try:
            result = callableObj(*args, **kwargs)
        except BaseException, e:
            exception = e
        else:
            exception = None
    return result, '\n'.join(output.stdout), '\n'.join(output.stderr), exception


# Now before EVERY test with output capturing create a new instance
class TestingEnvironment(Environment):
    SHHKEY = Environment.SHHKEY

    def __init__(self,
                 httpress_bin_path=None,
                 version='testing',
                 logger_level=logging.WARNING):
        """
        'logger_debug_output=True' allow using get_output(), empty_output()
        and shuts up the output to the console

        In case of 'httpress_bin_path = None' an exception may be raised

        A randomly named logger is used

        :type httpress_bin_path: str | None
        :type version: str
        :type logger_level: int
        """
        self._logger_out_stream = StringIO()
        self._logger_err_stream = StringIO()

        self._logger_level_emulator = logger_level

        logger_name = 'TESTLOGGER_%d_%f' % (random.randint(100, 1000000), time.time())

        Environment.__init__(self,
                             httpress_bin_path,
                             version,
                             'root',
                             self.SHHKEY(),
                             logging.getLogger(logger_name.replace('.', '_')),
                             self._logger_out_stream)

        logger_basic_config(self._logger,
                            None,
                            logger_level,
                            self._logger_out_stream,
                            self._logger_err_stream)

    def clean_output(self):
        self._logger_out_stream.truncate(0)
        self._logger_err_stream.truncate(0)

    def get_output(self):
        """
        Returns stdout and stderr of the Environment

        :rtype: (str, str)
        """
        output = (self._logger_out_stream.getvalue(),
                  self._logger_err_stream.getvalue())
        self.clean_output()
        return output

    def set_logging_level(self, level):
        """
        To test a peace of code which sets logging level
        use local GlobalEnvironment
        """
        self._logger_level_emulator = level
        # print a warning in unittest system if possible

    def get_logging_level(self):
        return self._logger_level_emulator