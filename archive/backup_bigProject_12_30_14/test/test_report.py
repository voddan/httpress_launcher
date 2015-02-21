#!/usr/bin/python
# coding=utf-8
# test_output
#
__author__ = 'voddan'
__package__ = None

import unittest
import copy

from src.report import HttpressReport
from src.report import Sum, Avr, Max, Nth
from src.report import HttpressReportCollector


class Test_HttpressReport(unittest.TestCase):
    def test_init(self):
        obj = HttpressReport()
        self.assertEqual(obj.lines, [])

    def test_repr(self):
        obj = HttpressReport()
        obj.set([(1, 2, 0.4), (0.5, 2)])
        expected_repr = '[(1, 2, 0.4), (0.5, 2)]'
        self.assertEqual(obj.__repr__(), expected_repr)

    def test_set(self):
        # Did not care on type validation
        # Fix if implemented
        tup1 = (1, 2, 3, 4, 5)
        tup2 = (1, 2, 3, 4, 6)
        tup3 = (1, 2, 3, 4)

        # to be sure
        tup1_ = copy.copy(tup1)
        tup2_ = copy.copy(tup2)
        tup3_ = copy.copy(tup3)

        # testing on a new instance each time
        self.assertEqual(HttpressReport().set([tup1]).lines, [tup1_])
        self.assertEqual(HttpressReport().set([tup1, tup2]).lines, [tup1_, tup2_])
        self.assertEqual(HttpressReport().set([tup1, tup2, tup3]).lines, [tup1_, tup2_, tup3_])

        self.assertNotEqual(HttpressReport().set([tup1, tup3]).lines, [tup2, tup3])
        self.assertNotEqual(HttpressReport().set([tup1, tup2]).lines, [tup1, tup3])

        # testing on the same instance
        # set(..) must reset all properties
        httpressReport_i = HttpressReport()
        self.assertEqual(httpressReport_i.lines, [])

        self.assertEqual(httpressReport_i.set([tup1]).lines, [tup1_])
        self.assertEqual(httpressReport_i.set([tup1, tup2]).lines, [tup1_, tup2_])
        self.assertEqual(httpressReport_i.set([tup1, tup2, tup3]).lines, [tup1_, tup2_, tup3_])

        self.assertNotEqual(httpressReport_i.set([tup1, tup3]).lines, [tup2, tup3])
        self.assertNotEqual(httpressReport_i.set([tup1, tup2]).lines, [tup1, tup3])

    def test_eq(self):
        obj1 = HttpressReport()
        obj2 = HttpressReport()

        self.assertEqual(obj1, obj2)
        self.assertEqual(obj1, obj1)

        tup1 = (1, 2, 3, 4, 5)
        tup2 = (1, 2, 3, 4, 6)
        tup3 = (1, 2, 3, 4)

        # to be sure
        tup1_ = copy.copy(tup1)
        tup2_ = copy.copy(tup2)
        tup3_ = copy.copy(tup3)

        self.assertEqual(obj1.set([tup1]), obj2.set([tup1_]))
        self.assertEqual(obj1.set([tup1, tup2]), obj2.set([tup1_, tup2_]))
        self.assertEqual(obj1.set([tup1, tup2, tup3]), obj2.set([tup1_, tup2_, tup3_]))

        self.assertNotEqual(obj1.set([tup1, tup3]), obj2.set([tup2, tup3]))
        self.assertNotEqual(obj1.set([tup1, tup2]), obj2.set([tup1, tup3]))

    def test_str(self):
        string = ('TOTALS:  400 connect, 400 requests, 399 success, 1 fail, 20 (20) real concurrency\n'
                  'RESPONSE: 2xx 299 (100.0%), non-2xx 0 (0.0%)\n'
                  'TRAFFIC: 56139 avg bytes, 1034 avg overhead, 11171738 bytes, 412921 overhead\n'
                  'TIMING:  2.026 seconds, 198 rps, 11110 kbps, 100.5 ms avg req time\n'
                  'loops: 200; failed: 1; time: 2.026; rate: { 199.029 } req/sec;')

        lines = [
            (400, 400, 399, 1, 20, 20),
            (299, 100.0, 0, 0.0),
            (56139, 1034, 11171738, 412921),
            (2.026, 198, 11110, 100.5),
            (200, 1, 2.026, 199.029)
        ]

        self.assertEqual(str(HttpressReport().set(lines)), string)


