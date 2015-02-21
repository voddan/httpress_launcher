#!/usr/bin/python
# coding=utf-8
# optparse_version~comline.py
#
__author__ = 'voddan'
__package__ = None

from optparse import OptionParser
def optparse_parse_args(environment, args=None, values=None):
    """
    Parses command line arguments, equivalent to optparse.parse_args(args, values)

    :type environment: Environment
    :rtype: (Values, list)
    """
    parser = OptionParser(version=environment.version, add_help_option=False)

    parser.add_option("--script-help", action="help",
                      help="show this help message and exit")

    parser.add_option("--hosts", dest="hosts_string", metavar="HOSTS",
                      help="list of HOSTS", default='')

    parser.add_option("-f", "--file", dest="filename", metavar="FILE",
                      help="read host options from FILE")

    parser.add_option("-v", "--verbose", action="store_true", dest="verbose",
                      help="turn logging.INFO on", default=False)

    return parser.parse_args(args, values)
pass