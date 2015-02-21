#!/usr/bin/python
# coding=utf-8
# httpress_launcher.py
# Lunches external bin 'httpress' (httpress_rh6)
#
from itertools import izip
import os
import re
import socket
import stat
import string
import subprocess
import time
import sys
import logging
from argparse import ArgumentParser
import paramiko
import platform
import traceback

class BinPath:
    """
    :type _list: [BinPath]
    :type _local: str | None
    """
    _list = []
    _local = None

    def __init__(self, path):
        """ :except EnvironmentError, subprocess.CalledProcessError, AssertionError """
        path = path.strip()
        assert os.access(path, os.R_OK)
        hash = subprocess.check_output(['set -- $(md5sum "%s"); echo $1' % path], shell=True)[:-1]
        self.path = path
        self.hash = hash.strip()

    @staticmethod
    def init(paths):
        """
        Sets up (local) paths to bin httpress for different systems.
        Must be called exactly ones

        :type paths: list[str]
        """
        assert not BinPath._list
        for path in paths:
            try:
                BinPath._list.append(BinPath(path))
            except (AssertionError, EnvironmentError, subprocess.CalledProcessError):
                logging.error("Path '%s' is unavailable. Make sure you have permissions for reading" % path)

        if not BinPath._list:
            logging.error(traceback.format_exc())  # stacktrace for BinPath.__init__
            raise Exception('No valid path were provided')

    @staticmethod
    def path(hash):
        """
        Returns path to a local bin or None if nothing matches.
        Note: 'hash' is being striped

        :type hash: str
        :rtype: str | None
        """
        hash = hash.strip()
        for binpath in BinPath._list:
            if hash == binpath.hash:
                return binpath.path
        return None

    @staticmethod
    def paths():
        """ :rtype: generator(str) """
        return (binpath.path for binpath in BinPath._list)

    @staticmethod
    def localpath():
        """ :rtype: str """
        if BinPath._local:
            return BinPath._local

        for binpath in BinPath._list:
            try:
                assert os.access(binpath.path, os.X_OK)
                subprocess.check_call([binpath.path, '-h'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            except (AssertionError, subprocess.CalledProcessError):
                continue
            BinPath._local = binpath.path
            return BinPath._local

        logging.error(traceback.format_exc())
        raise RuntimeError("Non of the given paths may run on LocalHost. Make sure you have permissions for execution"
                           "\nLinux distro: %s" % platform.linux_distribution())


def load_host_lines_from_single_file(filepath):
    """
    :type filepath: str
    :rtype: list[str]
    """
    try:
        file = open(filepath, 'r')
    except EnvironmentError as e:
        logging.error("File %s can't be open for reading \nERROR: %s %s" % (filepath, e.__class__.__name__, e))
        return []

    host_list = []
    try:
        host_list = file.readlines()
    except EnvironmentError as e:
        logging.error("Cannot read list of hosts from %s \nERROR: %s %s" % (filepath, e.__class__.__name__, e))
    finally:
        file.close()

    return host_list

def parse_host_lines(host_lines):
    """
    Parses a list of hostname string representations

    :type host_lines: list[str]
    :rtype: list[Host]
    """
    password_characters = r'[\w!\)\(-.?\]\[`~]'
    hostname_characters = r'[a-zA-Z0-9_-]'

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
        if clean_line == '' or clean_line[0] == '#':
            continue

        match = pattern.match(clean_line)
        if match is None:
            logging.error("Host line '%s' has incorrect format" % clean_line)
            continue

        login = match.group('login')
        password = match.group('password')
        hostname = match.group('hostname')

        if hostname.lower() == 'localhost':  # fits 'localhost' in any font-case
            hosts.append(LocalHost())
            if login or password:
                logging.warning("Attributes are ignored for localhost in '%s'" % clean_line)
        else:
            hosts.append(Host(login if login else "root",
                              password if password else None,  # open-private ssh key authentication
                              hostname))
    return hosts

class HttpressComLine:
    def __init__(self, host_line_list, filename_list, parameters_to_pass):
        """
        :type host_line_list: list[str]
        :type filename_list: list[str]
        :type parameters_to_pass: list[str]
        """
        self.host_line_list = host_line_list
        self.filename_list = filename_list
        self.parameters_to_pass = parameters_to_pass

def httpress_get_help_msg():
    """ :rtype: str """
    path = BinPath.localpath()
    try:
        # option '-h' must mean 'show help' for 'httpress'
        return subprocess.check_output([path, '-h'])  # subprocess.stderr goes to stderr
    except subprocess.CalledProcessError:
        logging.error("Help message of %s can't be get. Try '%s -h'" % (path, path))
        logging.error(traceback.format_exc())
        return "HELP MESSAGE CAN NOT BE DISPLAYED"

def argparse_parse_args(comline_arguments=None, comline_values=None):
    """
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

    parser.add_argument("--hosts", dest="hosts_string_list", metavar="HOSTS", action="append", type=str,
                        help="list of HOSTS in format [login@][password:](IPv4|host_name) or 'localhost'", default=[])

    parser.add_argument("-f", "--file", dest="filename_list", metavar="FILE", action="append", type=str,
                        help="read host options from FILE in addition to HOSTS", default=[])

    parser.add_argument("-v", "--verbose", action="store_true", dest="verbose",
                        help="set logging level to logging.INFO, print backtraces on errors", default=False)

    (arguments, parameters_to_pass) = parser.parse_known_args(comline_arguments[1:], comline_values)

    if not comline_arguments[1:] and not comline_values:
        logging.error("Command line is empty. Nothing to do.")
        parser.print_help(sys.stdout)
        exit()

    if arguments.run_script_help:
        parser.print_help(sys.stdout)
        print ('=' * 40)
        print (httpress_get_help_msg())
        exit()

    if arguments.run_httpress_help:
        print httpress_get_help_msg()
        exit()

    host_list = []
    for hosts_string in arguments.hosts_string_list:
        if hosts_string != '':
            host_list.extend(hosts_string.split(','))

    if (arguments.filename_list is not None) and len(arguments.filename_list) > 1:
        logging.info("More than one --file/-f argument is provided. "
                     "Content is taken from all sources: %s" % arguments.filename_list)

    logging.getLogger().setLevel(logging.INFO if arguments.verbose else logging.ERROR)

    return HttpressComLine(host_list, arguments.filename_list, parameters_to_pass)


def ssh_test(client, path, args, timeout=None):
    """
    :type client: paramiko.SSHClient
    :type path: str
    :type args: str
    :rtype: bool
    :except IOError, SSHException, RuntimeError
    :raises AssertionError
    """
    assert not [a for a in args if a not in string.ascii_letters]
    for arg in args:
        output = client.exec_command('test -%s %s; echo $?' % (arg, path), timeout=timeout)
        out = output[1].read()
        res = int(out)
        if res == 2 or output[2].read():
            raise RuntimeError("Cannot test file %s with arguments %s" % (path, arg))
        if res == 1:
            return False
    return True

class Host:
    TIMEOUT = 5  # timeout for every remote operation

    def __init__(self, login, password, hostname):
        """
        :type login: str
        :type password: str | SHHKEY
        :type hostname: str
        """
        self.login = login
        self.password = password
        self.hostname = hostname

        self.start_time = None
        self.stdout = None
        self.stderr = None

        # for Host instances only
        self.client = None

    def __repr__(self):
        return 'Host(%s, %s, %s)' % (self.login, self.password, self.hostname)

    def prepare(self):
        """
        connects to host, loads 'httpress' bin, initialises 'client' in the host
        Note: may be slow, but it does not affect the second launch because of the cashing

        :except BadHostKeyException, AuthenticationException, SSHException, socket.error, RuntimeError, EnvironmentError
        :raises AssertionError
        """
        dirpath = "/tmp/httpress_launcher/"
        exepath = "/tmp/httpress_launcher/httpress"
        self.exepath = exepath  # used in Host.launch

        client = paramiko.SSHClient()
        self.client = client
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        client.connect(hostname=self.hostname, username=self.login, password=self.password, timeout=Host.TIMEOUT)
        sftp = client.open_sftp()

        if not ssh_test(client, dirpath, 'e', Host.TIMEOUT):
            sftp.mkdir(dirpath, 0777)
        elif not ssh_test(client, dirpath, 'drwx', Host.TIMEOUT):
            # if we use another path there is no way to cash the loaded files
            raise RuntimeError("Unable to use remote path %s. Make sure you have R, W, X permissions" % dirpath)

        if ssh_test(client, exepath, 'frx', Host.TIMEOUT):
            hash = client.exec_command('set -- $(md5sum "%s"); echo $1' % exepath, timeout=Host.TIMEOUT)[1].read()
            path = BinPath.path(hash)
            if path is not None:
                err = client.exec_command('%s -h' % exepath)[2].read()
                if err == '':
                    sftp.close()
                    return

        if ssh_test(client, exepath, 'e', Host.TIMEOUT):
            logging.error("Rewriting httpress on %s" % self)
            try:
                output = client.exec_command('rm -fr %s' % exepath, timeout=Host.TIMEOUT)  # may fail
                assert not output[2].read()
            except (AssertionError, IOError):
                raise RuntimeError("Unable to use remote path %s. Make sure to delete it before relaunching" % exepath)

        logging.info("Trying to fit an httpress in %s" % self)
        for path in BinPath.paths():
            sftp.put(path, exepath)
            sftp.chmod(exepath, 0777)  # i am the owner

            err = client.exec_command('%s -h' % exepath)[2].read()
            if err == '':  # testing if the binary works
                sftp.close()
                return

        try:
            distro = client.exec_command('python -c "import platform; print platform.linux_distribution()"')
            distro_info = "\nLinux distro: %s" % distro[1].read()
        except (paramiko.SSHException, IOError):
            distro_info = ''

        raise RuntimeError("Non of the given files can be run at %s %s" % (self, distro_info))

    def launch(self, args):
        """
        Supposed to work as fast as possible

        :type args: list[str]
        :except SSHException
        :raises AssertionError
        """
        assert self.client  # must have been set in 'prepare'
        self.start_time = time.time()

        assert self.exepath  # must be declared in Host.prepare
        logging.info("launching %s at time[sec]: %f" % (self, self.start_time))
        (_, self.stdout, self.stderr) = self.client.exec_command(self.exepath + ' ' + ' '.join(args))

    def output(self):
        """
        :except EnvironmentError
        :raises AssertionError
        """
        assert self.stdout  # must have been set in 'launch'
        assert self.stderr  # must have been set in 'launch'
        out = self.stdout.read()
        err = self.stderr.read()
        return Output(self, out, err)

    def close(self):
        """ Should work after 'prepare', 'launch' and 'output' regardless any Exceptions """
        if self.client is not None:
            self.client.close()

class LocalHost(Host):
    def __init__(self):
        Host.__init__(self, None, None, 'localhost')

    def __repr__(self):
        return 'LocalHost'

    def prepare(self):
        assert BinPath.localpath()

    def launch(self, args):
        comline_list = [BinPath.localpath()] + args
        self.start_time = time.time()
        logging.info("launching LocalHost at time[sec]: %f" % self.start_time)
        child = subprocess.Popen(comline_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        assert child
        self.stdout = child.stdout
        self.stderr = child.stderr

    def close(self):
        pass

class Output:
    def __init__(self, host, out, err):
        """
        Note: Output.out and Output.err have been stripped

        :type host: Host
        :type out: str
        :type err: str
        """
        self.host = host
        self.out = out.strip()
        self.err = err.strip()
        self.start_time = host.start_time if host.start_time else 0  # the host was never launched

    @staticmethod
    def error(host, msg, error):
        """
        Returns an Output(err= 'msg' + 'error', out= traceback)

        :type host: Host
        :type msg: str
        :type error: Exception
        :rtype Output
        """
        return Output(host, traceback.format_exc(), '%s\n%s' % (msg, error.message))

class HttpressReport:
    """ Data class for parsing and keeping the stdout of 'httpress' """
    NUMBER_OF_VALUES = 22

    def __init__(self):
        self.values = []

    def parse(self, text):
        """
        Parsers text and fulls up the self instance, then returns it

        :type text: str
        :rtype: HttpressReport
        :except RuntimeError
        """
        self.values = []

        expression = \
            (r'^TOTALS:  (\d+) connect, (\d+) requests, (\d+) success, (\d+) fail, (\d+) \((\d+)\) real concurrency$\s'
             r'^RESPONSE: 2xx (\d+) \((\d+\.\d+)%\), non-2xx (\d+) \((\d+\.\d+)%\)$\s^[\s\S]*'
             r'^TRAFFIC: (\d+) avg bytes, (\d+) avg overhead, (\d+) bytes, (\d+) overhead$\s^[\s\S]*'
             r'^TIMING:  (\d+\.\d+) seconds, (\d+) rps, (\d+) kbps, (\d+\.\d+) ms avg req time$\s^[\s\S]*'
             r'^loops: (\d+); failed: (\d+); time: (\d+\.\d+); rate: \{ (\d+\.\d+) \} req/sec')

        pattern = re.compile(expression, re.MULTILINE)
        match = pattern.search(text)
        if match is None:
            raise RuntimeError("Unable to parse the text")

        for string in match.groups():
            try:
                self.values.append(int(string))
            except ValueError:
                self.values.append(float(string))
                # nothing else may be get because the expression collects only digits (with dots)

        return self

class HttpressReportCollector:
    """ Collects data from HttpressReports one by one, prints a formatted report by the report() method """
    class Functor:
        def __init__(self, name, collect_f, report_f):
            self.__repr__ = lambda: name
            self.collect = collect_f  # updated_value   = collect(old_value, new_value)
            self.report = report_f    # value_to_report = report(count: int, value)

    sum = Functor('Sum', (lambda a, b: a + b), (lambda c, v: v))
    max = Functor('Max', (lambda a, b: max(a, b)), (lambda c, v: v))
    avr = Functor('Avr', (lambda a, b: a + b), (lambda c, v: (v / c) if c else v))
    nth = Functor('Nth', (lambda a, b: 0), (lambda c, v: -1))  # report_f must return value less than zero

    functors = (
        sum, sum, sum, sum, sum, sum,
        sum, nth, sum, nth,
        avr, avr, sum, sum,  # by SPEC it should be: nth, nth, sum, sum,
        nth, avr, sum, avr,  # by SPEC it should be: nth, nth, sum, avr,
        sum, sum, max, sum
    )
    # fixme: what is the meaning of 'Timing: 2.0026 sec'?

    def __init__(self):
        assert len(HttpressReportCollector.functors) == HttpressReport.NUMBER_OF_VALUES
        self.count = 0
        self.values = []

    def collect(self, report):
        """
        Collects one HttpressReport

        :type report: HttpressReport
        """
        functors = HttpressReportCollector.functors

        if self.count:
            new_values = [functor.collect(self_value, value)
                          for functor, self_value, value in izip(functors, self.values, report.values)]
        else:
            new_values = report.values

        self.values = new_values
        self.count += 1

    def report(self):
        """
        Returns a formatted report or None if no reports were collected

        :except HttpressReport.EmptyReportError
        :rtype str|None
        """
        if len(self.values) == 0:
            return None

        assert len(self.values) == HttpressReport.NUMBER_OF_VALUES
        functors = HttpressReportCollector.functors

        report_values = [functor.report(self.count, value)
                         for functor, value in izip(functors, self.values)]

        values = [x for x in report_values if x >= 0]
        assert len(values) == HttpressReport.NUMBER_OF_VALUES - functors.count(HttpressReportCollector.nth)
        result = \
            ('TOTALS:  %d connect, %d requests, %d success, %d fail, %d (%d) real concurrency\n'
             'RESPONSE: 2xx %d (--%%), non-2xx %d (--%%)\n'
             'TRAFFIC: %d avg bytes, %d avg overhead, %d bytes, %d overhead\n'
             'TIMING:  -- seconds, %d rps, %d kbps, %.1f ms avg req time\n'
             'loops: %d; failed: %d; time: %.3f; rate: { %.3f } req/sec;'
             % tuple(values))

        return result

def launching(hosts, args):
    """
    Launches executable 'bin_path' with 'args' on 'hosts'
    and prints the outputs interactively.
    Returns output strings from successful launches

    :type hosts: list[Host]
    :type args: list[str]
    :rtype: list[HttpressReport]
    """
    logging.info("hosts to launch: %s" % hosts)

    failed_list = []  # outputs from all hosts which have failed for different reasons

    connected_hosts = []
    for host in hosts:
        try:
            host.prepare()
            connected_hosts.append(host)
            print 'Ready to launch %s' % host
        except (paramiko.BadHostKeyException, paramiko.AuthenticationException,
                paramiko.SSHException, socket.error, RuntimeError, EnvironmentError) as e:
            failed_list.append(Output.error(host, 'Cannot prepare %s' % host, e))
            logging.error('Cannot prepare %s \nERROR: %s %s' % (host, e.__class__.__name__, e))

    launched_hosts = []
    for host in connected_hosts:
        try:
            host.launch(args)
            launched_hosts.append(host)
        except paramiko.SSHException as e:
            failed_list.append(Output.error(host, 'Cannot launch %s' % host, e))
            logging.error('Cannot launch %s \nERROR: %s %s' % (host, e.__class__.__name__, e))

    successful_list = []
    for host in launched_hosts:
        try:
            output = host.output()
            if output.err:
                failed_list.append(output)
            else:
                successful_list.append(output)
        except EnvironmentError as e:
            failed_list.append(Output.error(host, 'Cannot get output from %s' % host, e))

    for host in hosts:
        try:
            host.close()
        except Exception as e:
            # no reason to halt the whole script after the we've got the information
            logging.error("Error on closing %s: %s %s" % (host, e.__class__.__name__, e))
            logging.error(traceback.format_exc())

    reports = []
    parsed_list = []
    for output in successful_list:
        try:
            report = HttpressReport()
            report.parse(output.out)
            reports.append(report)
            parsed_list.append(output)
        except RuntimeError as e:
            err_output = Output.error(output.host, 'Cannot parse the text from %s' % output.host, e)
            err_output.out = output.out  # initial output.out must be provided
            failed_list.append(err_output)

    for i, output in enumerate(parsed_list):
        print '===========%4d ============= at %s' % ((i + 1), output.host)
        print output.out, '\n'

    print '=== FAILED:         %4d =================' % len(failed_list)
    info_mode = (logging.getLogger().getEffectiveLevel() <= logging.INFO)
    for output in failed_list:
        if output.start_time > 0:
            print 'Task on %s at %f FAILED' % (output.host, output.start_time)
        else:
            print 'Task on %s FAILED TO BE RUN' % output.host

        print output.err
        if output.out and info_mode:
            print "''''\n%s\n'''" % output.out
        print  # an empty line after every message

    return reports


def main(comline_argv):
    options = argparse_parse_args(comline_argv)

    host_lines = options.host_line_list

    for filename in options.filename_list:
        logging.info('loading a hostlist from: %s' % filename)
        host_lines.extend(load_host_lines_from_single_file(filename))

    hosts = parse_host_lines(host_lines)

    # assuming LocalHost if no hosts are provided
    # if not hosts:
    #     hosts.append(LocalHost())

    report_list = launching(hosts, options.parameters_to_pass)

    collector = HttpressReportCollector()
    for report in report_list:
        collector.collect(report)

    print '=== LAUNCHED:       %4d =================' % len(hosts)
    print '=== SUCCESSFULLY:   %4d =================' % len(report_list)
    print '=========================================='

    report_str = collector.report()
    print report_str if report_str else 'no report'

#========================
if __name__ == '__main__':
    # BinPath.init(["bin/httpress_rh6", "bin/httpress_fc20", "bin/httpress_mock_slow_error.py"])
    # BinPath.init(["bin/httpress_mock_slow_error.py", "bin/httpress_rh6", "bin/httpress_fc20"])
    # BinPath.init(["bin/httpress_rh6", "bin/httpress_fc20"])

    BinPath.init(["httpress_rh6", "httpress_fc20", "httpress_mock_slow_error.py"])
    main(sys.argv)
