#!/usr/bin/python
# coding=utf-8
#
# report.py
# Methods for transforming the stdout of 'httpress' bin
#
__author__ = 'voddan'

# <editor-fold desc="HTTPRESS OUTPUT EXAMPLE">
#
# TOTALS:  400 connect, 400 requests, 399 success, 1 fail, 20 (20) real concurrency
# RESPONSE: 2xx 299 (100.0%), non-2xx 0 (0.0%)
# TRAFFIC: 56139 avg bytes, 1034 avg overhead, 11171738 bytes, 412921 overhead
# TIMING:  2.026 seconds, 198 rps, 11110 kbps, 100.5 ms avg req time
# loops: 200; failed: 1; time: 2.026; rate: { 199.029 } req/sec;
#
# </editor-fold>

from abc import abstractmethod
import re

class HttpressOutput:
    """
    Data class for parsing, keeping, transforming
    and printing the stdout of 'httpress' bin
    """
    class InitLengthMismatchError(Exception):
        def __init__(self, class_len, value_len):
            self.class_len = class_len
            self.value_len = value_len

        def __str__(self):
            return 'Class was initialised with %d arguments instead of %d' % (self.value_len, self.class_len)

    def __init__(self, totals, response, traffic, timing, loops):
        self.totals = totals
        self.response = response
        self.traffic = traffic
        self.timing = timing
        self.loops = loops

    def __str__(self):
        return '%s\n%s\n%s\n%s\n%s' % (str(self.totals),
                                       str(self.response),
                                       str(self.traffic),
                                       str(self.timing),
                                       str(self.loops))

    @staticmethod
    def parse(text):
        parsers = [HttpressOutput.Totals.parser(),
                   HttpressOutput.Response.parser(),
                   HttpressOutput.Traffic.parser(),
                   HttpressOutput.Timing.parser(),
                   HttpressOutput.Loops.parser()]

        end = -1
        categories = []
        for parser in parsers:
            match = parser.search(text, pos=(end + 1))
            if match is not None:
                end = match.end()
                categories.append(match.groups())
                # print end

        return HttpressOutput(HttpressOutput.Totals(categories[0]),
                              HttpressOutput.Response(categories[1]),
                              HttpressOutput.Traffic(categories[2]),
                              HttpressOutput.Timing(categories[3]),
                              HttpressOutput.Loops(categories[4]))

    class _Category:
        """
        Abstract class for different categories of contained data

        Implement '__len__(self): return K'
        to be able to keep exactly K constants in an instance

        Implement '__str__(self): return "some string" '
        to have a formatted text representation.
        You may use build-in string formatting and 'self.tuple'.
        You don't need a '\n' in the end.
        """
        # @staticmethod
        @abstractmethod
        def __len__(self):
            pass

        @abstractmethod
        def __str__(self):
            pass

        @staticmethod
        def parser():
            return re.compile(r'', re.M)

        def __init__(self, arg_tuple):
            """
            :type arg_tuple: tuple
            """
            if len(self) != len(arg_tuple):
                raise HttpressOutput.InitLengthMismatchError(len(self), len(arg_tuple))
            """:type : tuple"""
            self.tuple = arg_tuple

    class Totals(_Category):
        def __len__(self):
            return 6

        def __str__(self):
            print "very STRANGE CODE !!!!"
            return 'TOTALS:  %d connect, %d requests, %d success, %d fail, %d (%d) real concurrency' #% self.tuple

        @staticmethod
        def parser():
            return re.compile(r'TOTALS:  (\d+) connect, (\d+) requests, '
                              r'(\d+) success, (\d+) fail, '
                              r'(\d+) \((\d+)\) real concurrency', re.M)

    class Response(_Category):
        def __len__(self):
            return 4

        def __str__(self):
            return 'RESPONSE: 2xx %d (%.1f%%), non-2xx %d (%.1f%%)' % self.tuple

        @staticmethod
        def parser():
            return re.compile(r'RESPONSE: 2xx (\d+) \((\d+\.\d+)%\), '
                              r'non-2xx (\d+) \((\d+\.\d+)%\)', re.M)

    class Traffic(_Category):
        def __len__(self):
            return 4

        def __str__(self):
            return 'TRAFFIC: %d avg bytes, %d avg overhead, %d bytes, %d overhead' % self.tuple

        @staticmethod
        def parser():
            return re.compile(r'TRAFFIC: (\d+) avg bytes, (\d+) avg overhead, '
                              r'(\d+) bytes, (\d+) overhead', re.M)

    class Timing(_Category):
        def __len__(self):
            return 4

        def __str__(self):
            return r'TIMING:  %.3f seconds, %d rps, %d kbps, %.1f ms avg req time' % self.tuple

        @staticmethod
        def parser():
            return re.compile(r'TIMING:  (\d+\.\d+) seconds, (\d+) rps, '
                              r'(\d+) kbps, (\d+\.\d+) ms avg req time', re.M)

    class Loops(_Category):
        def __len__(self):
            return 4

        def __str__(self):
            return 'loops: %d; failed: %d; time: %.3f; rate: { %.3f } req/sec;' % self.tuple

        @staticmethod
        def parser():
            return re.compile(r'loops: (\d+); failed: (\d+); time: (\d+\.\d+); '
                              r'rate: [{] (\d+\.\d+) [}] req/sec;', re.M)
