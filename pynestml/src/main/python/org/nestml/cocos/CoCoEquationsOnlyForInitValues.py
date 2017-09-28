#
# CoCoEquationsOnlyForInitValues.py
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
from pynestml.src.main.python.org.nestml.cocos.CoCo import CoCo
from pynestml.src.main.python.org.utils.Logger import Logger, LOGGING_LEVEL
from pynestml.src.main.python.org.nestml.symbol_table.symbols.Symbol import SymbolKind
from pynestml.src.main.python.org.nestml.ast.ASTNeuron import ASTNeuron
from pynestml.src.main.python.org.nestml.visitor.ASTHigherOrderVisitor import ASTHigherOrderVisitor


class CoCoEquationsOnlyForInitValues(CoCo):
    """
    This coco ensures that ode equations are only provided for variables which have been defined in the
    initial_values block.
    Allowed:
        initial_values:
            V_m mV = 10mV
        end
        equations:
            V_m' = ....
        end
    Not allowed:
        state:
            V_m mV = 10mV
        end
        equations:
            V_m' = ....
        end
    """
    __neuronName = None

    @classmethod
    def checkCoCo(cls, _neuron=None):
        """
        Ensures the coco for the handed over neuron.
        :param _neuron: a single neuron instance.
        :type _neuron: ASTNeuron
        """
        assert (_neuron is not None and isinstance(_neuron, ASTNeuron)), \
            '(PyNestML.CoCo.CorrectNumerator) No or wrong type of neuron provided (%s)!' % type(_neuron)
        cls.__neuronName = _neuron.getName()
        ASTHigherOrderVisitor.visitNeuron(_neuron, cls.__checkCoco)
        return

    @classmethod
    def __checkCoco(cls, _ast=None):
        """
        For a given node of type unit-type it checks, if the coco applies.
        :param _ast: a single ast node
        :type _ast: AST_
        """
        from pynestml.src.main.python.org.nestml.ast.ASTOdeEquation import ASTOdeEquation
        if isinstance(_ast, ASTOdeEquation):
            symbol = _ast.getScope().resolveToSymbol(_ast.getLhs().getNameOfLhs(), SymbolKind.VARIABLE)
            if symbol is not None and not symbol.isInitValues():
                Logger.logMessage(
                    '[' + cls.__neuronName + '.nestml] Ode equation lhs-variable "%s" at %s not '
                                             'defined in initial-values block!'
                    % (_ast.getLhs().getNameOfLhs(), _ast.getSourcePosition().printSourcePosition()),
                    LOGGING_LEVEL.ERROR)
        return