class Test_HttpressReport_parse(unittest.TestCase):
    def test_parse(self):
        string = ('TOTALS:  400 connect, 400 requests, 399 success, 1 fail, 20 (20) real concurrency\n'
                  'RESPONSE: 2xx 299 (100.0%), non-2xx 0 (0.0%)\n'
                  'TRAFFIC: 56139 avg bytes, 1034 avg overhead, 11171738 bytes, 412921 overhead\n'
                  'TIMING:  2.026 seconds, 198 rps, 11110 kbps, 100.5 ms avg req time\n'
                  'loops: 200; failed: 1; time: 2.026; rate: { 199.029 } req/sec;')

        lines = [
            (400, 400, 399, 1, 20, 20),
            (299, 100.0, 0, 0.0),
            (56139, 1034, 11171738, 412921),
            (2.026, 198, 11110, 100.5),
            (200, 1, 2.026, 199.029)
        ]

        obj = HttpressReport().set(lines)

        self.assertEqual(obj, HttpressReport().parse(string))
        self.assertEqual(obj, HttpressReport().parse(string + 'some suffix'))
        self.assertEqual(obj, HttpressReport().parse('some prefix\n' + string))
        self.assertEqual(obj, HttpressReport().parse('some prefix\n' + string + 'some suffix'))
        self.assertEqual(obj, HttpressReport().parse(string + '\n' + string))

        # parse(..) must reset all properties
        another_obj = copy.deepcopy(obj)
        self.assertEqual(obj, another_obj.parse(string))

    def test_str_with_parse(self):
        # number of digit after a comma is fixed
        # number of positions is original, the values are not
        lines = [
            (1, 4020, 39, 15, 2110, 2),
            (2929, 10.0, 0, 0.5),
            (56139, 1034, 11138, 412111921),
            (2.026, 198, 110, 100.5),
            (80, 1, 2.026, 199.029)
        ]

        obj1 = HttpressReport().set(lines)
        string = str(obj1)
        obj2 = HttpressReport().parse('some prefix\n' + string + 'some suffix')

        self.assertEqual(obj1, obj2)

    def test_parse_error_line_disorder(self):
        # the order of lines is changed
        disordered_string = (
            'TOTALS:  400 connect, 400 requests, 399 success, 1 fail, 20 (20) real concurrency\n'
            'TRAFFIC: 56139 avg bytes, 1034 avg overhead, 11171738 bytes, 412921 overhead\n'
            'RESPONSE: 2xx 299 (100.0%), non-2xx 0 (0.0%)\n'
            'TIMING:  2.026 seconds, 198 rps, 11110 kbps, 100.5 ms avg req time\n'
            'loops: 200; failed: 1; time: 2.026; rate: { 199.029 } req/sec;'
        )

        self.assertRaises(HttpressReport.ParsingError,
                          HttpressReport.parse,
                          HttpressReport(), disordered_string)

    def test_parse_error_line_absence(self):
        # one line is missing
        incomplete_string = (
            'TOTALS:  400 connect, 400 requests, 399 success, 1 fail, 20 (20) real concurrency\n'
            'RESPONSE: 2xx 299 (100.0%), non-2xx 0 (0.0%)\n'
            'TIMING:  2.026 seconds, 198 rps, 11110 kbps, 100.5 ms avg req time\n'
            'loops: 200; failed: 1; time: 2.026; rate: { 199.029 } req/sec;'
        )

        self.assertRaises(HttpressReport.ParsingError,
                          HttpressReport.parse,
                          HttpressReport(), incomplete_string)


