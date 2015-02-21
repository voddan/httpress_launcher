#!/usr/bin/python
# coding=utf-8
# httpress_launcher.py
# Simple launcher for src/main.py
#
__author__ = 'voddan'
__package__ = None

import os

__file_path__ = os.path.dirname(os.path.realpath(__file__))
__project_root__ = __file_path__ + '/'

import sys

comline_argv = sys.argv[1:]
comline_list = ['"' + __project_root__ + 'src/main.py" '] + comline_argv
comline_string = ' '.join(comline_list)

# os.system(comline_string)

from src.main import main_launcher
main_launcher(comline_argv)
