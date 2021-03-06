#
# messages.py.py
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
from enum import Enum


class Messages(object):
    """
    This class contains a collection of error messages which enables a centralized maintaining and modifications of
    those.
    """

    SEPARATOR = " : "

    @classmethod
    def get_start_processing_file(cls, file_path):
        """
        Returns a message indicating that processing of a file has started
        :param file_path: the path to the file
        :type file_path: str
        :return: message code tuple
        :rtype: (MessageCode,str)
        """
        message = 'Start processing \'' + file_path + '\'!'
        return MessageCode.START_PROCESSING_FILE, message

    @classmethod
    def get_new_type_registered(cls, type_name):
        """
        Returns a message which indicates that a new type has been registered.
        :param type_name: a type name
        :type type_name: str
        :return: message code tuple
        :rtype: (MessageCode,str)
        """
        message = 'New type registered \'%s\'!' % type_name
        return MessageCode.TYPE_REGISTERED, message

    @classmethod
    def get_binary_operation_not_defined(cls, lhs, operator, rhs):
        message = 'Operation %s %s %s is not defined!' % (lhs, operator, rhs)
        return MessageCode.OPERATION_NOT_DEFINED, message

    @classmethod
    def get_unary_operation_not_defined(cls, operator, term):
        message = 'Operation %s%s is not defined!' % (operator, term)
        return MessageCode.OPERATION_NOT_DEFINED, message

    @classmethod
    def get_convolve_needs_buffer_parameter(cls):
        message = 'Convolve requires a buffer variable as second parameter!'
        return MessageCode.CONVOLVE_NEEDS_BUFFER_PARAMETER, message

    @classmethod
    def get_implicit_magnitude_conversion(cls, lhs, rhs, conversion_factor):
        message = 'Non-matching unit types at %s +/- %s! ' \
                  'Implicitly replaced by %s +/- %s * %s.' % (lhs, rhs, lhs, conversion_factor, rhs)
        return MessageCode.IMPLICIT_CAST, message

    @classmethod
    def get_start_building_symbol_table(cls):
        """
        Returns a message that the building for a neuron has been started.
        :return: a message
        :rtype: (MessageCode,str)
        """
        return MessageCode.START_SYMBOL_TABLE_BUILDING, 'Start building symbol table!'

    @classmethod
    def get_function_call_implicit_cast(cls, arg_nr, function_call, expected_type, got_type, castable = False):
        """
        Returns a message indicating that an implicit cast has been performed.
        :param arg_nr: the number of the argument which is cast
        :type arg_nr: int
        :param function_call: a single function call
        :type function_call: ASTFunctionCall
        :param expected_type: the expected type
        :type expected_type: TypeSymbol
        :param got_type: the got-type
        :type got_type: TypeSymbol
        :param castable: is the type castable
        :type castable: bool
        :return: a message
        :rtype: (MessageCode,str)
        """
        if not castable:
            message = str(arg_nr) + '. argument of function-call \'%s\' at is wrongly typed! Expected \'%s\',' \
                                    ' found \'%s\'!' % (function_call.get_name(), got_type,
                                                        expected_type.print_symbol())
        else:
            message = str(arg_nr) + '. argument of function-call \'%s\' is wrongly typed! ' \
                                    'Implicit cast from \'%s\' to \'%s\'.' % (function_call.get_name(),
                                                                              got_type,
                                                                              expected_type.print_symbol())
        return MessageCode.FUNCTION_CALL_TYPE_ERROR, message

    @classmethod
    def get_type_could_not_be_derived(cls, rhs):
        """
        Returns a message indicating that the type of the rhs rhs could not be derived.
        :param rhs: an rhs
        :type rhs: ASTExpressionNode
        :return: a message
        :rtype: (MessageCode,str)

        """
        message = 'Type of \'%s\' could not be derived!' % rhs
        return MessageCode.TYPE_NOT_DERIVABLE, message

    @classmethod
    def get_implicit_cast_rhs_to_lhs(cls, rhs_type, lhs_type):
        """
        Returns a message indicating that the type of the lhs does not correspond to the one of the rhs, but the rhs
        can be cast down to lhs type.
        :param rhs_type: the type of the rhs
        :type rhs_type: str
        :param lhs_type: the type of the lhs
        :type lhs_type: str
        :return: a message
        :rtype:(MessageCode,str)
        """
        message = 'Implicit casting %s to %s!' % (rhs_type, lhs_type)
        return MessageCode.IMPLICIT_CAST, message

    @classmethod
    def get_different_type_rhs_lhs(cls, rhs_expression, lhs_expression, rhs_type, lhs_type):
        """
        Returns a message indicating that the type of the lhs does not correspond to the one of the rhs and can not
        be cast down to a common type.
        :param rhs_expression: the rhs rhs
        :type rhs_expression: ASTExpression or ASTSimpleExpression
        :param lhs_expression: the lhs rhs
        :type lhs_expression: ast_expression or ast_simple_expression
        :param rhs_type: the type of the rhs
        :type rhs_type: type_symbol
        :param lhs_type: the type of the lhs
        :type lhs_type: TypeSymbol
        :return: a message
        :rtype:(MessageCode,str)
        """
        message = 'Type of lhs \'%s\' does not correspond to rhs \'%s\'! LHS: \'%s\', RHS: \'%s\'!' % (
            lhs_expression,
            rhs_expression,
            lhs_type,
            rhs_type)
        return MessageCode.CAST_NOT_POSSIBLE, message

    @classmethod
    def get_type_different_from_expected(cls, expected_type, got_type):
        """
        Returns a message indicating that the received type is different from the expected one.
        :param expected_type: the expected type
        :type expected_type: TypeSymbol
        :param got_type: the actual type
        :type got_type: type_symbol
        :return: a message
        :rtype: (MessageCode,str)
        """
        from pynestml.symbols.type_symbol import TypeSymbol
        assert (expected_type is not None and isinstance(expected_type, TypeSymbol)), \
            '(PyNestML.Utils.Message) Not a type symbol provided (%s)!' % type(expected_type)
        assert (got_type is not None and isinstance(got_type, TypeSymbol)), \
            '(PyNestML.Utils.Message) Not a type symbol provided (%s)!' % type(got_type)
        message = 'Actual type different from expected. Expected: \'%s\', got: \'%s\'!' % (
            expected_type.print_symbol(), got_type.print_symbol())
        return MessageCode.TYPE_DIFFERENT_FROM_EXPECTED, message

    @classmethod
    def get_buffer_set_to_conductance_based(cls, _buffer):
        """
        Returns a message indicating that a buffer has been set to conductance based.
        :param _buffer: the name of the buffer
        :type _buffer: str
        :return: a message
        :rtype: (MessageCode,str)
        """
        assert (_buffer is not None and isinstance(_buffer, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % type(_buffer)
        message = 'Buffer \'%s\' set to conductance based!' % _buffer
        return MessageCode.BUFFER_SET_TO_CONDUCTANCE_BASED, message

    @classmethod
    def get_ode_updated(cls, variable_name):
        """
        Returns a message indicating that the ode of a variable has been updated.
        :param variable_name: the name of the variable
        :type variable_name: str
        :return: a message
        :rtype: (MessageCode,str)
        """
        assert (variable_name is not None and isinstance(variable_name, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % type(variable_name)
        message = 'Ode of \'%s\' updated!' % variable_name
        return MessageCode.ODE_UPDATED, message

    @classmethod
    def get_no_variable_found(cls, variable_name):
        """
        Returns a message indicating that a variable has not been found.
        :param variable_name: the name of the variable
        :type variable_name: str
        :return: a message
        :rtype: (MessageCode,str)
        """
        assert (variable_name is not None and isinstance(variable_name, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % type(variable_name)
        message = 'No variable \'%s\' found!' % variable_name
        return MessageCode.NO_VARIABLE_FOUND, message

    @classmethod
    def get_buffer_type_not_defined(cls, buffer_name):
        """
        Returns a message indicating that a buffer type has not been defined, thus nS is assumed.
        :param buffer_name: a buffer name
        :type buffer_name: str
        :return: a message
        :rtype: (MessageCode,str)
        """
        assert (buffer_name is not None and isinstance(buffer_name, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % type(buffer_name)
        from pynestml.symbols.predefined_types import PredefinedTypes
        message = 'No buffer type declared of \'%s\', \'%s\' is assumed!' \
                  % (buffer_name, PredefinedTypes.get_type('nS').print_symbol())
        return MessageCode.SPIKE_BUFFER_TYPE_NOT_DEFINED, message

    @classmethod
    def get_neuron_contains_errors(cls, neuron_name):
        """
        Returns a message indicating that a neuron contains errors thus no code is generated.
        :param neuron_name: the name of the neuron
        :type neuron_name: str
        :return: a message
        :rtype: (MessageCode,str)
        """
        assert (neuron_name is not None and isinstance(neuron_name, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % type(neuron_name)
        message = 'Neuron \'' + neuron_name + '\' contains errors. No code generated!'
        return MessageCode.NEURON_CONTAINS_ERRORS, message

    @classmethod
    def get_start_processing_neuron(cls, neuron_name):
        """
        Returns a message indicating that the processing of a neuron is started.
        :param neuron_name: the name of the neuron
        :type neuron_name: str
        :return: a message
        :rtype: (MessageCode,str)
        """
        assert (neuron_name is not None and isinstance(neuron_name, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % type(neuron_name)
        message = 'Starts processing of the neuron \'' + neuron_name + '\''
        return MessageCode.START_PROCESSING_NEURON, message

    @classmethod
    def get_code_generated(cls, neuron_name, path):
        """
        Returns a message indicating that code has been successfully generated for a neuron in a certain path.
        :param neuron_name: the name of the neuron.
        :type neuron_name: str
        :param path: the path to the file
        :type path: str
        :return: a message
        :rtype: (MessageCode,str)
        """
        assert (neuron_name is not None and isinstance(neuron_name, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % type(neuron_name)
        assert (path is not None and isinstance(path, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % type(path)
        message = 'Successfully generated NEST code for the neuron: \'' + neuron_name + '\' in: \'' + path + '\' !'
        return MessageCode.CODE_SUCCESSFULLY_GENERATED, message

    @classmethod
    def get_module_generated(cls, path):
        """
        Returns a message indicating that a module has been successfully generated.
        :param path: the path to the generated file
        :type path: str
        :return: a message
        :rtype: (MessageCode,str)
        """
        assert (path is not None and isinstance(path, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % type(path)
        message = 'Successfully generated NEST module code in \'' + path + '\' !'
        return MessageCode.MODULE_SUCCESSFULLY_GENERATED, message

    @classmethod
    def get_dry_run(cls):
        """
        Returns a message indicating that a dry run is performed.
        :return: a message
        :rtype: (MessageCode,str)
        """
        message = 'Dry mode selected with -dry parameter, no models generated!'
        return MessageCode.DRY_RUN, message

    @classmethod
    def get_variable_used_before_declaration(cls, variable_name):
        """
        Returns a message indicating that a variable is used before declaration.
        :param variable_name: a variable name
        :type variable_name: str
        :return: a message
        :rtype: (MessageCode,str)
        """
        assert (variable_name is not None and isinstance(variable_name, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % type(variable_name)
        message = 'Variable \'%s\' used before declaration!' % variable_name
        return MessageCode.VARIABLE_USED_BEFORE_DECLARATION, message

    @classmethod
    def get_variable_not_defined(cls, variable_name):
        """
        Returns a message indicating that a variable is not defined .
        :param variable_name: a variable name
        :type variable_name: str
        :return: a message
        :rtype: (MessageCode,str)
        """
        assert (variable_name is not None and isinstance(variable_name, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % type(variable_name)
        message = 'Variable \'%s\' not defined!' % variable_name
        return MessageCode.NO_VARIABLE_FOUND, message

    @classmethod
    def get_variable_defined_recursively(cls, variable_name):
        """
        Returns a message indicating that a variable is defined recursively.
        :param variable_name: a variable name
        :type variable_name: str
        :return: a message
        :rtype: (MessageCode,str)
        """
        assert (variable_name is not None and isinstance(variable_name, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % type(variable_name)
        message = 'Variable \'%s\' defined recursively!' % variable_name
        return MessageCode.VARIABLE_DEFINED_RECURSIVELY, message

    @classmethod
    def get_value_assigned_to_buffer(cls, buffer_name):
        """
        Returns a message indicating that a value has been assigned to a buffer.
        :param buffer_name: a buffer name
        :type buffer_name: str
        :return: a message
        :rtype: (MessageCode,str)
        """
        assert (buffer_name is not None and isinstance(buffer_name, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % type(buffer_name)
        message = 'Value assigned to buffer \'%s\'!' % buffer_name
        return MessageCode.VALUE_ASSIGNED_TO_BUFFER, message

    @classmethod
    def get_first_arg_not_shape_or_equation(cls, func_name):
        """
        Indicates that the first argument of an rhs is not an equation or shape.
        :param func_name: the name of the function
        :type func_name: str
        :return: a message
        :rtype: (MessageCode,str)
        """
        assert (func_name is not None and isinstance(func_name, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % type(func_name)
        message = 'First argument of \'%s\' not a shape or equation!' % func_name
        return MessageCode.ARG_NOT_SHAPE_OR_EQUATION, message

    @classmethod
    def get_second_arg_not_a_buffer(cls, func_name):
        """
        Indicates that the second argument of an rhs is not a buffer.
        :param func_name: the name of the function
        :type func_name: str
        :return: a message
        :rtype: (MessageCode,str)
        """
        assert (func_name is not None and isinstance(func_name, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % type(func_name)
        message = 'Second argument of \'%s\' not a buffer!' % func_name
        return MessageCode.ARG_NOT_BUFFER, message

    @classmethod
    def get_wrong_numerator(cls, unit):
        """
        Indicates that the numerator of a unit is not 1.
        :param unit: the name of the unit
        :type unit: str
        :return: a message
        :rtype: (MessageCode,str)
        """
        assert (unit is not None and isinstance(unit, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % type(unit)
        message = 'Numeric numerator of unit \'%s\' not 1!' % unit
        return MessageCode.NUMERATOR_NOT_ONE, message

    @classmethod
    def get_order_not_declared(cls, lhs):
        """
        Indicates that the order has not been declared.
        :param lhs: the name of the variable
        :type lhs: str
        :return: a message
        :rtype: (MessageCode,str)
        """
        assert (lhs is not None and isinstance(lhs, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % lhs
        message = 'Order of differential equation for %s is not declared!' % lhs
        return MessageCode.ORDER_NOT_DECLARED, message

    @classmethod
    def get_current_buffer_specified(cls, name, keyword):
        """
        Indicates that the current buffer has been specified with a type keyword.
        :param name: the name of the buffer
        :type name: str
        :param keyword: the keyword
        :type keyword: list(str)
        :return: a message
        :rtype: (MessageCode,str)
        """
        assert (name is not None and isinstance(name, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % name
        message = 'Current buffer \'%s\' specified with type keywords (%s)!' % (name, keyword)
        return MessageCode.CURRENT_BUFFER_SPECIFIED, message

    @classmethod
    def get_block_not_defined_correctly(cls, block, missing):
        """
        Indicates that a given block has been defined several times or non.
        :param block: the name of the block which is not defined or defined multiple times.
        :type block: str
        :param missing: True if missing, False if multiple times.
        :type missing: bool
        :return: a message
        :rtype: (MessageCode,str)
        """
        assert (block is not None and isinstance(block, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % type(block)
        assert (missing is not None and isinstance(missing, bool)), \
            '(PyNestML.Utils.Message) Not a bool provided (%s)!' % type(missing)
        if missing:
            message = block + ' block not defined, model not correct!'
        else:
            message = block + ' block not unique, model not correct!!'
        return MessageCode.BLOCK_NOT_CORRECT, message

    @classmethod
    def get_equation_var_not_in_init_values_block(cls, variable_name):
        """
        Indicates that a variable in the equations block is not defined in the initial values block.
        :param variable_name: the name of the variable of an equation which is not defined in an equations block
        :type variable_name: str
        :return: a message
        :rtype: (MessageCode,str)
        """
        assert (variable_name is not None and isinstance(variable_name, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % type(variable_name)
        message = 'Ode equation lhs-variable \'%s\' not defined in initial-values block!' % variable_name
        return MessageCode.VARIABLE_NOT_IN_INIT, message

    @classmethod
    def get_wrong_number_of_args(cls, function_call, expected, got):
        """
        Indicates that a wrong number of arguments has been provided to the function call.
        :param function_call: a function call name
        :type function_call: str
        :param expected: the expected number of arguments
        :type expected: int
        :param got: the given number of arguments
        :type got: int
        :return: a message
        :rtype: (MessageCode,str)
        """
        assert (function_call is not None and isinstance(function_call, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % type(function_call)
        assert (expected is not None and isinstance(expected, int)), \
            '(PyNestML.Utils.Message) Not a int provided (%s)!' % type(expected)
        assert (got is not None and isinstance(got, int)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % type(got)
        message = 'Wrong number of arguments in function-call \'%s\'! Expected \'%s\', found \'%s\'.' % (
            function_call, expected, got)
        return MessageCode.WRONG_NUMBER_OF_ARGS, message

    @classmethod
    def get_no_rhs(cls, name):
        """
        Indicates that no right-hand side has been declared for the given variable.
        :param name: the name of the rhs variable
        :type name: str
        :return: a message
        :rtype: (MessageCode,str)
        """
        assert (name is not None and isinstance(name, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % type(name)
        message = 'Function variable \'%s\' has no right-hand side!' % name
        return MessageCode.NO_RHS, message

    @classmethod
    def get_several_lhs(cls, names):
        """
        Indicates that several left hand sides have been defined.
        :param names: a list of variables
        :type names: list(str)
        :return: a message
        :rtype: (MessageCode,str)
        """
        assert (names is not None and isinstance(names, list)), \
            '(PyNestML.Utils.Message) Not a list provided (%s)!' % type(names)
        message = 'Function declared with several variables (%s)!' % names
        return MessageCode.SEVERAL_LHS, message

    @classmethod
    def get_function_redeclared(cls, name, predefined):
        """
        Indicates that a function has been redeclared.
        :param name: the name of the function which has been redeclared.
        :type name: str
        :param predefined: True if function is predefined, otherwise False.
        :type predefined: bool
        :return: a message
        :rtype:(MessageCode,str)
        """
        assert (name is not None and isinstance(name, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % type(name)
        if predefined:
            message = 'Predefined function \'%s\' redeclared!' % name
        else:
            message = 'Function \'%s\' redeclared!' % name
        return MessageCode.FUNCTION_REDECLARED, message

    @classmethod
    def get_no_ode(cls, name):
        """
        Indicates that no ODE has been defined for a variable inside the initial values block.
        :param name: the name of the variable which does not have a defined ode
        :type name: str
        :return: a message
        :rtype: (MessageCode,str)
        """
        assert (name is not None and isinstance(name, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % type(name)
        message = 'Variable \'%s\' not provided with an ODE!' % name
        return MessageCode.NO_ODE, message

    @classmethod
    def get_no_init_value(cls, name):
        """
        Indicates that no initial value has been provided for a given variable.
        :param name: the name of the variable which does not have a initial value
        :type name: str
        :return: a message
        :rtype: (MessageCode,str)
        """
        assert (name is not None and isinstance(name, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % type(name)
        message = 'Initial value of ode variable \'%s\' not provided!' % name
        return MessageCode.NO_INIT_VALUE, message

    @classmethod
    def get_neuron_redeclared(cls, name):
        """
        Indicates that a neuron has been redeclared.
        :param name: the name of the neuron which has been redeclared.
        :type name: str
        :return: a message
        :rtype: (MessageCode,str)
        """
        assert (name is not None and isinstance(name, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % type(name)
        assert (name is not None and isinstance(name, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % type(name)
        message = 'Neuron \'%s\' redeclared!' % name
        return MessageCode.NEURON_REDECLARED, message

    @classmethod
    def get_nest_collision(cls, name):
        """
        Indicates that a collision between a user defined function and a nest function occurred.
        :param name: the name of the function which collides to nest
        :type name: str
        :return: a message
        :rtype: (MessageCode,str)
        """
        assert (name is not None and isinstance(name, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % type(name)
        message = 'Function \'%s\' collides with NEST namespace!' % name
        return MessageCode.NEST_COLLISION, message

    @classmethod
    def get_shape_outside_convolve(cls, name):
        """
        Indicates that a shape variable has been used outside a convolve call.
        :param name: the name of the shape
        :type name: str
        :return: message
        :rtype: (MessageCode,str)
        """
        assert (name is not None and isinstance(name, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % type(name)
        message = 'Shape \'%s\' used outside convolve!' % name
        return MessageCode.SHAPE_OUTSIDE_CONVOLVE, message

    @classmethod
    def get_compilation_unit_name_collision(cls, name, art1, art2):
        """
        Indicates that a name collision with the same neuron inside two artifacts.
        :param name: the name of the neuron which leads to collision
        :type name: str
        :param art1: the first artifact name
        :type art1: str
        :param art2: the second artifact name
        :type art2: str
        :return: a message
        :rtype: (MessageCode,str)
        """
        assert (name is not None and isinstance(name, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % type(name)
        assert (art1 is not None and isinstance(art1, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % type(art1)
        assert (art2 is not None and isinstance(art2, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % type(art2)
        message = 'Name collision of \'%s\' in \'%s\' and \'%s\'!' % (name, art1, art2)
        return MessageCode.NAME_COLLISION, message

    @classmethod
    def get_data_type_not_specified(cls, name):
        """
        Indicates that for a given element no type has been specified.
        :param name: the name of the variable for which a type has not been specified.
        :type name: str
        :return: a message
        :rtype: (MessageCode,str)
        """
        assert (name is not None and isinstance(name, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % type(name)
        message = 'Data type of \'%s\' at not specified!' % name
        return MessageCode.TYPE_NOT_SPECIFIED, message

    @classmethod
    def get_not_type_allowed(cls, name):
        """
        Indicates that a type for the given element is not allowed.
        :param name: the name of the element for which a type is not allowed.
        :type name: str
        :return: a message
        :rtype: (MessageCode,str)
        """
        assert (name is not None and isinstance(name, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % type(name)
        message = 'No data type allowed for \'%s\'!' % name
        return MessageCode.NO_TYPE_ALLOWED, message

    @classmethod
    def get_assignment_not_allowed(cls, name):
        """
        Indicates that an assignment to the given element is not allowed.
        :param name: the name of variable to which an assignment is not allowed.
        :type name: str
        :return: a message
        :rtype: (MessageCode,str)
        """
        assert (name is not None and isinstance(name, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % type(name)
        message = 'Assignment to \'%s\' not allowed!' % name
        return MessageCode.NO_ASSIGNMENT_ALLOWED, message

    @classmethod
    def get_not_a_variable(cls, name):
        """
        Indicates that a given name does not represent a variable.
        :param name: the name of the variable
        :type name: str
        :return: a message
        :rtype: (MessageCode,str)
        """
        assert (name is not None and isinstance(name, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % type(name)
        message = '\'%s\' not a variable!' % name
        return MessageCode.NOT_A_VARIABLE, message

    @classmethod
    def get_multiple_keywords(cls, keyword):
        """
        Indicates that a buffer has been declared with multiple keywords of the same type, e.g., inhibitory inhibitory
        :param keyword: the keyword which has been used multiple times
        :type keyword: str
        :return: a message
        :rtype: (MessageCode,str)
        """
        assert (keyword is not None and isinstance(keyword, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % type(keyword)
        message = 'Buffer specified with multiple \'%s\' keywords!' % keyword
        return MessageCode.MULTIPLE_KEYWORDS, message

    @classmethod
    def get_vector_in_non_vector(cls, vector, non_vector):
        """
        Indicates that a vector has been used in a non-vector declaration.
        :param vector: the vector variable
        :type vector: str
        :param non_vector: the non-vector lhs
        :type non_vector: list(str)
        :return: a message
        :rtype: (MessageCode,str)
        """
        assert (vector is not None and isinstance(vector, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % type(vector)
        assert (non_vector is not None and isinstance(non_vector, list)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % type(non_vector)
        message = 'Vector value \'%s\' used in a non-vector declaration of variables \'%s\'!' % (vector, non_vector)
        return MessageCode.VECTOR_IN_NON_VECTOR, message

    @classmethod
    def get_variable_redeclared(cls, name, predefined):
        """
        Indicates that a given variable has been redeclared. A redeclaration can happen with user defined
        functions or with predefined functions (second parameter).
        :param name: the name of the variable
        :type name: str
        :param predefined: True if a pre-defined variable has been redeclared, otherwise False.
        :type predefined: bool
        :return: a message
        :rtype: (MessageCode,str)
        """
        assert (name is not None and isinstance(name, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % type(name)
        assert (predefined is not None and isinstance(predefined, bool)), \
            '(PyNestML.Utils.Message) Not a bool provided (%s)!' % type(predefined)
        if predefined:
            message = 'Predefined variable \'%s\' redeclared!' % name
        else:
            message = 'Variable \'%s\' redeclared !' % name
        return MessageCode.VARIABLE_REDECLARED, message

    @classmethod
    def get_no_return(cls):
        """
        Indicates that a given function has no return statement although required.
        :return: a message
        :rtype: (MessageCode,str)
        """
        message = 'Return statement expected!'
        return MessageCode.NO_RETURN, message

    @classmethod
    def get_not_last_statement(cls, name):
        """
        Indicates that given statement is not the last statement in a block, e.g., in the case that a return
        statement is not the last statement.
        :param name: the statement.
        :type name: str
        :return: a message
        :rtype: (MessageCode,str)
        """
        assert (name is not None and isinstance(name, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % type(name)
        message = '\'%s\' not the last statement!' % name
        return MessageCode.NOT_LAST_STATEMENT, message

    @classmethod
    def get_function_not_declared(cls, name):
        """
        Indicates that a function, which is not declared, has been used.
        :param name: the name of the function.
        :type name: str
        :return: a message
        :rtype: (MessageCode,str)
        """
        assert (name is not None and isinstance(name, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % type(name)
        message = 'Function \'%s\' is not declared!' % name
        return MessageCode.FUNCTION_NOT_DECLARED, message

    @classmethod
    def get_could_not_resolve(cls, name):
        """
        Indicates that the handed over name could not be resolved to a symbol.
        :param name: the name which could not be resolved
        :type name: str
        :return: a message
        :rtype: (MessageCode,str)
        """
        assert (name is not None and isinstance(name, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % type(name)
        message = 'Could not resolve symbol \'%s\'!' % name
        return MessageCode.SYMBOL_NOT_RESOLVED, message

    @classmethod
    def get_neuron_solved_by_solver(cls, name):
        """
        Indicates that a neuron will be solved by the GSL solver inside the model printing process without any
        modifications to the initial model.
        :param name: the name of the neuron
        :type name: str
        :return: a message
        :rtype: (MessageCode,str)
        """
        assert (name is not None and isinstance(name, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % type(name)
        message = 'The neuron \'%s\' will be solved numerically with GSL solver without modification!' % name
        return MessageCode.NEURON_SOLVED_BY_GSL, message

    @classmethod
    def get_neuron_analyzed(cls, name):
        """
        Indicates that the analysis of a neuron will start.
        :param name: the name of the neuron which will be analyzed.
        :type name: str
        :return: a message
        :rtype: (MessageCode,str)
        """
        assert (name is not None and isinstance(name, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % type(name)
        message = 'The neuron \'%s\' will be analysed!' % name
        return MessageCode.NEURON_ANALYZED, message

    @classmethod
    def get_could_not_be_solved(cls):
        """
        Indicates that the set of equations could not be solved and will remain unchanged.
        :return: a message
        :rtype: (MessageCode,str)
        """
        message = 'Equations or shapes could not be solved. The model remains unchanged!'
        return MessageCode.NEURON_ANALYZED, message

    @classmethod
    def get_equations_solved_exactly(cls):
        """
        Indicates that all equations of the neuron are solved exactly by the solver script.
        :return: a message
        :rtype: (MessageCode,str)
        """
        message = 'Equations are solved exactly!'
        return MessageCode.NEURON_ANALYZED, message

    @classmethod
    def get_equations_solved_by_gls(cls):
        """
        Indicates that the set of ODEs as contained in the model will be solved by the gnu scientific library toolchain.
        :return: a message
        :rtype: (MessageCode,str)
        """
        message = 'Shapes will be solved with GLS!'
        return MessageCode.NEURON_ANALYZED, message

    @classmethod
    def get_ode_solution_not_used(cls):
        """
        Indicates that an ode has been defined in the model but is not used as part of the neurons solution.
        :return: a message
        :rtype: (MessageCode,str)
        """
        message = 'The model has defined an ODE. But its solution is not used in the update state.'
        return MessageCode.NEURON_ANALYZED, message

    @classmethod
    def get_unit_does_not_exist(cls, name):
        """
        Indicates that a unit does not exist.
        :param name: the name of the unit.
        :type name: str
        :return: a new code,message tuple
        :rtype: (MessageCode,str)
        """
        assert (name is not None and isinstance(name, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % type(name)
        message = 'Unit does not exist (%s).' % name
        return MessageCode.NO_UNIT, message

    @classmethod
    def get_not_neuroscience_unit_used(cls, name):
        """
        Indicates that a non-neuroscientific unit, e.g., kg, has been used. Those units can not be converted to
        a corresponding representation in the simulation and are therefore represented by the factor 1.
        :param name: the name of the variable
        :type name: str
        :return: a nes code,message tuple
        :rtype: (MessageCode,str)
        """
        assert (name is not None and isinstance(name, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % type(name)
        message = 'Not convertible unit \'%s\' used, 1 assumed as factor!' % name
        return MessageCode.NOT_NEUROSCIENCE_UNIT, message

    @classmethod
    def get_not_supported_op_in_constraint(cls, op, type_symbol):
        message = "'%s' not compatible with OP '%s'!" % (str(type_symbol), str(op))
        return MessageCode.NOT_COMPATIBLE_OP, message

    @classmethod
    def get_bounds_not_sat(cls, constraint):
        message = "Constraint '%s' is not satisfiable!" % str(constraint)
        return MessageCode.CONSTRAINT_NOT_SAT, message

    @classmethod
    def get_start_value_out_of_bounds(cls, variable, start_value, constraint, is_upper_bound = False):
        if is_upper_bound:
            message = "Start value '%s' of '%s' is over upper bound of constraint '%s'!" % (
                start_value, variable, constraint)
        else:
            message = "Start value '%s' of '%s' is under lower bound of constraint '%s'!" % (
                start_value, variable, constraint)
        return MessageCode.START_VAL_OUT_OF_BOUNDS, message

    @classmethod
    def get_syntax_error_in_model(cls, message):
        return MessageCode.SYNTAX_ERROR, message

    @classmethod
    def get_syntax_warning_in_model(cls, message):
        return MessageCode.SYNTAX_WARNING, message

    @classmethod
    def get_sat_check_only_for_simple_expressions(cls, constraint, left_bound = False):
        if left_bound:
            message = 'SAT check only available for simple bounds! Left bound of %s not simple.' % constraint
        else:
            message = 'SAT check only available for simple bounds! Right bound of %s not simple.' % constraint
        return MessageCode.SAT_CHECK_NOT_POSSIBLE, message

    @classmethod
    def get_void_function_on_rhs(cls, function_name, expression):
        message = "Function '%s' with type 'void' can not be used in an expression! Found in %s." \
                  % (function_name, expression)
        return MessageCode.VOID_FUNCTION_IN_EXPR, message

    @classmethod
    def get_ternary_mismatch(cls, origin, if_true_text, if_not_text, source_position):
        """
        construct an error message indicating that an a comparison operation has incompatible operands
        :param origin: the class reporting the error
        :param if_true_text: plain text of the positive branch of the ternary operator
        :type if_true_text: str
        :param if_not_text: plain text of the negative branch of the ternary operator
        :type if_not_text: str
        :param source_position: The location where the error was encountered
        :type source_position: ASTSourceLocation
        :return: the error message
        :rtype: str
        """
        error_msg_format = "Mismatched conditional alternatives " + if_true_text + " and " + \
                           if_not_text + "-> Assuming real."
        message = cls.__code(origin) + cls.SEPARATOR + error_msg_format + "(" + str(source_position) + ")"
        return MessageCode.TYPE_MISMATCH, message

    @classmethod
    def __code(cls, origin):
        """
        Helper method returning a unique identifier for the various classes that produce and log error messages
        :param origin: the class reporting an error
        :return: identifier unique to that class
        :rtype: str
        """
        from pynestml.visitors.ast_unary_visitor import ASTUnaryVisitor
        if isinstance(origin, ASTUnaryVisitor):
            return "SPL_UNARY_VISITOR"
        from pynestml.visitors.ast_power_visitor import ASTPowerVisitor
        if isinstance(origin, ASTPowerVisitor):
            return "SPL_POW_VISITOR"
        from pynestml.visitors.ast_logical_not_visitor import ASTLogicalNotVisitor
        if isinstance(origin, ASTLogicalNotVisitor):
            return "SPL_LOGICAL_NOT_VISITOR"
        from pynestml.visitors.ast_dot_operator_visitor import ASTDotOperatorVisitor
        if isinstance(origin, ASTDotOperatorVisitor):
            return "SPL_DOT_OPERATOR_VISITOR"
        from pynestml.visitors.ast_line_operation_visitor import ASTLineOperatorVisitor
        if isinstance(origin, ASTLineOperatorVisitor):
            return "SPL_LINE_OPERATOR_VISITOR"
        from pynestml.visitors.ast_no_semantics_visitor import ASTNoSemanticsVisitor
        if isinstance(origin, ASTNoSemanticsVisitor):
            return "SPL_NO_SEMANTICS"
        from pynestml.visitors.ast_comparison_operator_visitor import ASTComparisonOperatorVisitor
        if isinstance(origin, ASTComparisonOperatorVisitor):
            return "SPL_COMPARISON_OPERATOR_VISITOR"
        from pynestml.visitors.ast_binary_logic_visitor import ASTBinaryLogicVisitor
        if isinstance(origin, ASTBinaryLogicVisitor):
            return "SPL_BINARY_LOGIC_VISITOR"
        from pynestml.visitors.ast_condition_visitor import ASTConditionVisitor
        if isinstance(origin, ASTConditionVisitor):
            return "SPL_CONDITION_VISITOR"
        from pynestml.visitors.ast_function_call_visitor import ASTFunctionCallVisitor
        if isinstance(origin, ASTFunctionCallVisitor):
            return "SPL_FUNCTION_CALL_VISITOR"
        return ""

    @classmethod
    def get_non_numeric_type(cls, origin, type_name, source_position):
        """
        construct an error message indicating an expected numeric type is not, in fact, numeric
        :param origin: the class reporting the error
        :param type_name: plain text representation of the wrong type that was encountered
        :type type_name: str
        :param source_position: The location where the error was encountered
        :type source_position: ASTSourceLocation
        :return: the error message
        :rtype: str
        """
        error_msg_format = "Cannot perform an arithmetic operation on a non-numeric type: " + type_name
        message = cls.__code(origin) + cls.SEPARATOR + error_msg_format + "(" + str(source_position) + ")"
        return MessageCode.TYPE_MISMATCH, message

    @classmethod
    def get_type_error(cls, origin, expression_text, source_position):
        """
        construct an error message indicating a generic error in rhs type calculation
        :param origin: the class reporting the error
        :param expression_text: plain text representation of the offending rhs
        :type expression_text: str
        :param source_position: The location where the error was encountered
        :type source_position: ASTSourceLocation
        :return: the error message
        :rtype: str
        """
        error_msg_format = "Cannot determine the type of the rhs: " + expression_text
        message = cls.__code(origin) + cls.SEPARATOR + error_msg_format + "(" + str(source_position) + ")"
        return MessageCode.TYPE_MISMATCH, message

    @classmethod
    def get_implicit_magnitude_conversion_in_expression(cls, origin, parent_node):
        """
        Construct an warning for implicit conversion from parent_node.rhs to parent_node.lhs
        :param origin: the class dropping the warning
        :param parent_node: the addition,subtraction or assignment that requires implicit conversion
        :type: an ASTExpression that is either an Addition or a Subtraction for which an implicit conversion
        has already been determined
        :return: the warning message
        """

        from pynestml.meta_model.ast_expression import ASTExpression
        from pynestml.meta_model.ast_arithmetic_operator import ASTArithmeticOperator
        from pynestml.meta_model.ast_assignment import ASTAssignment
        from pynestml.symbols.symbol import SymbolKind
        assert parent_node is not None and (
                isinstance(parent_node, ASTExpression) or isinstance(parent_node, ASTAssignment))

        target_expression = None
        target_unit = None
        convertee_expression = None
        convertee_unit = None
        operation = None

        if isinstance(parent_node, ASTExpression):
            # code duplication from ASTExpressionTypeVisitor:
            # Rules with binary operators
            if parent_node.get_binary_operator() is not None:
                bin_op = parent_node.get_binary_operator()
                # All these rules employ left and right side expressions.
                if parent_node.get_lhs() is not None:
                    target_expression = parent_node.get_lhs()
                    target_unit = target_expression.type.astropy_unit
                if parent_node.get_rhs() is not None:
                    convertee_expression = parent_node.get_rhs()
                    convertee_unit = convertee_expression.type.astropy_unit
                # Handle all Arithmetic Operators:
                if isinstance(bin_op, ASTArithmeticOperator):
                    # Expr = left=expression (plusOp='+'  | minusOp='-') right=expression
                    if bin_op.is_plus_op:
                        operation = "+"
                    if bin_op.is_minus_op:
                        operation = "-"

        if isinstance(parent_node, ASTAssignment):
            lhs_variable_symbol = parent_node.get_scope().resolve_to_symbol(
                    parent_node.get_variable().get_complete_name(),
                    SymbolKind.VARIABLE)
            operation = "="
            target_expression = parent_node.get_variable()
            target_unit = lhs_variable_symbol.get_type_symbol().astropy_unit
            convertee_expression = parent_node.get_expression()
            convertee_unit = convertee_expression.type.astropy_unit

        assert (target_expression is not None and convertee_expression is not None and
                operation is not None), "Only call this on an addition/subtraction  or assignment after " \
                                        "an implicit conversion wrt unit magnitudes has already been determined"

        error_msg_format = "Non-matching unit types at '" + str(parent_node)
        error_msg_format += "'. Implicit conversion of rhs to lhs"
        error_msg_format += " (units: " + str(convertee_unit) + " and " + \
                            str(target_unit) + " )"
        error_msg_format += " implicitly replaced by '" + str(target_expression) + operation \
                            + convertee_expression.printImplicitVersion() + "'"

        message = (cls.__code(origin) + cls.SEPARATOR + error_msg_format + "("
                   + str(parent_node.get_source_position()) + ")")
        return MessageCode.IMPLICIT_CAST, message

    @classmethod
    def get_unit_base(cls, origin, source_position):
        """
        Construct an error message indicating that a non-int type was given as exponent to a unit type
        :param origin: the class reporting the error
        :param source_position: The location where the error was encountered
        :type source_position: ASTSourceLocation
        :return: the error message
        :rtype: str
        """
        error_msg_format = "With a Unit base, the exponent must be an integer."
        message = cls.__code(origin) + cls.SEPARATOR + error_msg_format + "(" + str(source_position) + ")"
        return MessageCode.TYPE_MISMATCH, message

    @classmethod
    def get_non_constant_exponent(cls, origin, source_position):
        """
        construct an error message indicating that the exponent given to a unit base is not a constant value
        :param origin: the class reporting the error
        :param source_position: The location where the error was encountered
        :type source_position: ASTSourceLocation
        :return: the error message
        :rtype: str
        """
        error_msg_format = "Cannot calculate value of exponent. Must be a constant value!"
        message = cls.__code(origin) + cls.SEPARATOR + error_msg_format + "(" + str(source_position) + ")"
        return MessageCode.TYPE_MISMATCH, message

    @classmethod
    def get_expected_bool(cls, origin, source_position):
        """
        construct an error message indicating that an expected bool value was not found
        :param origin: the class reporting the error
        :param source_position: The location where the error was encountered
        :type source_position: ASTSourceLocation
        :return: the error message
        :rtype: str
        """
        error_msg_format = "Expected a bool!"
        message = cls.__code(origin) + cls.SEPARATOR + error_msg_format + "(" + str(source_position) + ")"
        return MessageCode.TYPE_DIFFERENT_FROM_EXPECTED, message

    @classmethod
    def get_expected_int(cls, origin, source_position):
        """
        construct an error message indicating that an expected int value was not found
        :param origin: the class reporting the error
        :param source_position: The location where the error was encountered
        :type source_position: ASTSourceLocation
        :return: the error message
        :rtype: str
        """
        error_msg_format = "Expected an int!"
        message = cls.__code(origin) + cls.SEPARATOR + error_msg_format + "(" + str(source_position) + ")"
        return MessageCode.TYPE_MISMATCH, message

    @classmethod
    def get_type_mismatch(cls, origin, mismatch_text):
        """
        Construct an error message indicating that an operator is not defined for the handed over types.
        :param origin: the class reporting the error
        :param mismatch_text: the operation with mismatched types printed in plain text
        :type mismatch_text: str
        :return: the error message
        :rtype: str
        """
        error_msg_format = "Operation not defined: " + mismatch_text
        message = cls.__code(origin) + cls.SEPARATOR + error_msg_format
        return MessageCode.NO_SEMANTICS, message

    @classmethod
    def get_add_sub_type_mismatch(cls, origin, lhs_type_text, rhs_type_text, result_type_text, source_position):
        """
        Construct an message indicating that the types of an addition/subtraction are not compatible
        and that the result is implicitly cast to a different type.
        :param origin: the class reporting the error
        :param lhs_type_text: plain text of Lhs type
        :type lhs_type_text: str
        :param rhs_type_text: plain text of Rhs type
        :type rhs_type_text: str
        :param result_type_text: plain text of resulting type (implicit cast)
        :type result_type_text: str
        :param source_position: The location where the error was encountered
        :type source_position: ASTSourceLocation
        :return: the error message
        :rtype: str
        """
        error_msg_format = "Addition/subtraction of " + lhs_type_text + " and " + rhs_type_text + \
                           ". Assuming: " + result_type_text + "."
        message = cls.__code(origin) + cls.SEPARATOR + error_msg_format + "(" + str(source_position) + ")"
        return MessageCode.TYPE_MISMATCH, message

    @classmethod
    def get_no_semantics(cls, origin, expr_text, source_position):
        """
        construct an error message indicating that an rhs is not implemented
        :param origin: the class reporting the error
        :param expr_text: plain text of the unimplemented rhs
        :type expr_text: str
        :param source_position: The location where the error was encountered
        :type source_position: ASTSourceLocation
        :return: the error message
        :rtype: str
        """
        error_msg_format = "This rhs is not implemented: " + expr_text
        message = cls.__code(origin) + cls.SEPARATOR + error_msg_format + "(" + str(source_position) + ")"
        return MessageCode.NO_SEMANTICS, message

    @classmethod
    def get_comparison(cls, origin, source_position):
        """
        Construct an error message indicating that an a comparison operation has incompatible operands.
        :param origin: the class reporting the error
        :param source_position: The location where the error was encountered
        :type source_position: ASTSourceLocation
        :return: the error message
        :rtype: str
        """
        error_msg_format = "Operands of a logical rhs not compatible."
        message = cls.__code(origin) + cls.SEPARATOR + error_msg_format + "(" + str(source_position) + ")"
        return MessageCode.CONDITION_NOT_BOOL, message

    @classmethod
    def get_logic_operands_not_bool(cls, origin, source_position):
        """
        Construct an error message indicating that an a comparison operation has incompatible operands.
        :param origin: the class reporting the error
        :param source_position: The location where the error was encountered
        :type source_position: ASTSourceLocation
        :return: the error message
        :rtype: str
        """
        error_msg_format = "Both operands of a logical rhs must be boolean."
        message = cls.__code(origin) + cls.SEPARATOR + error_msg_format + "(" + str(source_position) + ")"
        return MessageCode.CONDITION_NOT_BOOL, message

    @classmethod
    def get_ternary(cls, origin, source_position):
        """
        Constructs an error message indicating that an a comparison operation has incompatible operands
        :param origin: the class reporting the error
        :param source_position: The location where the error was encountered
        :type source_position: ASTSourceLocation
        :return: the error message
        :rtype: str
        """
        error_msg_format = "The ternary operator condition must be boolean!"
        message = cls.__code(origin) + cls.SEPARATOR + error_msg_format + "(" + str(source_position) + ")"
        return MessageCode.CONDITION_NOT_BOOL, message


class MessageCode(Enum):
    """
    A mapping between codes and the corresponding messages.
    """
    START_PROCESSING_FILE = 0
    TYPE_REGISTERED = 1
    START_SYMBOL_TABLE_BUILDING = 2
    FUNCTION_CALL_TYPE_ERROR = 3
    TYPE_NOT_DERIVABLE = 4
    IMPLICIT_CAST = 5
    CAST_NOT_POSSIBLE = 6
    TYPE_DIFFERENT_FROM_EXPECTED = 7
    ADD_SUB_TYPE_MISMATCH = 8
    BUFFER_SET_TO_CONDUCTANCE_BASED = 9
    ODE_UPDATED = 10
    NO_VARIABLE_FOUND = 11
    SPIKE_BUFFER_TYPE_NOT_DEFINED = 12
    NEURON_CONTAINS_ERRORS = 13
    START_PROCESSING_NEURON = 14
    CODE_SUCCESSFULLY_GENERATED = 15
    MODULE_SUCCESSFULLY_GENERATED = 16
    DRY_RUN = 17
    VARIABLE_USED_BEFORE_DECLARATION = 18
    VARIABLE_DEFINED_RECURSIVELY = 19
    VALUE_ASSIGNED_TO_BUFFER = 20
    ARG_NOT_SHAPE_OR_EQUATION = 21
    ARG_NOT_BUFFER = 22
    NUMERATOR_NOT_ONE = 23
    ORDER_NOT_DECLARED = 24
    CURRENT_BUFFER_SPECIFIED = 25
    BLOCK_NOT_CORRECT = 26
    VARIABLE_NOT_IN_INIT = 27
    WRONG_NUMBER_OF_ARGS = 28
    NO_RHS = 29
    SEVERAL_LHS = 30
    FUNCTION_REDECLARED = 31
    FUNCTION_NOT_DECLARED = 52
    NO_ODE = 32
    NO_INIT_VALUE = 33
    NEURON_REDECLARED = 34
    NEST_COLLISION = 35
    SHAPE_OUTSIDE_CONVOLVE = 36
    NAME_COLLISION = 37
    TYPE_NOT_SPECIFIED = 38
    NO_TYPE_ALLOWED = 39
    NO_ASSIGNMENT_ALLOWED = 40
    NOT_A_VARIABLE = 41
    MULTIPLE_KEYWORDS = 42
    VECTOR_IN_NON_VECTOR = 43
    VARIABLE_REDECLARED = 44
    SOFT_INCOMPATIBILITY = 45
    HARD_INCOMPATIBILITY = 46
    NO_RETURN = 47
    NOT_LAST_STATEMENT = 48
    SYMBOL_NOT_RESOLVED = 49
    TYPE_MISMATCH = 50
    NO_SEMANTICS = 51
    NEURON_SOLVED_BY_GSL = 52
    NEURON_ANALYZED = 53
    NO_UNIT = 54
    NOT_NEUROSCIENCE_UNIT = 55
    INTERNAL_WARNING = 56
    OPERATION_NOT_DEFINED = 57
    CONVOLVE_NEEDS_BUFFER_PARAMETER = 58
    NOT_COMPATIBLE_OP = 59
    CONSTRAINT_NOT_SAT = 60
    START_VAL_OUT_OF_BOUNDS = 61
    SYNTAX_ERROR = 62
    SYNTAX_WARNING = 63
    SAT_CHECK_NOT_POSSIBLE = 64
    VOID_FUNCTION_IN_EXPR = 65
    CONDITION_NOT_BOOL = 66
