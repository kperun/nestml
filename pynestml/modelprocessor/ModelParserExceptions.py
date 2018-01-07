#
# ModelParserExceptions.py
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


class InvalidPathException(Exception):
    """
    This exception is thrown whenever neither a file nor a dir has been handed over. This should not happen.
    """
    pass


class InvalidTargetException(Exception):
    """
    This exception is thrown whenever a not correct target path has been handed over, e.g. a path to a file.
    """
    pass