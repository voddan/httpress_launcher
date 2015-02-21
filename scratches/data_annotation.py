#!/usr/bin/python
# coding=utf-8
# data_annotation.py
#
__author__ = 'voddan'
__package__ = None

class data:
    @staticmethod
    def repr(obj):
        items = []
        for prop, value in obj.__dict__.items():
            try:
                item = "%s = %r" % (prop, value)
                assert len(item) < 20
            except:
                item = "%s: <%s>" % (prop, value.__class__.__name__)
            items.append(item)

        return "%s(%s)" % (obj.__class__.__name__, ', '.join(items))

    def __init__(self, cls):
        cls.__repr__ = data.repr
        self.cls = cls

    def __call__(self, *args, **kwargs):
        return self.cls(*args, **kwargs)


class SomeOtherClass:
    pass

@data
class PythonBean:
    def __init__(self):
        self.int = 1
        self.list = [5, 6, 7]
        self.str = "hello"
        self.obj = SomeOtherClass()


if __name__ == '__main__':
    obj = PythonBean()
    print obj