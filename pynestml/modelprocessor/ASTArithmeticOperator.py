#
# ASTArithmeticOperator.py
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with NEST.  If not, see <http://www.gnu.org/licenses/>.


from pynestml.modelprocessor.ASTNode import ASTNode


class ASTArithmeticOperator(ASTNode):
    """
    This class is used to store a single arithmetic operator, e.g. +.
    No grammar. This part is defined outside the grammar to make processing and storing of models easier and 
    comprehensible.
    """
    is_times_op = False  # type: bool
    is_div_op = False  # type:bool
    is_modulo_op = False  # type:bool
    is_plus_op = False  # type:bool
    is_minus_op = False  # type: bool
    is_pow_op = False  # type:bool

    def __init__(self, is_times_op, is_div_op, is_modulo_op, is_plus_op, is_minus_op, is_pow_op, source_position):
        # type:(bool,bool,bool,bool,bool,bool,ASTSourcePosition) -> None
        assert ((is_times_op + is_div_op + is_modulo_op + is_plus_op + is_minus_op + is_pow_op) == 1), \
            '(PyNESTML.AST.ArithmeticOperator) Type of arithmetic operator not specified!'
        super(ASTArithmeticOperator, self).__init__(source_position)
        self.is_times_op = is_times_op
        self.is_div_op = is_div_op
        self.is_modulo_op = is_modulo_op
        self.is_plus_op = is_plus_op
        self.is_minus_op = is_minus_op
        self.is_pow_op = is_pow_op
        return

    def __str__(self):
        # type: () -> str
        """
        Returns the string representation of the operator.
        :return: the operator as a string.
        :rtype: str
        """
        if self.is_times_op:
            return ' * '
        elif self.is_div_op:
            return ' / '
        elif self.is_modulo_op:
            return ' % '
        elif self.is_plus_op:
            return ' + '
        elif self.is_minus_op:
            return ' - '
        elif self.is_pow_op:
            return ' ** '
        else:
            raise InvalidArithmeticOperator('(PyNestML.ArithmeticOperator.Print) Arithmetic operator not specified.')

    def get_parent(self, ast=None):
        """
        Indicates whether a this node contains the handed over node.
        :param ast: an arbitrary ast node.
        :type ast: AST_
        :return: AST if this or one of the child nodes contains the handed over element.
        :rtype: AST_ or None
        """
        return None

    def equals(self, other):
        # type: (ASTNode) -> bool
        """
        The equality method.
        """
        if not isinstance(other, ASTArithmeticOperator):
            return False
        return (self.is_times_op == other.is_times_op and self.is_div_op == other.is_div_op and
                self.is_modulo_op == other.is_modulo_op and self.is_plus_op == other.is_plus_op and
                self.is_minus_op == other.is_minus_op and self.is_pow_op == other.is_pow_op)


class InvalidArithmeticOperator(Exception):
    """
    This exception is thrown whenever the arithmetic operator has not been specified.
    """
    pass
