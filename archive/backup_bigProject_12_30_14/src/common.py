# coding=utf-8
# common.py
# Contains common classes and functions
#
__author__ = 'voddan'
__package__ = None

# VERSION FORMAT: ns.nr_mm.dd.yyyy
# ns - number of stage,
# nr - number of the last code revision
# mm.dd.yyyy - date of the last code revision
__version__ = '0.2_11.04.2014'

from abc import abstractmethod
import logging
import sys


class Comparable:  # pragma: no cover
    @abstractmethod
    def __eq__(self, other):
        pass

    def __ne__(self, other):
        return not self.__eq__(other)


# TODO: add access to different logging streams
# TODO: eliminate effect from logging level, collect ALL output
class Environment:
    # default const value for password
    class SHHKEY(Comparable):
        def __init__(self):
            pass

        def __repr__(self):
            return 'SHHKEY'

        def __eq__(self, other):
            return isinstance(other, Environment.SHHKEY)

    def __init__(self,
                 httpress_bin_path,
                 version,
                 default_user,
                 default_password,
                 logger,
                 text_stream):
        """
        :type httpress_bin_path: str
        :type version: str
        :type default_user: str
        :type default_password: str | SHHKEY

        :type logger: logging.Logger
        :type text_stream: Stream
        """
        self.httpress_bin_path = httpress_bin_path
        self.version = version

        self.default_user = default_user
        self.default_password = default_password

        self._logger = logger
        self.text_stream = text_stream

    # TODO: consider a better name
    # TODO: deal with exceptions
    # TODO: write unit-tests
    def text(self, msg):
        """
        Writing msg to text_stream

        :type msg: str
        """
        print >> self.text_stream, msg

    def text_chrs(self, msg):
        """
        Writing msg to text_stream
        without ending new line

        :type msg: str
        """
        self.text_stream.write(msg)

    def debug(self, msg):
        self._logger.debug(msg)

    def info(self, msg):
        """
        :type msg: str
        """
        self._logger.info(msg)

    def warning(self, msg):
        """
        :type msg: str
        """
        self._logger.warning(msg)

    def warn(self, msg):
        """
        :type msg: str
        """
        self._logger.warn(msg)

    def error(self, msg):
        """
        :type msg: str
        """
        self._logger.error(msg)

    def critical(self, msg):
        """
        :type msg: str
        """
        self._logger.critical(msg)

    def set_logging_level(self, level):
        """
        :type level: int
        """
        self._logger.setLevel(level)

    def get_logging_level(self):
        """
        :rtype: int
        """
        return self._logger.getEffectiveLevel()


class GlobalEnvironment(Environment):
    SHHKEY = Environment.SHHKEY

    # TODO: write unit tests
    # TODO: add custom err and out streams
    def __init__(self,
                 httpress_bin_path,
                 version,
                 default_user='root',
                 default_password=SHHKEY(),

                 logger=logging.getLogger('root'),
                 logger_filename=None,
                 logger_level=logging.WARNING):
        """
        MUST NOT be used in unit tests!
        Use test.helper.TestingEnvironment for testing
        If you use GlobalEnvironment with other tests,
        please ensure that non of the environments
        has logger=logging.getLogger('root') option

        :type httpress_bin_path: str
        :type version: str
        :type default_user: str
        :type default_password: str | SHHKEY

        :type logger: logging.Logger
        :type logger_filename: str
        :type logger_level: int
        """
        # TODO: we do not need this here, delete after debugging
        self._logger_out_stream = sys.stdout
        self._logger_err_stream = sys.stderr

        Environment.__init__(self, httpress_bin_path, version,
                                 default_user, default_password,
                                 logger, self._logger_out_stream)

        logger_basic_config(self._logger,
                            logger_filename,
                            logger_level,
                            self._logger_out_stream,
                            self._logger_err_stream)


# TODO: write unit-tests
class ExactLevelFilter(logging.Filter):
    def __init__(self, level_list):
        """
        :type level_list: list[int]
        """
        logging.Filter.__init__(self, '')
        self.level_list = level_list

    def filter(self, record):
        """
        :type record: LogRecord
        """
        return record.levelno in self.level_list


def load_host_lines_from_single_file(filename):
    """
    :type filename: str
    :rtype: list[str]
    """
    try:
        f = open(filename)
    except IOError:
        logging.warning("File %s can't be open for reading" % filename)
        # TODO: should be another (module-level) logger
        return []

    host_list = []

    try:
        for line in f:
            host_list.append(line)
    except IOError:
        logging.warning("List of hosts from %s may be incomplete" % filename)
    finally:
        f.close()

    return host_list


def logger_basic_config(logger,
                        filename,
                        level,
                        logger_out_stream,
                        logger_err_stream):
        """
        :type logger: logging.Logger
        :type filename: str | None
        :type level: int
        """

        logger.setLevel(level)

        formatter = logging.Formatter("%(levelname)s:%(name)s:%(message)s", None)
        info_formatter = logging.Formatter("%(message)s", None)

        # TODO: what do we wont here? This part is highly customizable

        if filename:
            handler = logging.FileHandler(filename, 'a')

            handler.setFormatter(formatter)
            logger.addHandler(handler)
        else:
            info_handler = logging.StreamHandler(logger_out_stream)  # gets INFO
            warn_handler = logging.StreamHandler(logger_err_stream)  # gets all but INFO

            info_handler.addFilter(ExactLevelFilter([logging.INFO]))
            warn_handler.addFilter(ExactLevelFilter([logging.DEBUG, logging.WARN,
                                                     logging.ERROR, logging.CRITICAL]))

            info_handler.setFormatter(info_formatter)
            warn_handler.setFormatter(formatter)

            logger.addHandler(info_handler)
            logger.addHandler(warn_handler)
