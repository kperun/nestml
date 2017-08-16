"""
@author kperun
TODO header
"""
from src.main.python.org.nestml.ast.ASTUnaryOperator import ASTUnaryOperator
from src.main.python.org.nestml.ast.ASTSimpleExpression import ASTSimpleExpression

class ASTExpression:
    """
    ASTExpr, i.e., several subexpressions combined by one or more operators, e.g., 10mV + V_m - (V_reset * 2)/ms ....
    or a simple expression, e.g. 10mV.
    Grammar: 
      expression : leftParentheses='(' expression rightParentheses=')'
             | <assoc=right> base=expression powOp='**' exponent=expression
             | unaryOperator term=expression
             | left=expression (timesOp='*' | divOp='/' | moduloOp='%') right=expression
             | left=expression (plusOp='+'  | minusOp='-') right=expression
             | left=expression bitOperator right=expression
             | left=expression comparisonOperator right=expression
             | logicalNot='not' expression
             | left=expression logicalOperator right=expression
             | condition=expression '?' ifTrue=expression ':' ifNot=expression
             | simpleExpression
             ;
    """
    # encapsulated or with unary operator or with a logical not or just a simple expression.
    __hasLeftParentheses = False
    __hasRightParentheses = False
    __isLogicalNot = False
    __unaryOperator = None
    __expression = None
    # lhs and rhs combined by an operator
    __lhs = None
    __binaryOperator = None
    __rhs = None
    # ternary operator
    __condition = None
    __ifTrue = None
    __ifNot = None

    def __init__(self, _hasLeftParentheses: bool = False, _hasRightParentheses: bool = False,
                 _unaryOperator: ASTUnaryOperator = None,
                 _isLogicalNot: bool = False,
                 _expression=None,
                 _lhs=None,
                 _binaryOperator=None,
                 _rhs=None,
                 _condition=None,
                 _ifTrue=None,
                 _ifNot=None):
        """
        Standard constructor.
        :param _hasLeftParentheses: is encapsulated in brackets (left). 
        :type _hasLeftParentheses: bool
        :param _hasRightParentheses: is encapsulated in brackets (right).
        :type _hasRightParentheses: bool
        :param _unaryOperator: combined by unary operator, e.g., ~.
        :type _unaryOperator: ASTUnaryOperator
        :param _isLogicalNot: is a negated expression.
        :type _isLogicalNot: bool
        :param _expression: the expression either encapsulated in brackets or negated or with a with a unary op, or a simple expression.
        :type _expression: ASTExpression
        :param _lhs: the left-hand side expression.
        :type _lhs: ASTExpression
        :param _binaryOperator: a binary operator, e.g., a comparison operator or a logical operator.
        :type _binaryOperator: ASTLogicalOperator,ASTComparisonOperator,ASTBitOperator,ASTArithmeticOperator
        :param _rhs: the right-hand side expression
        :type _rhs: ASTExpression
        :param _condition: the condition of a ternary operator
        :type _condition: ASTExpression
        :param _ifTrue: if condition holds, this expression is executed.
        :type _ifTrue: ASTExpression
        :param _ifNot: if condition does not hold, this expression is executed.
        :type _ifNot: ASTExpression
        """
        self.__hasLeftParentheses = _hasLeftParentheses
        self.__hasRightParentheses = _hasRightParentheses
        self.__isLogicalNot = _isLogicalNot
        self.__unaryOperator = _unaryOperator
        self.__expression = _expression
        # lhs and rhs combined by an operator
        self.__lhs = _lhs
        self.__binaryOperator = _binaryOperator
        self.__rhs = _rhs
        # ternary operator
        self.__condition = _condition
        self.__ifTrue = _ifTrue
        self.__ifNot = _ifNot

    @classmethod
    def makeExpression(cls, _hasLeftParentheses: bool = False, _hasRightParentheses: bool = False,
                       _unaryOperator: ASTUnaryOperator = None, _isLogicalNot: bool = False, _expression=None):
        """
        The factory method used to create expression which are either encapsulated in parentheses (e.g., (10mV)) 
        OR have a unary (e.g., ~bitVar), OR are negated (e.g., not logVar), or are simple expression (e.g., 10mV).
        :param _hasLeftParentheses: is encapsulated in brackets (left). 
        :type _hasLeftParentheses: bool
        :param _hasRightParentheses: is encapsulated in brackets (right).
        :type _hasRightParentheses: bool
        :param _unaryOperator: combined by unary operator, e.g., ~.
        :type _unaryOperator: ASTUnaryOperator
        :param _isLogicalNot: is a negated expression.
        :type _isLogicalNot: bool
        :param _expression: the expression either encapsulated in brackets or negated or with a with a unary op, or a simple expression.
        :type _expression: ASTExpression
        :return: a new ASTExpression object.
        :rtype: ASTExpression
        """
        assert ((_hasLeftParentheses ^ _hasRightParentheses) == False), \
            '(NESTML) Parenthesis on both sides of expression expected.'
        assert ((_hasRightParentheses and _hasLeftParentheses) or (_unaryOperator is not None) or _isLogicalNot), \
            '(NESTML) Expression build not correctly.'
        return cls(_hasLeftParentheses=_hasLeftParentheses, _hasRightParentheses=_hasRightParentheses,
                   _unaryOperator=_unaryOperator,
                   _isLogicalNot=_isLogicalNot, _expression=_expression)

    @classmethod
    def makeCompoundExpression(cls, _lhs=None, _binaryOperator=None, _rhs=None):
        """
        The factory method used to create compound expressions, e.g. 10mV + V_m.
        :param _lhs: the left-hand side expression.
        :type _lhs: ASTExpression
        :param _binaryOperator: a binary operator, e.g., a comparison operator or a logical operator.
        :type _binaryOperator: one of ASTLogicalOperator,ASTComparisonOperator,ASTBitOperator,ASTArithmeticOperator
        :param _rhs: the right-hand side expression
        :type _rhs: ASTExpression
        :return: a new ASTExpression object.
        :rtype: ASTExpression
        """
        assert (_lhs is not None), '(NESTML) The left-hand side expression must not be empty.'
        assert (_rhs is not None), '(NESTML) The right-hand side expression must not be empty.'
        assert (_binaryOperator is not None), '(NESTML) The binary operator mus not be empty.'
        return cls(_lhs=_lhs, _binaryOperator=_binaryOperator, _rhs=_rhs)

    @classmethod
    def makeTernaryExpression(cls, _condition=None, _ifTrue=None, _ifNot=None):
        """
        The factory method used to create a ternary operator expression, e.g., 10mV<V_m?10mV:V_m
        :param _condition: the condition of a ternary operator
        :type _condition: ASTExpression
        :param _ifTrue: if condition holds, this expression is executed.
        :type _ifTrue: ASTExpression
        :param _ifNot: if condition does not hold, this expression is executed.
        :type _ifNot: ASTExpression
        :return: a new ASTExpression object.
        :rtype: ASTExpression
        """
        assert (_condition is not None), '(NESTML) Condition of ternary operator must not be empty.'
        assert (_ifTrue is not None), '(NESTML) The if-true case of ternary operator must not be empty.'
        assert (_ifNot is not None), '(NESTML) The if-not case of ternary operator must not be empty.'
        return cls(_condition=_condition, _ifTrue=_ifTrue, _ifNot=_ifNot)

    def isSimpleExpression(self) -> bool:
        """
        Returns whether it is a simple expression, e.g. 10mV.
        :return: True if simple expression, otherwise false.
        :rtype: bool
        """
        return (self.__expression is not None) and isinstance(self.__expression,
                                                              ASTSimpleExpression.ASTSimpleExpression)

    def isExpression(self) -> bool:
        """
        Returns whether it is a expression, e.g. ~10mV.
        :return: True if expression, otherwise false.
        :rtype: bool 
        """
        return self.__expression is not None

    def getExpression(self):
        """
        Returns the expression.
        :return: the expression.
        :rtype: ASTExpression
        """
        return self.__expression

    def hasLeftParentheses(self) -> bool:
        """
        Returns whether the expression has a left parenthesis on the left side.
        :return: True if parenthesis on the left side, otherwise False.
        :rtype: bool
        """
        return self.__hasLeftParentheses

    def hasRightParentheses(self) -> bool:
        """
        Returns whether the expression has a left parenthesis on the right side.
        :return: True if parenthesis on the right side, otherwise False.
        :rtype: bool
        """
        return self.__hasRightParentheses

    def isLogicalNot(self) -> bool:
        """
        Returns whether the expression is negated by a logical not.
        :return: True if negated, otherwise False.  
        :rtype: bool
        """
        return self.__isLogicalNot

    def isUnaryOperator(self) -> bool:
        """
        Returns whether the expression uses an unary operator.
        :return: True if unary operator, otherwise False.  
        :rtype: bool
        """
        return self.__unaryOperator is not None

    def getUnaryOperator(self) -> ASTUnaryOperator:
        """
        Returns the unary operator.
        :return: the unary operator.
        :rtype: ASTUnaryOperator.
        """
        return self.__unaryOperator

    def isCompoundExpression(self) -> bool:
        """
        Returns whether it is a compound expression, e.g., 10+10
        :return: True if compound expression, otherwise False.
        :rtype: bool
        """
        return (self.__lhs is not None) and (self.__rhs is not None) and (self.__binaryOperator is not None)

    def getLhs(self):
        """
        Returns the left-hand side expression.
        :return: the left-hand side expression.
        :rtype: ASTExpression
        """
        return self.__lhs

    def getRhs(self):
        """
        Returns the right-hand side expression.
        :return: the right-hand side expression.
        :rtype: ASTExpression
        """
        return self.__rhs

    def getBinaryOperator(self):
        """
        Returns the binary operator.
        :return: the binary operator.
        :rtype: one of ASTLogicalOperator,ASTComparisonOperator,ASTBitOperator,ASTArithmeticOperator
        """
        return self.__binaryOperator

    def isTernaryOperator(self) -> bool:
        """
        Returns whether it is a ternary operator.
        :return: True if ternary operator, otherwise False.
        :rtype: bool
        """
        return (self.__condition is not None) and (self.__ifTrue is not None) and (self.__ifNot is not None)

    def getCondition(self):
        """
        Returns the condition expression.
        :return: the condition expression.
        :rtype: ASTExpression
        """
        return self.__condition

    def getIfTrue(self):
        """
        Returns the expression used in the case that the condition holds.
        :return: the if-true condition.
        :rtype: ASTExpression
        """
        return self.__ifTrue

    def getIfNot(self):
        """
        Returns the expression used in the case that the condition does not hold.
        :return: the if-not condition.
        :rtype: ASTExpression
        """
        return self.__ifNot

    def print(self) -> str:
        """
        Returns the string representation of the expression.
        :return: the expression as a string.
        :rtype: str
        """
        ret = ''
        if self.isExpression():
            if self.hasLeftParentheses():
                ret += '('
            if self.isLogicalNot():
                ret += 'not '
            else:
                ret += self.getUnaryOperator().print()
            ret += self.getExpression().print()
            if self.hasRightParentheses():
                ret += ')'
        elif self.isCompoundExpression():
            ret += self.getBinaryOperator().print()
        elif self.isTernaryOperator():
            ret += self.getCondition().print() + '?' + self.getIfTrue().print() + ':' + self.getIfNot().print()