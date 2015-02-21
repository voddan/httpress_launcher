# coding=utf-8
#
# report.py
# Methods for transforming the stdout of 'httpress' bin
#
__author__ = 'voddan'
__package__ = None

# <editor-fold desc="HTTPRESS OUTPUT SPEC">
#
# TOTALS:  400 connect, 400 requests, 399 success, 1 fail, 20 (20) real concurrency
# RESPONSE: 2xx 299 (100.0%), non-2xx 0 (0.0%)
# TRAFFIC: 56139 avg bytes, 1034 avg overhead, 11171738 bytes, 412921 overhead
# TIMING:  2.026 seconds, 198 rps, 11110 kbps, 100.5 ms avg req time
# loops: 200; failed: 1; time: 2.026; rate: { 199.029 } req/sec;
#
# </editor-fold>

import re
from abc import abstractmethod
from common import Comparable

# TODO: check input on types, generate sensible error messages
class HttpressReport(Comparable):
    """
    Data class for parsing, keeping
    and printing the stdout of 'httpress' bin
    """
    def __init__(self):
        """
        :type: list[tuple]
        """
        self.lines = []

    def __repr__(self):
        return self.lines.__repr__()

    def set(self, new_lines):
        """
        Sets parameters for the self instance, then returns it
        Handy for testing
        Performs no type-assertion

        :type new_lines: list[tuple]
        :rtype: HttpressReport
        """
        self.lines = new_lines
        return self

    def __eq__(self, other):
        return self.lines == other.lines

    def __str__(self):
        if len(self.lines) == 0:
            raise HttpressReport.EmptyReportError(self)

        # TODO: hardcodded number of lines
        if len(self.lines) != 5:
            raise HttpressReport.StructureError(self)

        result = ''
        try:
            result += 'TOTALS:  %d connect, %d requests, %d success, %d fail, %d (%d) real concurrency\n' % self.lines[0]
            result += 'RESPONSE: 2xx %d (%.1f%%), non-2xx %d (%.1f%%)\n' % self.lines[1]
            result += 'TRAFFIC: %d avg bytes, %d avg overhead, %d bytes, %d overhead\n' % self.lines[2]
            result += 'TIMING:  %.3f seconds, %d rps, %d kbps, %.1f ms avg req time\n' % self.lines[3]
            result += 'loops: %d; failed: %d; time: %.3f; rate: { %.3f } req/sec;' % self.lines[4]
        except TypeError:
            HttpressReport.StructureError(self)

        return result

    def parse(self, text):
        """
        Parsers text and fulls up the self instance, then returns it

        :type text: str
        :rtype: HttpressReport
        """
        self.lines = []

        expressions = [
            r'TOTALS:  (\d+) connect, (\d+) requests, (\d+) success, (\d+) fail, (\d+) \((\d+)\) real concurrency$',
            r'RESPONSE: 2xx (\d+) \((\d+\.\d+)%\), non-2xx (\d+) \((\d+\.\d+)%\)$',
            r'TRAFFIC: (\d+) avg bytes, (\d+) avg overhead, (\d+) bytes, (\d+) overhead$',
            r'TIMING:  (\d+\.\d+) seconds, (\d+) rps, (\d+) kbps, (\d+\.\d+) ms avg req time$',
            r'loops: (\d+); failed: (\d+); time: (\d+\.\d+); rate: \{ (\d+\.\d+) \} req/sec']

        # on an exception any tests fails
        patterns = [re.compile(expression, re.M)
                    for expression in expressions]

        # a performance optimisation
        matches = []
        pos = 0
        for pattern in patterns:
            match = pattern.search(text, pos=pos)

            if match is not None:
                matches.append(match)
                pos = match.end() + 1
            else:
                raise HttpressReport.ParsingError(pattern.pattern, text, pos)

        for match in matches:
            accumulator = []
            for string in match.groups():
                try:
                    try:
                        accumulator.append(int(string))
                    except ValueError:
                        accumulator.append(float(string))
                except ValueError:
                    # nothing else may be get because
                    # the expression collects only digits
                    raise

            self.lines.append(tuple(accumulator))

        return self

    class ParsingError(RuntimeError):
        def __init__(self, incorrect_line, text, start_pos):
            """
            Parameter 'text' may be big, so it is not present im the error message

            :type incorrect_line: str
            :type text: str
            :type start_pos: int
            """
            RuntimeError.__init__(self, "Unable to match pattern (re) on position %d: %s" %
                                        (start_pos, incorrect_line))
            self.incorrect_line = incorrect_line
            self.text = text  # may be useful on handling
            self.start_pos = start_pos

    class StructureError(RuntimeError):
        def __init__(self, report):
            """
            :type report: HttpressReport
            """
            self.report = report
            RuntimeError.__init__(self, "Internal structure of the report is invalid: %s" %
                                  str(report.lines))

    class EmptyReportError(StructureError):
        pass


