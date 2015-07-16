#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2015 uralbash <root@uralbash.ru>
#
# Distributed under terms of the MIT license.

"""
Test for elfinder connector
"""

import os
import json
import unittest
from datetime import datetime

from elfinder import Connector, ElfinderException

HERE = os.path.dirname(os.path.realpath(__file__))
ROOT = os.path.join(HERE, 'static/uploads')


class BaseTests(unittest.TestCase):

    maxDiff = None

    def setUp(self):

        self.options = {'root': ROOT}


class TestRootOption(BaseTests):

    def test_run_wo_root_option(self):
        connector = Connector({})
        self.assertRaises(
            ElfinderException,
            connector.run, {}
        )

    def test_run_with_bad_path_in_root_option(self):
        path = '/bad/path/'
        connector = Connector({'root': path})
        self.assertRaises(
            ElfinderException,
            connector.run, {}
        )

    def test_run_denied_root_path(self):
        pass


class TestCommand(BaseTests):

    def test_open_init(self):
        request = json.loads("""{"cmd": "open", "init": 1, "tree": 1}""")
        connector = Connector(self.options)
        response = connector.run(request)
        date = datetime.fromtimestamp(
            os.stat(ROOT).st_mtime
        ).strftime("%d %b %Y %H:%M")
        self.assertEqual(
            response,
            {'api': '2.0',
             'cdc': [],
             'cwd': {'date': date,
                     'hash': '8320a3d391b236e4cbde269a665c3045',
                     'mime': 'directory',
                     'name': 'Home',
                     'read': True,
                     'rel': 'Home',
                     'rm': False,
                     'size': 0,
                     'write': True},
             'tree': {'dirs': [],
                      'hash': '8320a3d391b236e4cbde269a665c3045',
                      'name': 'Home',
                      'read': True,
                      'write': True}}
        )
