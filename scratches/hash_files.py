#!/usr/bin/python
# coding=utf-8
# hash_files.py
#
import hashlib

__author__ = 'voddan'
__package__ = None

filepath = "../bin/httpress_rh6"

file = open(filepath, 'rb')
content = file.read()

hasher = hashlib.md5()
hasher.update(content)

print hasher.hexdigest()

# hasher = hashlib.md5()
# with open(filepath, 'rb') as afile:
#     buf = afile.read()
#     hasher.update(buf)
# print(hasher.hexdigest())
