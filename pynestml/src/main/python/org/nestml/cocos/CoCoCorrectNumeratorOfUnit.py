#
# CoCoCorrectNumeratorOfUnit.py
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
from pynestml.src.main.python.org.nestml.ast.ASTNeuron import ASTNeuron
from pynestml.src.main.python.org.nestml.visitor.ASTHigherOrderVisitor import ASTHigherOrderVisitor
from pynestml.src.main.python.org.utils.Logger import LOGGING_LEVEL, Logger


class CoCoCorrectNumeratorOfUnit(CoCo):
    """
    This coco ensures that all units which consist of a dividend and divisor, where the numerator is a numeric
    value, have 1 as the numerator. 
    Allowed:
        V_m 1/mV = ...
    Not allowed:
        V_m 2/mV = ...
    """
    __unitTypes = list()

    @classmethod
    def checkCoCo(cls, _neuron=None):
        """
        Ensures the coco for the handed over neuron.
        :param _neuron: a single neuron instance.
        :type _neuron: ASTNeuron
        """
        assert (_neuron is not None and isinstance(_neuron, ASTNeuron)), \
            '(PyNestML.CoCo.CorrectNumerator) No or wrong type of neuron provided (%s)!' % type(_neuron)
        cls.__unitTypes = list()
        ASTHigherOrderVisitor.visitNeuron(_neuron, cls.__collectUnitTypes)
        for unit in cls.__unitTypes:
            if unit.getLhs() != 1:
                Logger.logMessage(
                    '[' + _neuron.getName() + '.nestml] Numeric numerator of unit "%s" at %s not 1!'
                    % (unit.printAST(), unit.getSourcePosition().printSourcePosition()),
                    LOGGING_LEVEL.ERROR)

    @classmethod
    def __collectUnitTypes(cls, _ast=None):
        """
        For a given node, it collects all the unit-types which have a numeric numerator.
        :param _ast: a single ast node
        :type _ast: AST_
        """
        from pynestml.src.main.python.org.nestml.ast.ASTUnitType import ASTUnitType
        if isinstance(_ast, ASTUnitType) and _ast.isDiv() and isinstance(_ast.getLhs(), int):
            cls.__unitTypes.append(_ast)
        return