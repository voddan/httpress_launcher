#!/usr/bin/python
# coding=utf-8
__author__ = 'voddan'
__package__ = None

import os
import time

info_msg_list = [
    "25 requests launched",
    "50 requests launched",
    "75 requests launched",
    "100 requests launched"]

test_answer = """
TOTALS:  400 connect, 400 requests, 399 success, 1 fail, 20 (20) real concurrency
RESPONSE: 2xx 299 (100.0%), non-2xx 0 (0.0%)
TRAFFIC: 56139 avg bytes, 1034 avg overhead, 11171738 bytes, 412921 overhead
TIMING:  2.026 seconds, 198 rps, 11110 kbps, 100.5 ms avg req time
loops: 200; failed: 1; time: 2.026; rate: { 199.029 } req/sec;"""

help_msg = """httpress <options> <url>
  -d lvl    debug level (max is 2) (default: 0)
  -n num    number of requests     (default: no)
  -t sec    number of seconds to run, -n option has higher priority (default: 10)
  -i ipaddr makes the program to send request without resolving, using specified IP address (default: no)
  -p num    number of threads      (default: 1)
  -c num    concurrent connections (default: 1)
  -k        keep alive             (default: no)
  -q        no progress indication (default: no)
  -x regexp look for regular expression, example:
            "Page \d" - will look for expressions like "Page 1", "Page 2", etc
  -z pri    GNUTLS cipher priority (default: NORMAL)
  -h        show this help
  -r range  range of urls, {} inside of url will be replaced with numbers from the range (default: no)
  -V        show version

examples: httpress -n 10000 -c 100 -p 4 -k http://localhost:8080/index.html
          httpress -n 10000 -c 100 -p 4 -k http://domain{}.localdomain/index.html -r 1-16
"""

args = os.sys.argv[1:]

if not args:
    print "Test time is set to 10 seconds.\nmissing url argument\n"
    print help_msg
    exit(1)
elif '-h' in args or '-help' in args:
    print help_msg
    # exit(0)
elif '--help' in args:
    # TODO: fix the typo :)
    print 'unkown option: --\n'
    print help_msg
    exit(1)
else:
    for msg in info_msg_list:
        time.sleep(0.5)
        print msg

    print test_answer
    # exit(0)