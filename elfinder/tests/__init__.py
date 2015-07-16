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
from pprint import pprint

from elfinder import Connector, ElfinderException

PP = pprint
HERE = os.path.dirname(os.path.realpath(__file__))
ROOT = os.path.join(HERE, 'static/uploads')


class BaseTests(unittest.TestCase):

    maxDiff = None

    def setUp(self):
        self.options = {'root': ROOT}
        self.connector = Connector(self.options)


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
        response = self.connector.run(request)
        self.assertEqual(response['api'], '2.0')
        self.assertEqual(len(response['cdc']), 1)
        self.assertEqual(response['cwd']['mime'], 'directory')
        self.assertEqual(response['cwd']['name'], 'Home')
        self.assertEqual(response['cwd']['read'], True)
        self.assertEqual(response['cwd']['write'], True)
        self.assertEqual(response['cwd']['size'], 0)
        self.assertEqual(response['cwd']['rel'], 'Home')
        self.assertEqual(response['cwd']['rm'], False)
        self.assertEqual(response['tree']['dirs'], [])
        self.assertEqual(response['tree']['name'], 'Home')
        self.assertEqual(response['tree']['read'], True)
        self.assertEqual(response['tree']['write'], True)
