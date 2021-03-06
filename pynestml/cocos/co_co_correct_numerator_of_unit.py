#
# co_co_correct_numerator_of_unit.py
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
from pynestml.cocos.co_co import CoCo
from pynestml.meta_model.ast_neuron import ASTNeuron
from pynestml.meta_model.ast_unit_type import ASTUnitType
from pynestml.utils.logger import Logger, LoggingLevel
from pynestml.utils.messages import Messages
from pynestml.visitors.ast_visitor import ASTVisitor


class CoCoCorrectNumeratorOfUnit(CoCo):
    name = 'correct numerator of unit'

    description = 'This coco ensures that all units which consist of a dividend and divisor, where ' \
                  'the numerator is a numeric value, have 1 as the numerator.\n' \
                  'Allowed:\n' \
                  '    V_m 1/mV = ...\n' \
                  'Not allowed:\n' \
                  '    V_m 2/mV = ...'

    def check_co_co(self, node):
        """
        Ensures the coco for the handed over neuron.
        :param node: a single neuron instance.
        :type node: ASTNeuron
        """
        node.accept(NumericNumeratorVisitor())


class NumericNumeratorVisitor(ASTVisitor):
    """
    Visits a numeric numerator and checks if the value is 1.
    """

    def visit_unit_type(self, node):
        """
        Check if the coco applies,
        :param node: a single unit type object.
        :type node: ASTUnitType
        """
        if node.is_div and isinstance(node.lhs, int) and node.lhs != 1:
            code, message = Messages.get_wrong_numerator(str(node))
            Logger.log_message(code=code, message=message, error_position=node.get_source_position(),
                               log_level=LoggingLevel.ERROR)
