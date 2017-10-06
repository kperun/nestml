#
# ExpressionParsingTest.py
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
from antlr4 import *
import os
from pynestml.grammars.PyNESTMLLexer import PyNESTMLLexer
from pynestml.grammars.PyNESTMLParser import PyNESTMLParser
from pynestml.nestml.PredefinedTypes import PredefinedTypes
from pynestml.nestml.PredefinedUnits import PredefinedUnits
from pynestml.nestml.PredefinedFunctions import PredefinedFunctions
from pynestml.nestml.PredefinedVariables import PredefinedVariables
from pynestml.nestml.CoCosManager import CoCosManager
from pynestml.nestml.SymbolTable import SymbolTable
from pynestml.nestml.ASTSourcePosition import ASTSourcePosition
from pynestml.nestml.ASTBuilderVisitor import ASTBuilderVisitor
from pynestml.nestml.ASTNESTMLCompilationUnit import ASTNESTMLCompilationUnit
from pynestml.utils.Logger import LOGGING_LEVEL, Logger

# setups the infrastructure
PredefinedUnits.registerUnits()
PredefinedTypes.registerTypes()
PredefinedFunctions.registerPredefinedFunctions()
PredefinedVariables.registerPredefinedVariables()
SymbolTable.initializeSymbolTable(ASTSourcePosition(_startLine=0, _startColumn=0, _endLine=0, _endColumn=0))
Logger.initLogger(LOGGING_LEVEL.NO)
CoCosManager.initializeCoCosManager()


class ExpressionParsingTest(unittest.TestCase):
    """
    This text is used to check the parsing of the expression sub-language.
    """

    def test(self):
        # print('Start Expression Parser Test...'),
        inputFile = FileStream(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__),'resources')),
                         'ExpressionCollection.nestml'))
        lexer = PyNESTMLLexer(inputFile)
        # create a token stream
        stream = CommonTokenStream(lexer)
        # parse the file
        parser = PyNESTMLParser(stream)
        # parser.nestmlCompilationUnit()
        # print('done')
        astBuilderVisitor = ASTBuilderVisitor()
        ast = astBuilderVisitor.visit(parser.nestmlCompilationUnit())
        # print('done')
        assert isinstance(ast, ASTNESTMLCompilationUnit)


if __name__ == '__main__':
    unittest.main()