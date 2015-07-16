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

from .common import (
    OPTIONS,
    Commands,
    merge_dict,
    CachedAttribute,
    ElfinderException
)


class Connector(Commands):
    """
    Connector for elFinder
    """

    def __init__(self, options):
        # for cmd in self._options['disabled']:
        #     if cmd in self._commands:
        #         del self._commands[cmd]
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

        if 'root' not in self.options or\
                not os.path.exists(self.options['root'])\
                or self.options['root'] == '':
            raise ElfinderException(
                'Invalid backend configuration: "root" option has bad value'
            )
        elif not self._isAllowed(self.options['root'], 'read'):
            raise ElfinderException('Access denied to "root" path')

        return self.command()