class Functor:  # pragma: no cover
    """
    Base class for actions for collecting HttpressReport
    """
    @abstractmethod
    def __repr__(self):
        """
        :rtype: str
        """
        raise NotImplementedError

    @abstractmethod
    def collect(self, old, new):
        """
        Mixes up 'old' values from HttpressReportCollector
        with 'new' values form HttpressReport

        :type old: int | float
        :type new: int | float
        :rtype: int | float
        """
        raise NotImplementedError

    @abstractmethod
    def report(self, count, value):
        """
        Converts values from HttpressReportCollector
        to values for HttpressReport

        :type count: int
        :type value: int | float
        :rtype: int | float
        """
        raise NotImplementedError

class Sum(Functor):
    def __repr__(self):
        return 'Sum'

    def collect(self, old, new):
        return old + new

    def report(self, count, value):
        return value

class Max(Functor):
    def __repr__(self):
        return 'Max'

    def collect(self, old, new):
        return max(old, new)

    def report(self, count, value):
        return value

class Avr(Functor):
    """Average"""
    def __repr__(self):
        return 'Avr'

    def collect(self, old, new):
        return old + new

    def report(self, count, value):
        if count != 0:
            return value / count
        else:
            return value

class Nth(Functor):
    """Nothing"""
    def __repr__(self):
        return 'Nth'

    def collect(self, old, new):
        # nobody cares
        return 0

    def report(self, count, value):
        # TODO: what do I do with the representation ?
        # means unreliable result
        # must be int or float to let HttpressReport.__str__() work
        return -1


class HttpressReportCollector(Comparable):
    """
    Class for transforming data in HttpressReport
    Collects data from HttpressReports one by one,
    then may be transformed to a HttpressReport by
    the report() method
    """
    functors = (
        (Sum(), Sum(), Sum(), Sum(), Sum(), Sum()),
        (Sum(), Nth(), Sum(), Nth()),
        (Avr(), Avr(), Sum(), Sum()),  # by SPEC it should be (Nth(), Nth(), Sum(), Sum())
        (Nth(), Avr(), Sum(), Avr()),  # by SPEC it should be (Nth(), Nth(), Sum(), Avr())
        (Sum(), Sum(), Max(), Sum())
    )
    # TODO: what is the meaning of 'Timing: 2.0026 sec'?

    def __init__(self):
        self.count = 0
        self.lines = []

    def set(self, new_count, new_lines):
        """
        Sets parameters for the self instance, then returns it
        Handy for testing
        Performs no type checks

        :type new_lines: list[tuple]
        :type new_count: int
        :rtype: HttpressReportCollector
        """
        self.count = new_count
        self.lines = new_lines
        return self

    def __eq__(self, other):
        """
        :type other: HttpressReport | HttpressReportCollector
        :rtype: bool
        """
        if isinstance(other, HttpressReportCollector):
            return self.lines == other.lines and \
                   self.count == other.count
        elif isinstance(other, HttpressReport):
            return self.lines == other.lines
        else:
            return False

    def __repr__(self):
        result = 'HttpressReportCollector( count = %d,\n' % self.count
        result += ''.join(['\t%s,\n' % str(line) for line in self.lines])
        result += ')'
        return result

    def report(self):
        """
        Transforms HttpressReportCollector
        to a HttpressReport

        :rtype: HttpressReport
        """
        assert self.lines is not None

        new_lines = []
        for index in range(len(self.lines)):
            old_line = self.lines[index]
            func = HttpressReportCollector.functors[index]

            new_line = [func[i].report(self.count, old_line[i])
                        for i in range(len(old_line))]
            new_lines.append(tuple(new_line))

        report = HttpressReport()
        report.lines = new_lines
        return report

    def collect(self, report):
        """
        Collects a HttpressReport

        :type report: HttpressReport
        """
        if self.count == 0:
            self.lines = report.lines
            self.count += 1
        else:
            assert self.lines is not None

            new_lines = []
            for index in range(len(self.lines)):
                old_line = self.lines[index]
                new_line = report.lines[index]
                func = HttpressReportCollector.functors[index]

                line = [func[i].collect(old_line[i], new_line[i])
                        for i in range(len(old_line))]
                new_lines.append(tuple(line))

            self.lines = new_lines
            self.count += 1