#!/usr/bin/python
# coding=utf-8
# setup.py
#
__author__ = 'voddan'
__package__ = None
__project_root__ = '/home/voddan/Program/Parallels/httpress_launcher/'

from setuptools import setup, find_packages

project_root_url = __project_root__.replace('/', '.')
# print find_packages(project_root_url + 'src')
# print find_packages('../src')

setup(
    name="httpress_launcher",
    version="0.1",
    packages=['httpress_launcher']
    # py_modules=['httpress_launcher']
)
