#
# ast_utils.py
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
from pynestml.meta_model.ast_function_call import ASTFunctionCall
from pynestml.symbols.predefined_functions import PredefinedFunctions
from pynestml.symbols.symbol import SymbolKind
from pynestml.utils.logger import Logger, LoggingLevel


class ASTUtils(object):
    """
    A collection of helpful methods.
    """
    epsilon = 0.0001

    @classmethod
    def get_all_neurons(cls, list_of_compilation_units):
        """
        For a list of compilation units, it returns a list containing all neurons defined in all compilation
        units.
        :param list_of_compilation_units: a list of compilation units.
        :type list_of_compilation_units: list(ASTNestMLCompilationUnit)
        :return: a list of neurons
        :rtype: list(ASTNeuron)
        """
        ret = list()
        for compilationUnit in list_of_compilation_units:
            ret.extend(compilationUnit.get_neuron_list())
        return ret

    @classmethod
    def is_small_stmt(cls, ast):
        """
        Indicates whether the handed over meta_model is a small statement. Used in the template.
        :param ast: a single meta_model object.
        :type ast: AST_
        :return: True if small stmt, otherwise False.
        :rtype: bool
        """
        from pynestml.meta_model.ast_small_stmt import ASTSmallStmt
        return isinstance(ast, ASTSmallStmt)

    @classmethod
    def is_compound_stmt(cls, ast):
        """
        Indicates whether the handed over meta_model is a compound statement. Used in the template.
        :param ast: a single meta_model object.
        :type ast: AST_
        :return: True if compound stmt, otherwise False.
        :rtype: bool
        """
        from pynestml.meta_model.ast_compound_stmt import ASTCompoundStmt
        return isinstance(ast, ASTCompoundStmt)

    @classmethod
    def is_integrate(cls, function_call):
        """
        Checks if the handed over function call is a ode integration function call.
        :param function_call: a single function call
        :type function_call: ASTFunctionCall
        :return: True if ode integration call, otherwise False.
        :rtype: bool
        """
        return function_call.get_name() == PredefinedFunctions.INTEGRATE_ODES

    @classmethod
    def is_spike_input(cls, body):
        # type: (ASTBody) -> bool
        """
        Checks if the handed over neuron contains a spike input buffer.
        :param body: a single body element.
        :type body: ASTBody
        :return: True if spike buffer is contained, otherwise false.
        :rtype: bool
        """
        from pynestml.utils.ast_helper import ASTHelper
        from pynestml.meta_model.ast_body import ASTBody
        inputs = (inputL for inputL in ASTHelper.get_input_block_from_body(body).get_input_lines())
        for inputL in inputs:
            if inputL.is_spike():
                return True
        return False

    @classmethod
    def is_current_input(cls, body):
        """
        Checks if the handed over neuron contains a current input buffer.
        :param body: a single body element.
        :type body: ASTBody
        :return: True if current buffer is contained, otherwise false.
        :rtype: bool
        """
        from pynestml.utils.ast_helper import ASTHelper
        inputs = (inputL for inputL in ASTHelper.get_input_block_from_body(body).get_input_lines())
        for inputL in inputs:
            if inputL.is_current():
                return True
        return False

    @classmethod
    def compute_type_name(cls, data_type):
        """
        Computes the representation of the data type.
        :param data_type: a single data type.
        :type data_type: ASTDataType
        :return: the corresponding representation.
        :rtype: str
        """
        if data_type.is_boolean:
            return 'boolean'
        elif data_type.is_integer:
            return 'integer'
        elif data_type.is_real:
            return 'real'
        elif data_type.is_string:
            return 'string'
        elif data_type.is_void:
            return 'void'
        elif data_type.is_unit_type():
            return str(data_type)
        else:
            Logger.log_message(message='Type could not be derived!', log_level=LoggingLevel.ERROR)
            return ''

    @classmethod
    def deconstruct_assignment(cls, lhs = None, is_plus = False, is_minus = False, is_times = False, is_divide = False,
                               _rhs = None):
        """
        From lhs and rhs it constructs a new rhs which corresponds to direct assignment.
        E.g.: a += b*c -> a = a + b*c
        :param lhs: a lhs rhs
        :type lhs: ASTExpression or ASTSimpleExpression
        :param is_plus: is plus assignment
        :type is_plus: bool
        :param is_minus: is minus assignment
        :type is_minus: bool
        :param is_times: is times assignment
        :type is_times: bool
        :param is_divide: is divide assignment
        :type is_divide: bool
        :param _rhs: a rhs rhs
        :type _rhs: ASTExpression or ASTSimpleExpression
        :return: a new direct assignment rhs.
        :rtype: ASTExpression
        """
        from pynestml.visitors.ast_symbol_table_visitor import ASTSymbolTableVisitor
        from pynestml.meta_model.ast_node_factory import ASTNodeFactory
        assert ((is_plus + is_minus + is_times + is_divide) == 1), \
            '(PyNestML.CodeGeneration.Utils) Type of assignment not correctly specified!'
        if is_plus:
            op = ASTNodeFactory.create_ast_arithmetic_operator(is_plus_op=True,
                                                               source_position=_rhs.get_source_position())
        elif is_minus:
            op = ASTNodeFactory.create_ast_arithmetic_operator(is_minus_op=True,
                                                               source_position=_rhs.get_source_position())
        elif is_times:
            op = ASTNodeFactory.create_ast_arithmetic_operator(is_times_op=True,
                                                               source_position=_rhs.get_source_position())
        else:
            op = ASTNodeFactory.create_ast_arithmetic_operator(is_div_op=True,
                                                               source_position=_rhs.get_source_position())
        var_expr = ASTNodeFactory.create_ast_simple_expression(variable=lhs,
                                                               source_position=lhs.get_source_position())
        var_expr.update_scope(lhs.get_scope())
        op.update_scope(lhs.get_scope())
        rhs_in_brackets = ASTNodeFactory.create_ast_expression(is_encapsulated=True, expression=_rhs,
                                                               source_position=_rhs.get_source_position())
        rhs_in_brackets.update_scope(_rhs.get_scope())
        expr = ASTNodeFactory.create_ast_compound_expression(lhs=var_expr, binary_operator=op, rhs=rhs_in_brackets,
                                                             source_position=_rhs.get_source_position())
        expr.update_scope(lhs.get_scope())
        # update the symbols
        expr.accept(ASTSymbolTableVisitor())
        return expr

    @classmethod
    def get_alias_symbols(cls, ast):
        """
        For the handed over meta_model, this method collects all functions aka. aliases in it.
        :param ast: a single meta_model node
        :type ast: AST_
        :return: a list of all alias variable symbols
        :rtype: list(VariableSymbol)
        """
        ret = list()
        from pynestml.visitors.ast_higher_order_visitor import ASTHigherOrderVisitor
        from pynestml.meta_model.ast_variable import ASTVariable
        res = list()

        def loc_get_vars(node):
            if isinstance(node, ASTVariable):
                res.append(node)

        ast.accept(ASTHigherOrderVisitor(visit_funcs=loc_get_vars))

        for var in res:
            if '\'' not in var.get_complete_name():
                symbol = ast.get_scope().resolve_to_symbol(var.get_complete_name(), SymbolKind.VARIABLE)
                if symbol.is_function:
                    ret.append(symbol)
        return ret

    @classmethod
    def is_castable_to(cls, type_a, type_b):
        """
        Indicates whether typeA can be casted to type b. E.g., in Nest, a unit is always casted down to real, thus
        a unit where unit is expected is allowed.
        :param type_a: a single TypeSymbol
        :type type_a: TypeSymbol
        :param type_b: a single TypeSymbol
        :type type_b: TypeSymbol
        :return: True if castable, otherwise False
        :rtype: bool
        """
        # we can always cast from unit to real
        if type_a.is_unit and type_b.is_real:
            return True
        elif type_a.is_boolean and type_b.is_real:
            return True
        elif type_a.is_real and type_b.is_boolean:
            return True
        elif type_a.is_integer and type_b.is_real:
            return True
        elif type_a.is_real and type_b.is_integer:
            return True
        else:
            return False

    @classmethod
    def differs_in_magnitude(cls, type_a, type_b):
        """
        Indicates whether both type represent the same unit but with different magnitudes. This
        case is still valid, e.g., mV can be assigned to volt.
        :param type_a: a type
        :type type_a:  TypeSymbol
        :param type_b: a type
        :type type_b: TypeSymbol
        :return: True if both elements equal or differ in magnitude, otherwise False.
        :rtype: bool
        """
        if type_a.equals(type_b):
            return True
        # in the case that we don't deal with units, there are no magnitudes
        if not (type_a.is_unit() and type_b.is_unit()):
            return False
        # if it represents the same unit, if we disregard the prefix and simplify it
        unit_a = type_a.get_unit().unit
        unit_b = type_b.get_unit().unit
        # if isinstance(unit_a,)
        from astropy import units
        # TODO: consider even more complex cases which can be resolved to the same unit?
        if isinstance(unit_a, units.PrefixUnit) and isinstance(type_b, units.PrefixUnit) \
                and unit_a.physical_type == unit_b.physical_type:
            return True
        return False

    @classmethod
    def get_all(cls, ast, node_type):
        """
        Finds all meta_model which are part of the tree as spanned by the handed over meta_model.
        The type has to be specified.
        :param ast: a single meta_model node
        :type ast: ASTNode
        :param node_type: the type
        :type node_type: ASTNode
        :return: a list of all meta_model of the specified type
        :rtype: list[ASTNode]
        """
        from pynestml.visitors.ast_higher_order_visitor import ASTHigherOrderVisitor
        ret = list()

        def loc_get_all_of_type(node):
            if isinstance(node, node_type):
                ret.append(node)

        ast.accept(ASTHigherOrderVisitor(visit_funcs=loc_get_all_of_type))
        return ret

    @classmethod
    def get_vectorized_variable(cls, ast, scope):
        """
        Returns all variable symbols which are contained in the scope and have a size parameter.
        :param ast: a single meta_model
        :type ast: ASTNode
        :param scope: a scope object
        :type scope: Scope
        :return: the first element with the size parameter
        :rtype: VariableSymbol
        """
        from pynestml.meta_model.ast_variable import ASTVariable
        from pynestml.symbols.symbol import SymbolKind
        variables = (var for var in cls.get_all(ast, ASTVariable) if
                     scope.resolve_to_symbol(var.get_complete_name(), SymbolKind.VARIABLE))
        for var in variables:
            symbol = scope.resolve_to_symbol(var.get_complete_name(), SymbolKind.VARIABLE)
            if symbol is not None and symbol.has_vector_parameter():
                return symbol
        return None

    @classmethod
    def get_function_call(cls, ast, function_name):
        """
        Collects for a given name all function calls in a given meta_model node.
        :param ast: a single node
        :type ast: ASTNode
        :param function_name: the name of the function
        :type function_name: str
        :return: a list of all function calls contained in _ast
        :rtype: list(ASTFunctionCall)
        """
        from pynestml.visitors.ast_higher_order_visitor import ASTHigherOrderVisitor
        from pynestml.meta_model.ast_function_call import ASTFunctionCall
        ret = list()

        def loc_get_function(node):
            if isinstance(node, ASTFunctionCall) and node.get_name() == function_name:
                ret.append(node)

        ast.accept(ASTHigherOrderVisitor(loc_get_function, list()))
        return ret

    @classmethod
    def get_tuple_from_single_dict_entry(cls, dict_entry):
        """
        For a given dict of length 1, this method returns a tuple consisting of (key,value)
        :param dict_entry: a dict of length 1
        :type dict_entry:  dict
        :return: a single tuple
        :rtype: tuple
        """
        if len(dict_entry.keys()) == 1:
            # key() is not an actual list, thus indexing is not possible.
            for keyIter in dict_entry.keys():
                key = keyIter
                value = dict_entry[key]
                return key, value
        else:
            return None, None

    @classmethod
    def needs_arguments(cls, ast_function_call):
        """
        Indicates whether a given function call has any arguments
        :param ast_function_call: a function call
        :type ast_function_call: ASTFunctionCall
        :return: True if arguments given, otherwise false
        :rtype: bool
        """
        return len(ast_function_call.get_args()) > 0

    @classmethod
    def create_internal_block(cls, neuron):
        """
        Creates a single internal block in the handed over neuron.
        :param neuron: a single neuron
        :type neuron: ASTNeuron
        :return: the modified neuron
        :rtype: ASTNeuron
        """
        from pynestml.meta_model.ast_node_factory import ASTNodeFactory
        from pynestml.utils.ast_helper import ASTHelper
        if ASTHelper.get_internals_block_from_neuron(neuron) is None:
            internal = ASTNodeFactory.create_ast_block_with_variables(False, False, True, False, list(),
                                                                      ASTSourcePosition.get_added_source_position())
            neuron.get_body().get_body_elements().append(internal)
        return neuron

    @classmethod
    def create_state_block(cls, neuron):
        """
        Creates a single internal block in the handed over neuron.
        :param neuron: a single neuron
        :type neuron: ASTNeuron
        :return: the modified neuron
        :rtype: ASTNeuron
        """
        # local import since otherwise circular dependency
        from pynestml.meta_model.ast_node_factory import ASTNodeFactory
        from pynestml.utils.ast_helper import ASTHelper
        if ASTHelper.get_internals_block_from_neuron(neuron) is None:
            state = ASTNodeFactory.create_ast_block_with_variables(True, False, False, False, list(),
                                                                   ASTSourcePosition.get_added_source_position())
            neuron.get_body().get_body_elements().append(state)
        return neuron

    @classmethod
    def create_initial_values_block(cls, neuron):
        """
        Creates a single initial values block in the handed over neuron.
        :param neuron: a single neuron
        :type neuron: ASTNeuron
        :return: the modified neuron
        :rtype: ASTNeuron
        """
        # local import since otherwise circular dependency
        from pynestml.meta_model.ast_node_factory import ASTNodeFactory
        from pynestml.utils.ast_helper import ASTHelper
        if ASTHelper.get_initial_block_from_neuron(neuron) is None:
            initial_values = ASTNodeFactory. \
                create_ast_block_with_variables(False, False, False, True, list(),
                                                ASTSourcePosition.get_added_source_position())
            neuron.get_body().get_body_elements().append(initial_values)
        return neuron

    @classmethod
    def contains_sum_call(cls, variable):
        """
        Indicates whether the declaring rhs of this variable symbol has a x_sum or convolve in it.
        :return: True if contained, otherwise False.
        :rtype: bool
        """
        from pynestml.utils.ast_helper import ASTHelper
        if not variable.get_declaring_expression():
            return False
        else:
            for func in ASTHelper.get_function_calls_from_expression(variable.get_declaring_expression()):
                if func.get_name() == PredefinedFunctions.CONVOLVE or \
                        func.get_name() == PredefinedFunctions.CURR_SUM or \
                        func.get_name() == PredefinedFunctions.COND_SUM:
                    return True
        return False

    @classmethod
    def add_to_state_block(cls, neuron, declaration):
        """
        Adds the handed over declaration the state block
        :param neuron: a single neuron instance
        :type neuron: ASTNeuron
        :param declaration: a single declaration
        :type declaration: ASTDeclaration
        """
        from pynestml.utils.ast_helper import ASTHelper
        if ASTHelper.get_state_block_from_neuron(neuron) is None:
            ASTUtils.create_state_block(neuron)
        ASTHelper.get_state_block_from_neuron(neuron).get_declarations().append(declaration)
        return

    @classmethod
    def convert_variable_name_to_model_notation(cls, variable):
        """
        This Function is used to convert a supported name (aka. defined with d instead of '), to an unsupported one.
        It is used to find all variables which have to provided with a ode declaration.
        """
        from pynestml.meta_model.ast_node_factory import ASTNodeFactory
        from pynestml.meta_model.ast_variable import ASTVariable
        # type: ASTVariable -> str

        name = variable.get_name()
        diff_order = 0
        while True:
            if name.endswith('__d'):
                diff_order += 1
                name = name[:-3]
                break
            elif name.endswith('d'):
                diff_order += 1
                name = name[:-1]
            else:
                break
        return ASTNodeFactory.create_ast_variable(name=name, differential_order=diff_order)

    @classmethod
    def convert_variable_name_to_generator_notation(cls, variable):
        """
        This function is used to convert an unsupported name in the codegeneration (aka g_in') to a supported
        one (e.g., g_in_d). It decreases the unsupported order by one.
        """
        from pynestml.meta_model.ast_variable import ASTVariable
        from pynestml.meta_model.ast_node_factory import ASTNodeFactory
        # type: ASTVariable -> str

        name = variable.get_name()
        diff_order = variable.get_differental_order()
        if diff_order > 0:
            import re
            pattern = re.compile('w*_((d)*)\b')
            if pattern.match(name):
                name += 'd'
            else:
                name += '__d'
            diff_order -= 1
        return ASTNodeFactory.create_ast_variable(name=name, differential_order=diff_order)

    @classmethod
    def get_lower_bound_of_constraint(cls, constraint):
        # type: (ASTConstraint) -> list[(ASTSimpleExpression,ASTComparisonOperator)]
        from pynestml.meta_model.ast_constraint import ASTConstraint
        from pynestml.meta_model.ast_simple_expression import ASTSimpleExpression
        from pynestml.meta_model.ast_comparison_operator import ASTComparisonOperator
        ret = list()
        r_bound = constraint.right_bound
        r_bound_type = constraint.right_bound_type
        # the case of the right bound being > or >=
        if r_bound is not None and (r_bound_type.is_gt or r_bound_type.is_ge):
            ret.append(r_bound)
        # now the other side,e.g., 100mV =< V_m >= 200mV
        l_bound = constraint.left_bound
        l_bound_type = constraint.left_bound_type
        if l_bound is not None and (l_bound_type.is_lt or l_bound_type.is_le):
            ret.append(l_bound)
        return ret

    @classmethod
    def get_upper_bound_of_constraint(cls, constraint):
        # type: (ASTConstraint) -> list[(ASTSimpleExpression,ASTComparisonOperator)]
        from pynestml.meta_model.ast_constraint import ASTConstraint
        from pynestml.meta_model.ast_simple_expression import ASTSimpleExpression
        from pynestml.meta_model.ast_comparison_operator import ASTComparisonOperator
        ret = list()
        r_bound = constraint.right_bound
        r_bound_type = constraint.right_bound_type
        # the case of the right bound being < or <=
        if r_bound is not None and (r_bound_type.is_lt or r_bound_type.is_le):
            ret.append(r_bound)
        # now the other side,e.g., 100mV >= V_m <= 200mV
        l_bound = constraint.left_bound
        l_bound_type = constraint.left_bound_type
        if l_bound is not None and (l_bound_type.is_gt or l_bound_type.is_ge):
            ret.append(l_bound)
        return ret

    @classmethod
    def has_constraints(cls, variable, neuron):
        # type: (ASTVariable,ASTNeuron) -> bool
        from pynestml.meta_model.ast_variable import ASTVariable
        from pynestml.meta_model.ast_neuron import ASTNeuron
        from pynestml.utils.ast_helper import ASTHelper
        if ASTHelper.get_constraint_block_from_neuron(neuron) is None:
            return False
        for const in ASTHelper.get_constraint_block_from_neuron(neuron).constraints:
            if const.variable.get_complete_name() == variable.name:
                return True

    @classmethod
    def get_constraints_of_variable(cls, variable, neuron):
        # type: (ASTVariable,ASTNeuron) -> list[ASTConstraint]
        from pynestml.meta_model.ast_variable import ASTVariable
        from pynestml.meta_model.ast_neuron import ASTNeuron
        from pynestml.meta_model.ast_constraint import ASTConstraint
        from pynestml.utils.ast_helper import ASTHelper
        ret = list()
        if ASTHelper.get_constraint_block_from_neuron(neuron) is None:
            return ret
        for const in ASTHelper.get_constraint_block_from_neuron(neuron).constraints:
            if const.variable.get_complete_name() == variable.name:
                ret.append(const)
        return ret

    @classmethod
    def separate_constraint(cls, constraint):
        # type: (ASTConstraint) -> list[(ASTSimpleExpression,ASTComparisonOperator)]
        from pynestml.meta_model.ast_constraint import ASTConstraint
        from pynestml.meta_model.ast_simple_expression import ASTSimpleExpression
        from pynestml.meta_model.ast_comparison_operator import ASTComparisonOperator
        ret = list()
        if constraint.left_bound is not None:
            ret.append((constraint.left_bound, constraint.left_bound_type))
        if constraint.right_bound is not None:
            ret.append((constraint.right_bound, constraint.right_bound_type))
        return ret

    @classmethod
    def get_variable_constraints(cls, neuron):
        # type: (ASTNeuron) -> list[ASTConstraint]
        from pynestml.meta_model.ast_neuron import ASTNeuron
        from pynestml.meta_model.ast_constraint import ASTConstraint
        from pynestml.symbols.variable_symbol import BlockType
        from pynestml.utils.ast_helper import ASTHelper
        ret = list()
        if ASTHelper.get_constraint_block_from_neuron(neuron) is None:
            return ret

        for const in ASTHelper.get_constraint_block_from_neuron(neuron).constraints:
            symbol = neuron.get_scope().resolve_to_symbol(const.variable.get_complete_name(), SymbolKind.VARIABLE)
            if symbol is None:
                # the constrained var is not defined, this should be reported by cocos
                continue
            if symbol.block_type == BlockType.STATE or symbol.block_type == BlockType.INITIAL_VALUES:
                # in this case it is a constraint for a state or a initial values var
                ret.append(const)
        return ret

    @classmethod
    def negate_comparison_op(cls, op):
        # type: (ASTComparisonOperator) -> ASTComparisonOperator
        from pynestml.meta_model.ast_comparison_operator import ASTComparisonOperator
        from pynestml.meta_model.ast_node_factory import ASTNodeFactory
        if op.is_gt:
            return ASTNodeFactory.create_ast_comparison_operator(is_le=True)
        if op.is_ge:
            return ASTNodeFactory.create_ast_comparison_operator(is_lt=True)
        if op.is_ne2:
            return ASTNodeFactory.create_ast_comparison_operator(is_eq=True)
        if op.is_ne:
            return ASTNodeFactory.create_ast_comparison_operator(is_eq=True)
        if op.is_eq:
            return ASTNodeFactory.create_ast_comparison_operator(is_ne=True)
        if op.is_le:
            return ASTNodeFactory.create_ast_comparison_operator(is_gt=True)
        if op.is_lt:
            return ASTNodeFactory.create_ast_comparison_operator(is_ge=True)

    @classmethod
    def get_next_valid_value(cls, op, expr):
        # type: (ASTComparisonOperator,ASTExpression) -> ASTExpression
        """
        This function returns the next valid value for a constraint. For instance, in cases where
        the constraint is -70mV < V_m, we can not simply set V_m to -70mV, since this would contradict the constraint.
        We have to set is to -70mV + epsilon where epsilon is a infinitesimal small value. For epsilon ,we
        use 0.0001.
        :param op: a single operator
        :type op: ASTComparisonOperator
        :param expr: a single expression
        :type expr: ASTExpression
        :return: a modified expression
        :rtype: ASTExpression
        """
        from pynestml.meta_model.ast_comparison_operator import ASTComparisonOperator
        from pynestml.meta_model.ast_node_factory import ASTNodeFactory
        from pynestml.meta_model.ast_expression import ASTExpression
        from pynestml.meta_model.ast_source_location import ASTSourceLocation
        # in this case we simply set to the bound, since still sat
        if op.is_ge or op.is_eq or op.is_le:
            return expr

        epsilon = ASTNodeFactory.create_ast_simple_expression(numeric_literal=cls.epsilon)
        location = ASTSourceLocation.get_added_source_position()
        if op.is_gt:
            plus_op = ASTNodeFactory.create_ast_arithmetic_operator(is_plus_op=True, source_position=location)
            return ASTNodeFactory.create_ast_compound_expression(lhs=expr, binary_operator=plus_op, rhs=epsilon,
                                                                 source_position=location)
        if op.is_lt:
            minus_op = ASTNodeFactory.create_ast_arithmetic_operator(is_minus_op=True, source_position=location)
            return ASTNodeFactory.create_ast_compound_expression(lhs=expr, binary_operator=minus_op, rhs=epsilon,
                                                                 source_position=location)

        if op.is_ne2 or op.is_ne:
            minus_op = ASTNodeFactory.create_ast_assignment(is_compound_minus=True, source_position=location)
            return ASTNodeFactory.create_ast_compound_expression(lhs=expr, binary_operator=minus_op, rhs=epsilon,
                                                                 source_position=location)

    @classmethod
    def resolve_self_to_symbol(cls, ast):
        # type: (ASTVariable) -> VariableSymbol
        from pynestml.meta_model.ast_variable import ASTVariable
        from pynestml.symbols.variable_symbol import VariableSymbol
        if isinstance(ast, ASTVariable):
            return ast.get_scope().resolve_to_symbol(ast.get_complete_name(), SymbolKind.VARIABLE)

    @classmethod
    def get_parent(cls, root, child_node):
        """
        Returns the parent of child_node. Here, the root has to be the node object, to start a traversal of the ast
        correctly. Preferably the neuron root, i.e., ASTNeuron.
        :param root: a single neuron instance
        :type root: ASTNode
        :param child_node: a single child node
        :type child_node: ASTNode
        :return: ASTNode
        """
        from pynestml.visitors.ast_parent_collector_visitor import ASTParentCollectorVisitor
        visitor = ASTParentCollectorVisitor(to_find=child_node)
        root.accept(visitor)
        return visitor.parent
