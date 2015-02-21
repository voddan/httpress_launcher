#!/usr/bin/python
# coding=utf-8
# re_debug.py
#
import re

__author__ = 'voddan'
__package__ = None

rtext = """
TOTALS:  150 connect, 150 requests, 150 success, 0 fail, 1 (1) real concurrency
RESPONSE: 2xx 150 (100.0%), non-2xx 0 (0.0%)
TRAFFIC: 14590 avg bytes, 280 avg overhead, 2188500 bytes, 42000 overhead
TIMING:  9.987 seconds, 15 rps, 218 kbps, 66.6 ms avg req time
loops: 150; failed: 0; time: 9.987; rate: { 15.020 } req/sec;
"""

ltext = """
TOTALS:  85 connect, 85 requests, 85 success, 0 fail, 1 (1) real concurrency
RESPONSE: 2xx 0 (0.0%), non-2xx 85 (100.0%)
302 -         85  100.0%

TRAFFIC: 0 avg bytes, 161 avg overhead, 0 bytes, 13685 overhead
TIMING:  10.007 seconds, 8 rps, 1 kbps, 117.7 ms avg req time
loops: 85; failed: 85; time: 10.007; rate: { 8.494 } req/sec;
"""

ttext = """
TOTALS:  85 connect, 85 requests, 85 success, 0 fail, 1 (1) real concurrency
RESPONSE: 2xx 0 (0.0%), non-2xx 85 (100.0%)
302 -         85  100.0%
TRAFFIC: 0 avg bytes, 161 avg overhead, 0 bytes, 13685 overhead
TIMING:  10.007 seconds, 8 rps, 1 kbps, 117.7 ms avg req time
loops: 85; failed: 85; time: 10.007; rate: { 8.494 } req/sec;
"""

text = rtext

expression = \
    (r'^TOTALS:  (\d+) connect, (\d+) requests, (\d+) success, (\d+) fail, (\d+) \((\d+)\) real concurrency$\s^[\s\S]*'
     r'^RESPONSE: 2xx (\d+) \((\d+\.\d+)%\), non-2xx (\d+) \((\d+\.\d+)%\)$\s^[\s\S]*'
     r'^TRAFFIC: (\d+) avg bytes, (\d+) avg overhead, (\d+) bytes, (\d+) overhead$\s^[\s\S]*'
     r'^TIMING:  (\d+\.\d+) seconds, (\d+) rps, (\d+) kbps, (\d+\.\d+) ms avg req time$\s^[\s\S]*'
     r'^loops: (\d+); failed: (\d+); time: (\d+\.\d+); rate: \{ (\d+\.\d+) \} req/sec')

pattern = re.compile(expression, re.MULTILINE)
match = pattern.search(text)

print match
print match.groups()