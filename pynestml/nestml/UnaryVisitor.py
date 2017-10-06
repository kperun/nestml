#
# UnaryVisitor.py
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

"""
Expr = unaryOperator term=expression
unaryOperator : (unaryPlus='+' | unaryMinus='-' | unaryTilde='~');
"""
from pynestml.nestml.ASTUnaryOperator import ASTUnaryOperator
from pynestml.nestml.TypeChecker import TypeChecker
from pynestml.nestml.ErrorStrings import ErrorStrings
from pynestml.nestml.NESTMLVisitor import NESTMLVisitor
from pynestml.nestml.Either import Either
from pynestml.utils.Logger import Logger, LOGGING_LEVEL


class UnaryVisitor(NESTMLVisitor):
    def visitExpression(self, _expr=None):
        termTypeE = _expr.getExpression().getTypeEither()

        if termTypeE.isError():
            _expr.setTypeEither(termTypeE)
            return

        termType = termTypeE.getValue()
        unaryOp = _expr.getUnaryOperator()
        # unaryOp exists if we get into this visitor but make sure:
        assert unaryOp is not None and isinstance(unaryOp, ASTUnaryOperator)

        if unaryOp.isUnaryMinus() or unaryOp.isUnaryPlus():
            if (TypeChecker.isNumeric(termType)):
                _expr.setTypeEither(Either.value(termType))
                return
            else:
                errorMsg = ErrorStrings.messageNonNumericType(self, termType.printSymbol(), _expr.getSourcePosition())
                _expr.setTypeEither(Either.error(errorMsg))
                Logger.logMessage(errorMsg, LOGGING_LEVEL.ERROR)
                return
        elif unaryOp.isUnaryTilde():
            if TypeChecker.isInteger(termType):
                _expr.setTypeEither(Either.value(termType))
                return
            else:
                errorMsg = ErrorStrings.messageNonNumericType(self, termType.printSymbol(), _expr.getSourcePosition())
                _expr.setTypeEither(Either.error(errorMsg))
                Logger.logMessage(errorMsg, LOGGING_LEVEL.ERROR)
                return
        # Catch-all if no case has matched
        errorMsg = ErrorStrings.messageTypeError(self, _expr.printAST(), _expr.get_SourcePosition())
        Logger.logMessage(errorMsg, LOGGING_LEVEL.ERROR)
        _expr.setTypeEither(Either.error(errorMsg))
        return