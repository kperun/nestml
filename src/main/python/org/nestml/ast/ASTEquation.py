"""
TODO header
@author kperun
"""
from src.main.python.org.nestml.ast.ASTDerivative import ASTDerivative
from src.main.python.org.nestml.ast.ASTExpression import ASTExpression

class ASTEquation:
    """
    This class is used to store ast equations, e.g., V_m' = 10mV + V_m.
    ASTEquation Represents an equation, e.g. "I = exp(t)" or represents an differential equations, e.g. "V_m' = V_m+1".
    @attribute lhs      Left hand side, e.g. a Variable.
    @attribute rhs      Expression defining the right hand side.
    Grammar:
        equation : lhs=derivative '=' rhs=expression;
    """
    __lhs = None
    __rhs = None

    def __init__(self, _lhs: ASTDerivative = None, _rhs: ASTExpression = None):
        """
        Standard constructor.
        :param _lhs: an object of type ASTDerivative
        :type _lhs: ASTDerivative
        :param _rhs: an object of type ASTExpression.
        :type _rhs: ASTExpression
        """
        self.__lhs = _lhs
        self.__rhs = _rhs

    @classmethod
    def makeASTEquation(cls, _lhs: ASTDerivative = None, _rhs: ASTExpression = None):
        """
        A factory method used to generate new ASTEquation.
        :param _lhs: an object of type ASTDerivative
        :type _lhs: ASTDerivative
        :param _rhs: an object of type ASTExpression
        :type _rhs: ASTExpression
        """
        return cls(_lhs, _rhs)

    def getLhs(self) -> ASTDerivative:
        """
        Returns the left-hand side of the equation.
        :return: an object of the ast-derivative class.
        :rtype: ASTDerivative
        """
        return self.__lhs

    def getRhs(self) -> ASTExpression:
        """
        Returns the left-hand side of the equation.
        :return: an object of the ast-expr class.
        :rtype: ASTExpression
        """
        return self.__rhs