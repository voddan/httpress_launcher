# coding=utf-8
#
# common.py
#
__author__ = 'voddan'
__package__ = None
from common import __version__

import subprocess

# <editor-fold desc="COMMAND LINE OPTIONS SPEC">
#
#   1) --hosts user1@pass1:hostname1,user2@hostname2,hostname3,hostname4
#
#   где
#   user - имя пользователя, если не укзано, то root
#   pass - пароль, если не указан, то используем ssh ключ
#   hostname - имя хоста или IP адрес
#
#   список хостов разделён запятыми
#
#   2) -f /tmp/hosts | --file /tmp/hosts
#
#   где /tmp/hosts - файл со списком хостов в таком формате
#   ...
#   user1@pass1:hostname1
#   user@hostname2
#   hostname3
#   ...
#
#   где user, pass, hostname - такие же как и в случае с --hosts XXX
#
#   3) -v | --verbose
#
#   при наличии этой опции включается logging.INFO
#
#       logging.basicConfig(logging.INFO if opts.verbose else logging.ERROR)
#
#   4) все остальные опции передаются утилите httpress как есть
#
# </editor-fold>

from argparse import ArgumentParser
from common import Environment
from common import Comparable
import logging

class HttpressComLine(Comparable):
    """
    Class to keep data form ComLine which is needed for the main program
    """
    def __init__(self, host_line_list, filename_list, parameters_to_pass):
        """
        :type host_line_list: list[str]
        :type filename_list: list[str]
        :type parameters_to_pass: list[str]
        """
        self.host_line_list = host_line_list
        self.filename_list = filename_list
        self.parameters_to_pass = parameters_to_pass

    def __eq__(self, other):
        """
        :type other: HttpressComLine
        :rtype: bool
        """
        return self.host_line_list == other.host_line_list and \
               self.filename_list == other.filename_list and \
               self.parameters_to_pass == other.parameters_to_pass

    def __repr__(self):
        return 'HttpressComLine(%s; %s; %s)' % \
               (self.host_line_list, self.filename_list, self.parameters_to_pass)


def httpress_get_help_msg(environment):
    """
    Lunches httpress bin (environment.httpress_bin_path) and returns its help message

    Note:
        option '-h' must mean 'show help' for 'httpress'

    :param environment: Environment
    :rtype: str
    """
    try:
        child = subprocess.Popen([environment.httpress_bin_path, '-h'],
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)

        (child_out, child_err) = child.communicate()

        if child_err != '':
            # should be cached inside the method
            raise RuntimeError
    except:
        environment.error("Help message of %s can't be get. "
                          "Try '%s -h'" %
                          ((environment.httpress_bin_path,) * 2))
        return "HELP MESSAGE CAN NOT BE DISPLAYED"

    return child_out

def argparse_parse_args(environment, comline_arguments=None, comline_values=None):
    """
    Parses command line arguments, options equivalent to argparse.parse_args(args, values)

    Note:
        option '--help' must be unused by 'httpress'
        option '-h' must mean 'show help' for 'httpress'

    :type environment: Environment
    :type comline_values: dict[str,str]
    :type comline_arguments: list[str]
    :rtype: HttpressComLine
    """
    parser = ArgumentParser(add_help=False)

    # option '--help' must be unused by httpress bin
    parser.add_argument('--help', action='store_true', dest='run_script_help',
                        help="show help messages both for the script and for the 'httpress', then exit", default=False)

    # option '-h' must mean 'show help' for httpress bin
    parser.add_argument('-h', action='store_true', dest='run_httpress_help',
                        help="show 'httpress' help messages", default=False)

    # no warning message on multi hosts
    parser.add_argument("--hosts", dest="hosts_string_list", metavar="HOSTS", action="append", type=str,
                        help="list of HOSTS in format [login@][password:](IPv4|host_name) or 'localhost'", default=[])

    parser.add_argument("-f", "--file", dest="filename_list", metavar="FILE", action="append", type=str,
                        help="read host options from FILE in addition to HOSTS", default=[])

    parser.add_argument("-v", "--verbose", action="store_true", dest="verbose",
                        help="logging level to logging.INFO", default=False)

    # debugging options: undocumented, no unit-tests
    parser.add_argument("--script-debug", action="store_true", dest="script_debug",
                        help="logging level to logging.DEBUG", default=False)

    (arguments, parameters_to_pass) = parser.parse_known_args(comline_arguments, comline_values)

    if not comline_arguments and not comline_values:
        environment.error("Command line is empty. Nothing to do.")
        exit()

    if arguments.run_script_help:
        parser.print_help(environment.text_stream)
        environment.text("VERSION: %s" % __version__)
        environment.text('=' * 40)
        environment.text(httpress_get_help_msg(environment))
        exit()

    if arguments.run_httpress_help:
        environment.text(httpress_get_help_msg(environment))
        exit()

    host_list = []
    for hosts_string in arguments.hosts_string_list:
        if hosts_string != '':
            host_list.extend(hosts_string.split(','))

    if (arguments.filename_list is not None) and len(arguments.filename_list) > 1:
        environment.warning("More than one --file/-f arguments are provided. "
                                   "Content is taken from all sources: %s" %
                                   str(arguments.filename_list))

    if arguments.verbose:
        environment.set_logging_level(logging.INFO)
    else:
        environment.set_logging_level(logging.ERROR)

    # Makes sense to have INFO level to debug concurrency and SSH
    # add unit-tests
    if arguments.script_debug:  # pragma: no cover
        environment.set_logging_level(logging.DEBUG)

    return HttpressComLine(host_list,
                           arguments.filename_list,
                           parameters_to_pass)
