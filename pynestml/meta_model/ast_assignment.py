#
# ast_assignment.py
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
from pynestml.meta_model.ast_node import ASTNode
from pynestml.meta_model.ast_source_location import ASTSourceLocation
from pynestml.meta_model.ast_variable import ASTVariable


class ASTAssignment(ASTNode):
    """
    This class is used to store assignments.
    Grammar:
        assignment : lhs_variable=variable
            (directAssignment='='       |
            compoundSum='+='     |
            compoundMinus='-='   |
            compoundProduct='*=' |
            compoundQuotient='/=') rhs;

    Attributes:
        lhs = None
        is_direct_assignment = False
        is_compound_sum = False
        is_compound_minus = False
        is_compound_product = False
        is_compound_quotient = False
        rhs = None
    """

    def __init__(self, lhs = None, is_direct_assignment = False, is_compound_sum = False, is_compound_minus = False,
                 is_compound_product = False, is_compound_quotient = False, rhs = None, source_position = None):
        """
        Standard constructor.
        :param lhs: the left-hand side variable to which is assigned to.
        :type lhs: ASTVariable
        :param is_direct_assignment: is a direct assignment
        :type is_direct_assignment: bool
        :param is_compound_sum: is a compound sum
        :type is_compound_sum: bool
        :param is_compound_minus: is a compound minus
        :type is_compound_minus: bool
        :param is_compound_product: is a compound product
        :type is_compound_product: bool
        :param is_compound_quotient: is a compound quotient
        :type is_compound_quotient: bool
        :param rhs: an meta_model-rhs object
        :type rhs: ast_expression
        :param source_position: The source position of the assignment
        :type source_position: ASTSourceLocation
        """
        super(ASTAssignment, self).__init__(source_position)
        self.lhs = lhs
        self.is_direct_assignment = is_direct_assignment
        self.is_compound_sum = is_compound_sum
        self.is_compound_minus = is_compound_minus
        self.is_compound_product = is_compound_product
        self.is_compound_quotient = is_compound_quotient
        self.rhs = rhs
        return

    def get_variable(self):
        """
        Returns the left-hand side variable.
        :return: left-hand side variable object.
        :rtype: ASTVariable
        """
        return self.lhs

    def get_expression(self):
        """
        Returns the right-hand side rhs.
        :return: rhs object.
        :rtype: ASTExpression
        """
        return self.rhs

    def equals(self, other):
        """
        The equals operation.
        :param other: a different object.
        :type other: object
        :return: True if equal, otherwise False.
        :rtype: bool
        """
        if not isinstance(other, ASTAssignment):
            return False
        return (self.get_variable().equals(other.get_variable()) and
                self.is_compound_quotient == other.is_compound_quotient and
                self.is_compound_product == other.is_compound_product and
                self.is_compound_minus == other.is_compound_minus and
                self.is_compound_sum == other.is_compound_sum and
                self.is_direct_assignment == other.is_direct_assignment and
                self.get_expression().equals(other.get_expression()))
