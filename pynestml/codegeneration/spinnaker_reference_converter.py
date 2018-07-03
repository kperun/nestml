#
# spinnaker_reference_converter.py
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
from pynestml.codegeneration.i_reference_converter import IReferenceConverter
from pynestml.codegeneration.nest_names_converter import NestNamesConverter
from pynestml.codegeneration.unit_converter import UnitConverter
from pynestml.meta_model.ast_arithmetic_operator import ASTArithmeticOperator
from pynestml.meta_model.ast_bit_operator import ASTBitOperator
from pynestml.meta_model.ast_comparison_operator import ASTComparisonOperator
from pynestml.meta_model.ast_function_call import ASTFunctionCall
from pynestml.meta_model.ast_logical_operator import ASTLogicalOperator
from pynestml.meta_model.ast_variable import ASTVariable
from pynestml.symbols.predefined_functions import PredefinedFunctions
from pynestml.symbols.predefined_units import PredefinedUnits
from pynestml.symbols.predefined_variables import PredefinedVariables
from pynestml.symbols.symbol import SymbolKind
from pynestml.utils.ast_utils import ASTUtils
from pynestml.utils.logger import Logger, LoggingLevel
from pynestml.utils.messages import Messages


class SpiNNakerReferenceConverter(IReferenceConverter):

    def convert_binary_op(self, op):
        """
        Converts a single binary operator to nest processable format.
        :param op: a single binary operator string.
        :type op: AST_
        :return: the corresponding nest representation
        :rtype: str
        """
        if isinstance(op, ASTArithmeticOperator):
            return self.convert_arithmetic_operator(op)
        if isinstance(op, ASTBitOperator):
            return self.convert_bit_operator(op)
        if isinstance(op, ASTComparisonOperator):
            return self.convert_comparison_operator(op)
        if isinstance(op, ASTLogicalOperator):
            return self.convert_logical_operator(op)
        else:
            Logger.log_message('Cannot determine binary operator!', LoggingLevel.ERROR)
            return '(%s) ERROR (%s)'

    def convert_function_call(cls, op):
        """
        Converts a single handed over function call to nest processable format.
        :param op: a single function call
        :type op:  ASTFunctionCall
        :return: a string representation
        :rtype: str
        """
        function_name = op.get_name()
        if function_name == 'and':
            return '&&'
        elif function_name == 'or':
            return '||'
        elif function_name == 'resolution':
            return 'nest::Time::get_resolution().get_ms()'
        elif function_name == 'steps':
            return 'nest::Time(nest::Time::ms((double) %s)).get_steps()'
        elif function_name == PredefinedFunctions.POW:
            return 'std::pow(%s)'
        elif function_name == PredefinedFunctions.MAX or function_name == PredefinedFunctions.BOUNDED_MAX:
            return 'std::max(%s)'
        elif function_name == PredefinedFunctions.MIN or function_name == PredefinedFunctions.BOUNDED_MIN:
            return 'std::min(%s)'
        elif function_name == PredefinedFunctions.EXP:
            return 'std::exp(%s)'
        elif function_name == PredefinedFunctions.LOG:
            return 'std::log(%s)'
        elif function_name == 'expm1':
            return 'numerics::expm1(%s)'
        elif function_name == PredefinedFunctions.EMIT_SPIKE:
            return 'set_spiketime(nest::Time::step(origin.get_steps()+lag+1));\n' \
                   'nest::SpikeEvent se;\n' \
                   'nest::kernel().event_delivery_manager.send(*this, se, lag)'
        elif ASTUtils.needs_arguments(op):
            return function_name + '(%s)'
        else:
            return function_name + '()'

    def convert_name_reference(self, op):
        """
        Converts a single variable to nest processable format.
        :param op: a single variable.
        :type op: ASTVariable
        :return: a nest processable format.
        :rtype: str
        """
        assert (op is not None and isinstance(op, ASTVariable)), \
            '(PyNestML.CodeGeneration.NestReferenceConverter) No or wrong type of uses-gsl provided (%s)!' % type(
                    op)
        if PredefinedUnits.is_unit(op.get_complete_name()):
            return 'REAL_CONST(%s)' % (
                UnitConverter.get_factor(PredefinedUnits.get_unit(op.get_complete_name()).get_unit()))
        variable_name = NestNamesConverter.convert_to_cpp_name(op.get_complete_name())
        if variable_name == PredefinedVariables.E_CONSTANT:
            return 'M_E'
        return 'neuron->' + op.get_name()

    def convert_constant(self, constant):
        """
        Converts a single handed over constant.
        :param constant: a constant as string.
        :type constant: str
        :return: the corresponding nest representation
        :rtype: str
        """
        # TODO: SpiNNaker does not support boolean , thus 1 == True, 0 == False
        if constant == 'True':
            return '1'
        elif constant == 'False':
            return '0'
        elif isinstance(constant, int) or isinstance(constant, float):
            return 'REAL_CONST(%s)' % constant
        elif constant == 'inf':
            raise Exception('SpiNNaker: Inf currently not supported!')
            # return 'std::numeric_limits<double_t>::infinity()'
        else:
            return str(constant)

    def convert_unary_op(self, unary_operator):
        """
        Depending on the concretely used operator, a string is returned.
        :param unary_operator: a single operator.
        :type unary_operator:  str
        :return: the same operator
        :rtype: str
        """
        from pynestml.meta_model.ast_unary_operator import ASTUnaryOperator
        assert (unary_operator is not None and isinstance(unary_operator, ASTUnaryOperator)), \
            '(PyNestML.CodeGeneration.NestReferenceConverter) No or wrong type of unary operator provided (%s)!' \
            % type(unary_operator)
        if unary_operator.is_unary_plus:
            return '(' + '+' + '%s' + ')'
        elif unary_operator.is_unary_minus:
            return '(' + '-' + '%s' + ')'
        elif unary_operator.is_unary_tilde:
            return '(' + '~' + '%s' + ')'
        else:
            Logger.log_message('Cannot determine unary operator!', LoggingLevel.ERROR)
            return '(' + '%s' + ')'

    def convert_encapsulated(self):
        """
        Converts the encapsulating parenthesis to NEST style.
        :return: a set of parenthesis
        :rtype: str
        """
        return '(%s)'

    def convert_logical_not(self):
        """
        Returns a representation of the logical not in NEST.
        :return: a string representation
        :rtype: str
        """
        return '(' + '!' + '%s' + ')'

    def convert_logical_operator(self, op):
        """
        Prints a logical operator in NEST syntax.
        :param op: a logical operator object
        :type op: ASTLogicalOperator
        :return: a string representation
        :rtype: str
        """
        from pynestml.meta_model.ast_logical_operator import ASTLogicalOperator
        assert (op is not None and isinstance(op, ASTLogicalOperator)), \
            '(PyNestML.CodeGeneration.NestReferenceConverter) No or wrong type of logical operator provided (%s)!' \
            % type(op)
        if op.is_logical_and:
            return '%s' + '&&' + '%s'
        elif op.is_logical_or:
            return '%s' + '||' + '%s'
        else:
            Logger.log_message('Cannot determine logical operator!', LoggingLevel.ERROR)
            return '(%s) ERROR  (%s)'

    @classmethod
    def convert_comparison_operator(cls, op):
        """
        Prints a logical operator in NEST syntax.
        :param op: a logical operator object
        :type op: ASTComparisonOperator
        :return: a string representation
        :rtype: str
        """
        from pynestml.meta_model.ast_comparison_operator import ASTComparisonOperator
        assert (op is not None and isinstance(op, ASTComparisonOperator)), \
            '(PyNestML.CodeGeneration.NestReferenceConverter) No or wrong type of logical operator provided (%s)!' \
            % type(op)
        if op.is_lt:
            return '%s' + '<' + '%s'
        elif op.is_le:
            return '%s' + '<=' + '%s'
        elif op.is_eq:
            return '%s' + '==' + '%s'
        elif op.is_ne or op.is_ne2:
            return '%s' + '!=' + '%s'
        elif op.is_ge:
            return '%s' + '>=' + '%s'
        elif op.is_gt:
            return '%s' + '>' + '%s'
        else:
            Logger.log_message('Cannot determine comparison operator!', LoggingLevel.ERROR)
            return '(%s) ERROR  (%s)'

    @classmethod
    def convert_bit_operator(cls, op):
        """
        Prints a logical operator in NEST syntax.
        :param op: a logical operator object
        :type op: ASTBitOperator
        :return: a string representation
        :rtype: str
        """
        from pynestml.meta_model.ast_bit_operator import ASTBitOperator
        assert (op is not None and isinstance(op, ASTBitOperator)), \
            '(PyNestML.CodeGeneration.NestReferenceConverter) No or wrong type of bit operator provided (%s)!' \
            % type(op)
        if op.is_bit_shift_left:
            return '%s' + '<<' '%s'
        if op.is_bit_shift_right:
            return '%s' + '>>' + '%s'
        if op.is_bit_and:
            return '%s' + '&' + '%s'
        if op.is_bit_or:
            return '%s' + '|' + '%s'
        if op.is_bit_xor:
            return '%s' + '^' + '%s'
        else:
            Logger.log_message('Cannot determine bit operator!', LoggingLevel.ERROR)
            return '(%s) ERROR (%s)'

    def convert_arithmetic_operator(self, op):
        """
        Prints a logical operator in NEST syntax.
        :param op: a logical operator object
        :type op: ASTArithmeticOperator
        :return: a string representation
        :rtype: str
        """
        from pynestml.meta_model.ast_arithmetic_operator import ASTArithmeticOperator
        assert (op is not None and isinstance(op, ASTArithmeticOperator)), \
            '(PyNestML.CodeGeneration.ExpressionPrettyPrinter) No or wrong type of arithmetic operator provided (%s)!' \
            % type(op)
        if op.is_plus_op:
            return '%s' + '+' + '%s'
        if op.is_minus_op:
            return '%s' + '-' + '%s'
        if op.is_times_op:
            return '%s' + '*' + '%s'
        if op.is_div_op:
            return '%s' + '/' + '%s'
        if op.is_modulo_op:
            return '%s' + '%' + '%s'
        if op.is_pow_op:
            return 'pow' + '(%s,%s)'
        else:
            Logger.log_message('Cannot determine arithmetic operator!', LoggingLevel.ERROR)
            return '(%s) ERROR (%s)'

    def convert_ternary_operator(self):
        """
        Prints a ternary operator in NEST syntax.
        :return: a string representation
        :rtype: str
        """
        return '(' + '%s' + ')?(' + '%s' + '):(' + '%s' + ')'