class Test_HttpressReport_ParsingError(unittest.TestCase):
    def test_init(self):
        exception = HttpressReport.ParsingError(r'abc\w*\\', 'abracadabra', 239)
        self.assertEqual(exception.incorrect_line, r'abc\w*\\')
        self.assertEqual(exception.text, 'abracadabra')
        self.assertEqual(exception.start_pos, 239)
        self.assertIsInstance(exception, RuntimeError)

    def test_repr(self):
        exception = HttpressReport.ParsingError(r'abc\w*\\', 'abracadabra', 239)
        string = exception.__repr__()
        self.assertRegexpMatches(string, r'.*239.*')
        self.assertRegexpMatches(string, r'.*abc\\\\w\*\\\\\\\\.*')


class Test_Sum(unittest.TestCase):
    def test_repr(self):
        self.assertEqual(Sum().__repr__(), 'Sum')

    def test_transform(self):
        self.assertEqual(Sum().collect(2, 3), 5)
        self.assertAlmostEqual(Sum().collect(0.4, 0.8), 1.2)

    def test_report(self):
        self.assertEqual(Sum().report(3, 34), 34)
        self.assertEqual(Sum().report(3, 3.4), 3.4)


class Test_Max(unittest.TestCase):
    def test_repr(self):
        self.assertEqual(Max().__repr__(), 'Max')

    def test_transform(self):
        self.assertEqual(Max().collect(2, 3), 3)
        self.assertEqual(Max().collect(3, 2), 3)
        self.assertEqual(Max().collect(0.4, 0.8), 0.8)

    def test_report(self):
        self.assertEqual(Max().report(3, 34), 34)
        self.assertEqual(Max().report(3, 3.4), 3.4)


class Test_Avr(unittest.TestCase):
    def test_repr(self):
        self.assertEqual(Avr().__repr__(), 'Avr')

    def test_transform(self):
        self.assertEqual(Avr().collect(2, 3), 5)
        self.assertAlmostEqual(Avr().collect(0.4, 0.8), 1.2)

    def test_report(self):
        self.assertEqual(Avr().report(3, 34), 34 / 3)
        self.assertEqual(Avr().report(3, 3.4), 3.4 / 3)
        self.assertEqual(Avr().report(0, 3.4), 3.4)


class Test_Nth(unittest.TestCase):
    def test_repr(self):
        self.assertEqual(Nth().__repr__(), 'Nth')

    def test_transform(self):
        self.assertIsNotNone(Nth().collect(2, 3))

    def test_report(self):
        self.assertEqual(Nth().report(3, 34), -1)
        self.assertEqual(Nth().report(3, 3.4), -1)


