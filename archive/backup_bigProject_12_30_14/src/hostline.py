# coding=utf-8
# hostline.py
#
__author__ = 'voddan'
__package__ = None

import re

from common import Environment
from common import Comparable


class Host(Comparable):
    """
    Contains information about launching one particular instance of httpress bin
    such ass system and connection logging information
    """
    def __init__(self, login, password, hostname):
        """
        :type login: str
        :type password: str | Environment.SHHKEY
        :type hostname: str
        """
        self.login = login
        self.password = password
        self.hostname = hostname

    def __eq__(self, other):
        """
        :type other: Host
        :rtype: bool
        """
        return isinstance(other, Host) and \
               self.login == other.login and \
               self.password == other.password and \
               self.hostname == other.hostname

    def __repr__(self):
        return 'Host(%s, %s, %s)' % \
               (self.login, str(self.password), self.hostname)


class LocalHost(Host, Comparable):
    """
    Special case of launching tests on the local machine
    Does not require login or password
    Should always be treated as a special case
    """
    def __init__(self):
        Host.__init__(self, '', '', 'localhost')
        # in order to support '__eq__(Host(..), LocalHost()) == False'
        self.login = None
        self.password = None

    def __eq__(self, other):
        """
        :type other: Host
        """
        return isinstance(other, LocalHost)

    def __repr__(self):
        return 'LocalHost'


def parse_host_lines(environment, host_lines):
    """
    Parses a list of hostname string representations

    :type environment: Environment
    :type host_lines: list[str]
    :rtype: list[Host]
    """

    # not sure about characters which are allowed in passwords
    # used 'http://goo.gl/jtsM9v' (IBM): r'[\w!\)\(-.?\]\[`~]'
    # also consider 'http://goo.gl/9QfGvt': r'[^ \s"\'`&\)\(><|:]'
    password_characters = r'[\w!\)\(-.?\]\[`~]'
    hostname_characters = r'[a-zA-Z0-9_-]'
    # IPv6 is not supported

    expr_user = r'(?P<login>\w+)@'
    expr_pass = r'(?P<password>(%s)+):' % password_characters
    expr_host_ipv4 = r'\d+\.\d+\.\d+\.\d+'
    expr_host_name = r'((%s)+\.)*(%s)+' % (hostname_characters, hostname_characters)
    expr_host = r'(?P<hostname>(%s)|(%s))' % (expr_host_ipv4, expr_host_name)

    expression = r'^(%s)?(%s)?(%s)$' % (expr_user, expr_pass, expr_host)
    pattern = re.compile(expression)

    hosts = []
    for line in host_lines:
        clean_line = line.strip()
        if clean_line == '':
            # we do not need warning messages on empty lines
            continue

        match = pattern.match(clean_line)
        if not match:
            environment.warning("Host line '%s' has incorrect format" % clean_line)
            continue

        login = match.group('login')
        password = match.group('password')
        hostname = match.group('hostname')

        # it fits 'localhost' in any font-case
        if hostname.lower() == 'localhost':
            hosts.append(LocalHost())
            if login or password:
                environment.warning("Attributes are ignored for localhost in '%s'" % clean_line)
        else:
            if not login:
                login = environment.default_user
            if not password:
                password = environment.default_password

            hosts.append(Host(login, password, hostname))

    return hosts
