#
# UnitTypeSymbol.py
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
from pynestml.modelprocessor.TypeSymbol import TypeSymbol


class UnitTypeSymbol(TypeSymbol):

    def __init__(self,_name=None,_unit=None):

    def print_symbol(self):
        result = self.getUnit().printUnit()
        if self.is_buffer:
            result += ' buffer'
        return result

    def __get_concrete_nest_type(self):
        return 'double'