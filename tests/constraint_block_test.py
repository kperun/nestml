#
# constraint_block_test.py
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
import os
import unittest

from pynestml.utils.model_parser import ModelParser

from pynestml.meta_model.ast_source_location import ASTSourceLocation

from pynestml.symbols.predefined_types import PredefinedTypes
from pynestml.symbols.predefined_functions import PredefinedFunctions
from pynestml.symbols.predefined_variables import PredefinedVariables
from pynestml.symbols.predefined_units import PredefinedUnits
from pynestml.symbol_table.symbol_table import SymbolTable

from pynestml.utils.logger import Logger, LoggingLevel

# minor setup steps required
Logger.init_logger(LoggingLevel.INFO)
SymbolTable.initialize_symbol_table(ASTSourceLocation(start_line=0, start_column=0, end_line=0, end_column=0))
PredefinedUnits.register_units()
PredefinedTypes.register_types()
PredefinedVariables.register_variables()
PredefinedFunctions.register_functions()


class ConstraintBlockTest(unittest.TestCase):
    def test_invalid(self):
        Logger.set_logging_level(LoggingLevel.NO)
        model = ModelParser.parse_model(
                os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'invalid')),
                             'CoCoConstraintBlockCorrectlyBuilt.nestml'))
        self.assertEqual(len(
                Logger.get_all_messages_of_level_and_or_neuron(model.get_neuron_list()[0], LoggingLevel.ERROR)), 8)

    def test_valid(self):
        Logger.set_logging_level(LoggingLevel.INFO)
        model = ModelParser.parse_model(
                os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'valid')),
                             'CoCoConstraintBlockCorrectlyBuilt.nestml'))
        self.assertEqual(len(
                Logger.get_all_messages_of_level_and_or_neuron(model.get_neuron_list()[0], LoggingLevel.ERROR)), 0)
