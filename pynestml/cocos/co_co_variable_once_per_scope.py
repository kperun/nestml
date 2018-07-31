#
# co_co_variable_once_per_scope.py
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
from pynestml.symbols.symbol import SymbolKind
from pynestml.utils.logger import Logger, LoggingLevel
from pynestml.utils.messages import Messages


class CoCoVariableOncePerScope(CoCo):
    """
    This coco ensures that each variables is defined at most once per scope, thus no redeclaration occurs.
    """

    def check_co_co(self, node):
        """
        Checks if each variable is defined at most once per scope. Obviously, this test does not check if a declaration
        is shadowed by an embedded scope.
        :param node: a single neuron
        :type node: ASTNeuron
        """
        self.__check_scope(node, node.get_scope())

    def __check_scope(self, neuron, scope):
        """
        Checks a single scope and proceeds recursively.
        :param neuron: a single neuron object, required for correct printing of messages.
        :type neuron: ASTNeuron
        :param scope: a single scope to check.
        :type scope: Scope
        """
        checked = list()
        for sym1 in scope.get_symbols_in_this_scope():
            for sym2 in scope.get_symbols_in_this_scope():
                if (sym1 is not sym2 and sym1.get_symbol_name() == sym2.get_symbol_name() and
                        sym1.get_symbol_kind() == sym2.get_symbol_kind() and
                        sym1.get_symbol_kind() == SymbolKind.VARIABLE and
                        sym2 not in checked):
                    if sym1.is_predefined:
                        code, message = Messages.get_variable_redeclared(sym1.get_symbol_name(), True)
                        Logger.log_message(error_position=sym2.get_referenced_object().get_source_position(),
                                           neuron=neuron, log_level=LoggingLevel.ERROR, code=code, message=message)
                    elif sym2.is_predefined:
                        code, message = Messages.get_variable_redeclared(sym1.get_symbol_name(), True)
                        Logger.log_message(error_position=sym1.get_referenced_object().get_source_position(),
                                           neuron=neuron, log_level=LoggingLevel.ERROR, code=code, message=message)
                    elif sym1.get_referenced_object().get_source_position().before(
                            sym2.get_referenced_object().get_source_position()):
                        code, message = Messages.get_variable_redeclared(sym1.get_symbol_name(), False)
                        Logger.log_message(error_position=sym2.get_referenced_object().get_source_position(),
                                           neuron=neuron, log_level=LoggingLevel.ERROR, code=code, message=message)
            checked.append(sym1)
        for scope in scope.get_scopes():
            self.__check_scope(neuron, scope)
        return
