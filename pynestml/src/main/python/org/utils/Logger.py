#
# Logger.py
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


class Logger(object):
    """
    This class represents a logger which can be used to print messages to the screen depending on the logging 
    level.
        LEVELS:
            ALL         Print all received messages.
            WARNING     Print all received warning.
            ERROR      Print all received error.
    Hereby, errors are the most specific level, thus no warnings and non critical messages are shown. If logging 
    level is set to WARNING, only warnings and errors are printed. Only if level is set to ALL, all messages 
    are printed.
    Attributes:
        __log       Stores all messages as received during the execution. Map from id (int) to message+type
    """
    __log = {}
    __currMessage = None
    __loggingLevel = None

    @classmethod
    def initLogger(cls, _loggingLevel=None):
        """
        Initializes the logger.
        :param _loggingLevel: the logging level as required
        :type _loggingLevel: LOGGING_LEVEL
        """
        assert (_loggingLevel is not None and isinstance(_loggingLevel, LOGGING_LEVEL)), \
            '(PyNestML.Logger) No or wrong type of logging-level provided!'
        cls.__loggingLevel = _loggingLevel
        cls.__currMessage = 0
        cls.__log = {}

    @classmethod
    def getLog(cls):
        """
        Returns the overall log of messages.
        :return: dict from id to message+type.
        :rtype: dict(int->str,)
        """
        return cls.__log

    @classmethod
    def logMessage(cls, _message=None, _logLevel=None):
        """
        Logs the handed over message on the handed over level only if current level is set to corresponding level.
        :param _message: a message. 
        :type _message: str
        :param _logLevel: the corresponding log level.
        :type _logLevel: LOGGING_LEVEL
        """
        assert (_message is not None and isinstance(_message, str)), \
            '(PyNestML.Logger) No or wrong type of message provided!'
        assert (_logLevel is not None and isinstance(_logLevel, LOGGING_LEVEL)), \
            '(PyNestML.Logger) No or wrong type of logging-level provided!'
        if cls.__loggingLevel.value <= _logLevel.value:
            cls.__log[cls.__currMessage] = (_message, _logLevel)
            cls.__currMessage += 1
        return

    @classmethod
    def logAndPrintMessage(cls, _message=None, _logLevel=None):
        """
        Logs and prints to the screen the handed over message on the handed over level only if current level is 
        set to corresponding level.
        :param _message: a message. 
        :type _message: str
        :param _logLevel: the corresponding log level.
        :type _logLevel: LOGGING_LEVEL 
        """
        assert (_message is not None and isinstance(_message, str)), \
            '(PyNestML.Logger) No or wrong type of message provided!'
        assert (_logLevel is not None and isinstance(_logLevel, LOGGING_LEVEL)), \
            '(PyNestML.Logger) No or wrong type of logging-level provided!'
        if cls.__loggingLevel.value <= _logLevel.value:
            cls.__log[cls.__currMessage] = (_message, _logLevel)
            cls.__currMessage += 1
            print('[' + str(_logLevel.name) + ']:' + str(_message))
        return

    @classmethod
    def stringToLevel(cls, _string=None):
        """
        Returns the logging level corresponding to the handed over string. If no such exits, returns None.
        :param _string: a single string representing the level.
        :type _string: str
        :return: a single logging level.
        :rtype: LOGGING_LEVEL
        """
        if type(_string) != str:
            return LOGGING_LEVEL.ERROR
        elif _string == 'ALL':
            return LOGGING_LEVEL.ALL
        elif _string == 'WARNING' or _string == 'WARNINGS':
            return LOGGING_LEVEL.WARNING
        elif _string == 'ERROR' or _string == 'ERRORS':
            return LOGGING_LEVEL.ERROR
        elif _string == 'NO':
            return LOGGING_LEVEL.NO
        else:
            return LOGGING_LEVEL.ERROR


class LOGGING_LEVEL(Enum):
    """
    Different types of logging levels, this part can be extended.
    """
    ALL = 0
    WARNING = 1
    ERROR = 2
    NO = 3