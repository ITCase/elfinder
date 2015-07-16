#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2015 uralbash <root@uralbash.ru>
#
# Distributed under terms of the MIT license.

"""
Connector for elfinder
"""
import os
import time
from datetime import datetime

from .common import OPTIONS, Commands, merge_dict


class CachedAttribute(object):
    '''
    Computes attribute value and caches it in the instance.  From the Python
    Cookbook (Denis Otkidach) This decorator allows you to create a property
    which can be computed once and accessed many times. Sort of like
    memoization.
    '''
    def __init__(self, method, name=None):
        # record the unbound-method and the name
        self.method = method
        self.name = name or method.__name__
        self.__doc__ = method.__doc__

    def __get__(self, inst, cls):
        # self: <__main__.cache object at 0xb781340c>
        # inst: <__main__.Foo object at 0xb781348c>
        # cls: <class '__main__.Foo'>
        if inst is None:
            # instance attribute accessed on class, return self
            # You get here if you write `Foo.bar`
            return self
        # compute, cache and return the instance's attribute value
        result = self.method(inst)
        # setattr redefines the instance's attribute so this doesn't get called
        # again
        setattr(inst, self.name, result)
        return result


class Connector(Commands):
    """
    Connector for elFinder
    """

    def __init__(self, options):
        # TODO: Add disabled commands
        self.options = merge_dict(OPTIONS, options)

    @CachedAttribute
    def tmbDir(self):
        if self.options['tmbDir']:
            thumbs_dir = os.path.join(
                self.options['root'],
                self.options['tmbDir']
            )
            if not os.path.exists(thumbs_dir):
                os.makedirs(thumbs_dir)
            return thumbs_dir
        else:
            return OPTIONS['tmbDir']

    @property
    def command(self):
        cmd = getattr(self.request, 'cmd', 'open')
        return getattr(self, cmd)

    def run(self, request):
        self.request = request
        self._time = time.time()
        t = datetime.fromtimestamp(self._time)
        self._today = time.mktime(datetime(t.year, t.month, t.day).timetuple())
        self._yesterday = self._today - 86400
        self.check_path(self.options['root'])
        return self.command()