class Test_HttpressReportCollector(unittest.TestCase):
    def test_init(self):
        obj = HttpressReportCollector()
        self.assertEqual(obj.lines, [])
        self.assertEqual(obj.count, 0)

    def test_set(self):
        lines1 = [(1, 2, 0.4), (0.5, 2)]
        lines1_ = copy.deepcopy(lines1)

        obj = HttpressReportCollector()

        obj_set = obj.set(5, lines1)

        self.assertEqual(obj_set.count, 5)
        self.assertEqual(obj_set.lines, lines1_)

        self.assertEqual(obj.count, 5)
        self.assertEqual(obj.lines, lines1_)

        lines2 = [(5, 1, 0.5, 2)]
        lines2_ = copy.deepcopy(lines2)
        obj.set(1, lines2)

        self.assertEqual(obj.count, 1)
        self.assertEqual(obj.lines, lines2_)

    def test_eq(self):
        obj1 = HttpressReportCollector()
        obj2 = HttpressReportCollector()
        report = HttpressReport()

        self.assertEqual(obj1, obj2)
        self.assertEqual(obj1, report)

        lines = [(1, 2, 0.4), (0.5, 2)]
        obj1.lines = obj2.lines = report.lines = lines
        obj1.count = obj2.count = 5

        self.assertEqual(obj1, obj2)
        self.assertEqual(obj1, report)

        self.assertNotEqual(obj1, 'HttpressReport')

        self.assertNotEqual(obj1, HttpressReportCollector().set(6, lines))
        self.assertNotEqual(obj1, HttpressReportCollector().set(4, lines))
        self.assertNotEqual(obj1, HttpressReportCollector().set(5, lines + [(1, 2)]))
        self.assertNotEqual(obj1, HttpressReportCollector().set(5, lines[1:2]))
        self.assertNotEqual(obj1, HttpressReportCollector().set(5, [(1, 2, 0.4), (0.6, 2)]))

        self.assertNotEqual(obj1, HttpressReport().set(lines + [(1, 2)]))
        self.assertNotEqual(obj1, HttpressReport().set(lines[1:2]))
        self.assertNotEqual(obj1, HttpressReport().set([(1, 2, 0.4), (0.6, 2)]))

    def test_repr(self):
        obj = HttpressReportCollector()
        obj.set(36, [(1, 2, 0.4), (0.5, 2)])
        expected_repr = ('HttpressReportCollector( count = 36,\n'
                         '\t(1, 2, 0.4),\n'
                         '\t(0.5, 2),\n'
                         ')')
        self.assertEqual(obj.__repr__(), expected_repr)

    def test_report(self):
        # functors = (
        #     (Sum(), Sum(), Sum(), Sum(), Sum(), Sum()),
        #     (Sum(), Nth(), Sum(), Nth()),
        #     (Avr(), Avr(), Sum(), Sum()),  # by SPEC it should be (Nth(), Nth(), Sum(), Sum())
        #     (Nth(), Avr(), Sum(), Avr()),  # by SPEC it should be (Nth(), Nth(), Sum(), Avr())
        #     (Sum(), Sum(), Max(), Sum())
        # )

        collector_lines = [
            (400, 400, 399, 1, 20, 20),
            (299, 100.0, 0, 0.0),
            (56139, 1034, 11171738, 412921),
            (2.026, 198, 11110, 100.5),
            (200, 1, 2.026, 199.029)
        ]

        report_lines = [
            (400, 400, 399, 1, 20, 20),
            (299, -1.0, 0, -1.0),
            (56139 / 5, 1034 / 5, 11171738, 412921),
            (-1.0, 198 / 5, 11110, 100.5 / 5),
            (200, 1, 2.026, 199.029)
        ]

        # report_lines = [
        #     (400 * 5, 400 * 5, 399 * 5, 1 * 5, 20 * 5, 20 * 5),
        #     (299 * 5, -1.0, 0 * 5, -1.0),
        #     (56139, 1034, 11171738 * 5, 412921 * 5),
        #     (-1.0, 198, 11110 * 5, 100.5),
        #     (200 * 5, 1 * 5, 2.026, 199.029 * 5)
        # ]

        collector = HttpressReportCollector().set(5, collector_lines)
        report = collector.report()

        self.assertEqual(report.lines, report_lines)

    def test_collect(self):
        # functors = (
        #     (Sum(), Sum(), Sum(), Sum(), Sum(), Sum()),
        #     (Sum(), Nth(), Sum(), Nth()),
        #     (Avr(), Avr(), Sum(), Sum()),  # by SPEC it should be (Nth(), Nth(), Sum(), Sum())
        #     (Nth(), Avr(), Sum(), Avr()),  # by SPEC it should be (Nth(), Nth(), Sum(), Avr())
        #     (Sum(), Sum(), Max(), Sum())
        # )

        report_lines = [
            (400, 400, 399, 1, 20, 20),
            (299, 100.0, 0, 0.0),
            (56139, 1034, 11171738, 412921),
            (2.026, 198, 11110, 100.5),
            (200, 1, 2.026, 199.029)
        ]

        collector_lines = [
            (400 * 5, 400 * 5, 399 * 5, 1 * 5, 20 * 5, 20 * 5),
            (299 * 5, -1.0, 0 * 5, -1.0),
            (56139, 1034, 11171738 * 5, 412921 * 5),
            (-1.0, 198, 11110 * 5, 100.5),
            (200 * 5, 1 * 5, 2.026, 199.029 * 5)
        ]

        report = HttpressReport().set(report_lines)

        collector = HttpressReportCollector()
        for i in range(5):
            collector.collect(report)

        final_report = collector.report()
        self.assertEqual(final_report.lines, collector_lines)


#========================
if __name__ == '__main__':  # pragma: no cover
    unittest.main(exit=False, failfast=False)
