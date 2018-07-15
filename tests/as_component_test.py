#
# as_component_test.py
#
# This file is part of NEST.
#
# Copyright (C) 2004 The NEST Initiative
#
# NEST is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# NEST is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with NEST.  If not, see <http://www.gnu.org/licenses/>.
import unittest
import os
import shutil

from pynestml.frontend.pynestml_frontend import to_nest
from pynestml.frontend.frontend_configuration import FrontendConfiguration


class AsComponentTest(unittest.TestCase):
    """"
    This test checks whether PyNestML can be executed correctly as a component from a different component.
    """

    def test_from_string(self):
        path = 'resources/CommentTest.nestml'
        target = 'target'
        dry = False
        logging_level = 'NO'
        module_name = 'module'
        store_log = False
        dev = True
        to_nest(path, target, dry, logging_level, module_name, store_log, dev)
        self.assertTrue(os.path.isfile(os.path.join(FrontendConfiguration.get_target_path(), 'CMakeLists.txt')))
        self.assertTrue(os.path.isfile(os.path.join(FrontendConfiguration.get_target_path(), 'commentTest.cpp')))
        self.assertTrue(os.path.isfile(os.path.join(FrontendConfiguration.get_target_path(), 'commentTest.h')))
        self.assertTrue(os.path.isfile(os.path.join(FrontendConfiguration.get_target_path(), 'module.cpp')))
        self.assertTrue(os.path.isfile(os.path.join(FrontendConfiguration.get_target_path(), 'module.h')))

    def test_from_objects(self):
        path = os.path.join('resources', 'CommentTest.nestml')
        target = os.path.join('target')
        dry = False
        logging_level = 'NO'
        module_name = 'module'
        store_log = False
        dev = True
        to_nest(path, target, dry, logging_level, module_name, store_log, dev)
        self.assertTrue(os.path.isfile(os.path.join(FrontendConfiguration.get_target_path(), 'CMakeLists.txt')))
        self.assertTrue(os.path.isfile(os.path.join(FrontendConfiguration.get_target_path(), 'commentTest.cpp')))
        self.assertTrue(os.path.isfile(os.path.join(FrontendConfiguration.get_target_path(), 'commentTest.h')))
        self.assertTrue(os.path.isfile(os.path.join(FrontendConfiguration.get_target_path(), 'module.cpp')))
        self.assertTrue(os.path.isfile(os.path.join(FrontendConfiguration.get_target_path(), 'module.h')))

    def tearDown(self):
        # clean up
        shutil.rmtree(FrontendConfiguration.target_path)
