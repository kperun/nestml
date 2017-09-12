"""
/*
 *  SymbolTableASTVisitor.py
 *
 *  This file is part of NEST.
 *
 *  Copyright (C) 2004 The NEST Initiative
 *
 *  NEST is free software: you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation, either version 2 of the License, or
 *  (at your option) any later version.
 *
 *  NEST is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with NEST.  If not, see <http://www.gnu.org/licenses/>.
 *
 */
@author kperun
"""
from pynestml.src.main.python.org.nestml.symbol_table.Scope import Scope
from pynestml.src.main.python.org.nestml.symbol_table.Scope import ScopeType
from pynestml.src.main.python.org.nestml.symbol_table.Symbol import Symbol
from pynestml.src.main.python.org.nestml.symbol_table.Symbol import SymbolType
from pynestml.src.main.python.org.nestml.ast import *


class SymbolTableASTVisitor:
    """
    This class is used to create a symbol table from a handed over AST.
    """

    @classmethod
    def updateSymbolTable(cls, _astNeuron=None):
        """
        Creates for the handed over ast the corresponding symbol table.
        :param _astNeuron: a AST neuron object as used to create the symbol table
        :type _astNeuron: ASTNeuron
        :return: a new symbol table
        :rtype: SymbolTable
        """
        return SymbolTableASTVisitor.__visitNeuron(_astNeuron)

    @classmethod
    def __visitNeuron(cls, _neuron=None):
        """
        Private method: Used to visit a single neuron and create the corresponding global as well as local scopes.
        :return: a single neuron.
        :rtype: ASTNeuron
        """
        assert (_neuron is not None and isinstance(_neuron, ASTNeuron.ASTNeuron)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of neuron provided!'
        scope = Scope(_scopeType=ScopeType.GLOBAL, _enclosingScope=None, _sourcePosition=_neuron.getSourcePosition())
        _neuron.updateScope(scope)
        _neuron.getBody().updateScope(scope)
        cls.__visitBody(_neuron.getBody())
        return

    @classmethod
    def __visitBody(cls, _body=None):
        """
        Private method: Used to visit a single neuron body and create the corresponding scope.
        :param _body: a single body element.
        :type _body: ASTBody
        """
        for bodyElement in _body.getBodyElements():
            bodyElement.updateScope(_body.getScope())
            if isinstance(bodyElement, ASTBlockWithVariables.ASTBlockWithVariables):
                cls.__visitBlockWithVariable(bodyElement)
            elif isinstance(bodyElement, ASTUpdateBlock.ASTUpdateBlock):
                cls.__visitUpdateBlock(bodyElement)
            elif isinstance(bodyElement, ASTEquationsBlock.ASTEquationsBlock):
                cls.__visitEquationsBlock(bodyElement)
            elif isinstance(bodyElement, ASTInputBlock.ASTInputBlock):
                cls.__visitInputBlock(bodyElement)
            elif isinstance(bodyElement, ASTOutputBlock.ASTOutputBlock):
                cls.__visitOutputBlock(bodyElement)
            elif isinstance(bodyElement, ASTFunction.ASTFunction):
                cls.__visitFunctionBlock(bodyElement)
        return

    @classmethod
    def __visitFunctionBlock(cls, _block=None):
        """
        Private method: Used to visit a single function block and create the corresponding scope.
        :param _block: a function block object.
        :type _block: ASTFunction
        """
        assert (_block is not None and isinstance(_block, ASTFunction.ASTFunction)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of function block provided!'
        symbol = Symbol(_scope=_block.getScope(), _elementReference=_block,
                        _name=_block.getName(), _type=SymbolType.FUNCTION)
        _block.getScope().addSymbol(symbol)
        scope = Scope(_scopeType=ScopeType.FUNCTION, _enclosingScope=_block.getScope(),
                      _sourcePosition=_block.getSourcePosition())
        for arg in _block.getParameters().getParametersList():
            arg.updateScope(scope)
            scope.addSymbol(Symbol(_elementReference=arg, _scope=scope, _type=SymbolType.VARIABLE, _name=arg.getName()))
            arg.getDataType().updateScope(scope)
            cls.__visitDataType(arg.getDataType())
        _block.getBlock().updateScope(scope)
        cls.__visitBlock(_block.getBlock())
        return

    @classmethod
    def __visitUpdateBlock(cls, _block=None):
        """
        Private method: Used to visit a single update block and create the corresponding scope.
        :param _block: an update block object. 
        :type _block: ASTDynamics
        """
        assert (_block is not None and isinstance(_block, ASTUpdateBlock.ASTUpdateBlock)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of update-block provided!'
        scope = Scope(_scopeType=ScopeType.UPDATE, _enclosingScope=_block.getScope(),
                      _sourcePosition=_block.getSourcePosition())
        _block.getScope().addScope(scope)
        _block.getBlock().updateScope(scope)
        cls.__visitBlock(_block.getBlock())
        return

    @classmethod
    def __visitBlock(cls, _block=None):
        """
        Private method: Used to visit a single block of statements, create and update the corresponding scope.
        :param _block: a block object.
        :type _block: ASTBlock
        """
        assert (_block is not None and isinstance(_block, ASTBlock.ASTBlock)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of block provided!'
        for stmt in _block.getStmts():
            if stmt.isSmallStmt():
                stmt.updateScope(_block.getScope())
                stmt.getSmallStmt().updateScope(_block.getScope())
                cls.__visitSmallStmt(stmt.getSmallStmt())
            else:
                innerScope = Scope(_scopeType=ScopeType.LOCAL, _enclosingScope=_block.getScope(),
                                   _sourcePosition=stmt.getSourcePosition())
                _block.getScope().addScope(innerScope)
                stmt.updateScope(innerScope)
                stmt.getCompoundStmt().updateScope(innerScope)
                cls.__visitCompoundStmt(stmt.getCompoundStmt())
        return

    @classmethod
    def __visitSmallStmt(cls, _stmt=None):
        """
        Private method: Used to visit a single small statement and create the corresponding sub-scope.
        :param _stmt: a single small statement.
        :type _stmt: ASTSmallStatement
        """
        assert (_stmt is not None and isinstance(_stmt, ASTSmallStmt.ASTSmallStmt)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of small statement provided!'
        if _stmt.isDeclaration():
            _stmt.getDeclaration().updateScope(_stmt.getScope())
            cls.__visitDeclaration(_stmt.getDeclaration())
        elif _stmt.isAssignment():
            _stmt.getAssignment().updateScope(_stmt.getScope())
            cls.__visitAssignment(_stmt.getAssignment())
        elif _stmt.isFunctionCall():
            _stmt.getFunctionCall().updateScope(_stmt.getScope())
            cls.__visitFunctionCall(_stmt.getFunctionCall())
        elif _stmt.isReturnStmt():
            _stmt.getReturnStmt().updateScope(_stmt.getScope())
            cls.__visitReturnStmt(_stmt.getReturnStmt())
        return

    @classmethod
    def __visitCompoundStmt(cls, _stmt=None):
        """
        Private method: Used to visit a single compound statement and create the corresponding sub-scope. 
        :param _stmt: a single compound statement.
        :type _stmt: ASTCompoundStatement
        """
        assert (_stmt is not None and isinstance(_stmt, ASTCompoundStmt.ASTCompoundStmt)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of compound statement provided!'
        if _stmt.isIfStmt():
            _stmt.getIfStmt().updateScope(_stmt.getScope())
            cls.__visitIfStmt(_stmt.getIfStmt())
        elif _stmt.isWhileStmt():
            _stmt.getWhileStmt().updateScope(_stmt.getScope())
            cls.__visitWhileStmt(_stmt.getWhileStmt())
        else:
            _stmt.getForStmt().updateScope(_stmt.getScope())
            cls.__visitForStmt(_stmt.getForStmt())
        return

    @classmethod
    def __visitAssignment(cls, _assignment=None):
        """
        Private method: Used to visit a single assignment and update the its corresponding scope.
        :param _assignment: an assignment object.
        :type _assignment: ASTAssignment
        :return: no return value, since neither scope nor symbol is created
        :rtype: void
        """
        assert (_assignment is not None and isinstance(_assignment, ASTAssignment.ASTAssignment)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of assignment provided!'
        _assignment.getVariable().updateScope(_assignment.getScope())
        cls.__visitVariable(_assignment.getVariable())
        _assignment.getExpression().updateScope(_assignment.getScope())
        cls.__visitExpression(_assignment.getExpression())
        return

    @classmethod
    def __visitFunctionCall(cls, _functionCall=None):
        """
        Private method: Used to visit a single function call and update its corresponding scope.
        :param _functionCall: a function call object.
        :type _functionCall: ASTFunctionCall
        :return: no return value, since neither scope nor symbol is created
        :rtype: void
        """
        assert (_functionCall is not None and isinstance(_functionCall, ASTFunctionCall.ASTFunctionCall)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of function call provided!'
        for arg in _functionCall.getArgs():
            arg.updateScope(_functionCall.getScope())
            cls.__visitExpression(arg)
        return

    @classmethod
    def __visitDeclaration(cls, _declaration=None):
        """
        Private method: Used to visit a single declaration, update its scope and return the corresponding set of
        symbols
        :param _declaration: a declaration object.
        :type _declaration: ASTDeclaration
        :return: the scope is update without a return value.
        :rtype: void
        """
        assert (_declaration is not None and isinstance(_declaration, ASTDeclaration.ASTDeclaration)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong typ of declaration provided!'
        for var in _declaration.getVariables():  # for all variables declared create a new symbol
            var.updateScope(_declaration.getScope())
            _declaration.getScope().addSymbol(Symbol(_scope=_declaration.getScope(), _elementReference=_declaration,
                                                     _name=var.getName(), _type=SymbolType.VARIABLE))
            cls.__visitVariable(var)
        _declaration.getDataType().updateScope(_declaration.getScope())
        cls.__visitDataType(_declaration.getDataType())
        if _declaration.hasExpression():
            _declaration.getExpr().updateScope(_declaration.getScope())
            cls.__visitExpression(_declaration.getExpr())
        if _declaration.hasInvariant():
            _declaration.getInvariant().updateScope(_declaration.getScope())
            cls.__visitExpression(_declaration.getInvariant())
        return

    @classmethod
    def __visitReturnStmt(cls, _returnStmt=None):
        """
        Private method: Used to visit a single return statement and update its scope.
        :param _returnStmt: a return statement object.
        :type _returnStmt: ASTReturnStmt
        """
        assert (_returnStmt is not None and isinstance(_returnStmt, ASTReturnStmt.ASTReturnStmt)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of return statement provided!'
        if _returnStmt.hasExpr():
            _returnStmt.getExpr().updateScope(_returnStmt.getScope())
            cls.__visitExpression(_returnStmt.getExpr())
        return

    @classmethod
    def __visitIfStmt(cls, _ifStmt=None):
        """
        Private method: Used to visit a single if-statement, update its scope and create the corresponding sub-scope.
        :param _ifStmt: an if-statement object.
        :type _ifStmt: ASTIfStmt
        """
        assert (_ifStmt is not None and isinstance(_ifStmt, ASTIfStmt.ASTIfStmt)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of if-statement provided!'
        _ifStmt.getIfClause().updateScope(_ifStmt.getScope())
        cls.__visitIfClause(_ifStmt.getIfClause())
        for elIf in _ifStmt.getElifClauses():
            elIf.updateScope(_ifStmt.getScope())
            cls.__visitElifClause(elIf)
        if _ifStmt.hasElseClause():
            _ifStmt.getElseClause().updateScope(_ifStmt.getScope())
            cls.__visitElseClause(_ifStmt.getElseClause())
        return

    @classmethod
    def __visitIfClause(cls, _ifClause=None):
        """
        Private method: Used to visit a single if-clause, update its scope and create the corresponding sub-scope.
        :param _ifClause: an if clause.
        :type _ifClause: ASTIfClause
        """
        assert (_ifClause is not None and isinstance(_ifClause, ASTIfClause.ASTIfClause)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of if-clause handed over!'
        _ifClause.getCondition().updateScope(_ifClause.getScope())
        cls.__visitExpression(_ifClause.getCondition())
        _ifClause.getBlock().updateScope(_ifClause.getScope())
        cls.__visitBlock(_ifClause.getBlock())
        return

    @classmethod
    def __visitElifClause(cls, _elifClause=None):
        """
        Private method: Used to visit a single elif-clause, update its scope and create the corresponding sub-scope.
        :param _elifClause: an elif clause.
        :type _elifClause: ASTElifClause
        """
        assert (_elifClause is not None and isinstance(_elifClause, ASTElifClause.ASTElifClause)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of elif-clause handed over!'
        _elifClause.getCondition().updateScope(_elifClause.getScope())
        cls.__visitExpression(_elifClause.getCondition())
        _elifClause.getBlock().updateScope(_elifClause.getScope())
        cls.__visitBlock(_elifClause.getBlock())
        return

    @classmethod
    def __visitElseClause(cls, _elseClause=None):
        """
        Private method: Used to visit a single else-clause, update its scope and create the corresponding sub-scope.
        :param _elseClause: an else clause.
        :type _elseClause: ASTElseClause
        """
        assert (_elseClause is not None and isinstance(_elseClause, ASTElseClause.ASTElseClause)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of else-clause handed over!'
        _elseClause.getBlock().updateScope(_elseClause.getScope())
        cls.__visitBlock(_elseClause.getBlock())
        return

    @classmethod
    def __visitForStmt(cls, _forStmt=None):
        """
        Private method: Used to visit a single for-stmt, update its scope and create the corresponding sub-scope.
        :param _forStmt: a for-statement. 
        :type _forStmt: ASTForStmt
        """
        assert (_forStmt is not None and isinstance(_forStmt, ASTForStmt.ASTForStmt)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of for-statement provided!'
        _forStmt.getFrom().updateScope(_forStmt.getScope())
        cls.__visitExpression(_forStmt.getFrom())
        _forStmt.getTo().updateScope(_forStmt.getScope())
        cls.__visitExpression(_forStmt.getTo())
        _forStmt.getBlock().updateScope(_forStmt.getScope())
        cls.__visitBlock(_forStmt.getBlock())
        return

    @classmethod
    def __visitWhileStmt(cls, _whileStmt=None):
        """
        Private method: Used to visit a single while-stmt, update its scope and create the corresponding sub-scope.
        :param _whileStmt: a while-statement.
        :type _whileStmt: ASTWhileStmt
        """
        assert (_whileStmt is not None and isinstance(_whileStmt, ASTWhileStmt.ASTWhileStmt)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of while-statement provided!'
        _whileStmt.getCondition().updateScope(_whileStmt.getScope())
        cls.__visitExpression(_whileStmt.getCondition())
        _whileStmt.getBlock().updateScope(_whileStmt.getScope())
        cls.__visitBlock(_whileStmt.getBlock())
        return

    @classmethod
    def __visitDataType(cls, _dataType=None):
        """
        Private method: Used to visit a single data-type and update its scope. 
        :param _dataType: a data-type.
        :type _dataType: ASTDataType
        """
        assert (_dataType is not None and isinstance(_dataType, ASTDatatype.ASTDatatype)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of data-type provided!'
        if _dataType.isUnitType():
            _dataType.getUnitType().updateScope(_dataType.getScope())
            cls.__visitUnitType(_dataType.getUnitType())
        return

    @classmethod
    def __visitUnitType(cls, _unitType=None):
        """
        Private method: Used to visit a single unit-type and update its scope.
        :param _unitType: a unit type.
        :type _unitType: ASTUnitType
        """
        assert (_unitType is not None and isinstance(_unitType, ASTUnitType.ASTUnitType)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of unit-typ provided!'
        if _unitType.isPowerExpression():
            _unitType.getBase().updateScope(_unitType.getScope())
            cls.__visitUnitType(_unitType.getBase())
        elif _unitType.isEncapsulated():
            _unitType.getCompoundUnit().updateScope(_unitType.getScope())
            cls.__visitUnitType(_unitType.getCompoundUnit())
        elif _unitType.isDiv() or _unitType.isTimes():
            if isinstance(_unitType.getLhs(),
                          ASTUnitType.ASTUnitType):  # regard that lhs can be a numeric Or a unit-type
                _unitType.getLhs().updateScope(_unitType.getScope())
                cls.__visitUnitType(_unitType.getLhs())
            _unitType.getRhs().updateScope(_unitType.getScope())
            cls.__visitUnitType(_unitType.getRhs())
        return

    @classmethod
    def __visitExpression(cls, _expr=None):
        """
        Private method: Used to visit a single expression and update its scope.
        :param _expr: an expression.
        :type _expr: ASTExpression
        """
        assert (_expr is not None and (isinstance(_expr, ASTExpression.ASTExpression)
                                       or isinstance(_expr, ASTSimpleExpression.ASTSimpleExpression))), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of expression handed over!'
        if _expr.isSimpleExpression():
            _expr.getExpression().updateScope(_expr.getScope())
            cls.__visitSimpleExpression(_expr.getExpression())
        if _expr.isUnaryOperator():
            _expr.getUnaryOperator().updateScope(_expr.getScope())
            cls.__visitUnaryOperator(_expr.getUnaryOperator())
        if _expr.isCompoundExpression():
            _expr.getLhs().updateScope(_expr.getScope())
            cls.__visitExpression(_expr.getLhs())
            _expr.getBinaryOperator().updateScope(_expr.getScope())
            if isinstance(_expr.getBinaryOperator(), ASTBitOperator.ASTBitOperator):
                cls.__visitBitOperator(_expr.getBinaryOperator())
            elif isinstance(_expr.getBinaryOperator(), ASTComparisonOperator.ASTComparisonOperator):
                cls.__visitComparisonOperator(_expr.getBinaryOperator())
            elif isinstance(_expr.getBinaryOperator(), ASTLogicalOperator.ASTLogicalOperator):
                cls.__visitLogicalOperator(_expr.getBinaryOperator())
            else:
                cls.__visitArithmeticOperator(_expr.getBinaryOperator())
            _expr.getRhs().updateScope(_expr.getScope())
            cls.__visitExpression(_expr.getRhs())
        if _expr.isTernaryOperator():
            _expr.getCondition().updateScope(_expr.getScope())
            cls.__visitExpression(_expr.getCondition())
            _expr.getIfTrue().updateScope(_expr.getScope())
            cls.__visitExpression(_expr.getIfTrue())
            _expr.getIfNot().updateScope(_expr.getScope())
            cls.__visitExpression(_expr.getIfNot())
        return

    @classmethod
    def __visitSimpleExpression(cls, _expr=None):
        """
        Private method: Used to visit a single simple expression and update its scope.
        :param _expr: a simple expression. 
        :type _expr: ASTSimpleExpression
        """
        assert (_expr is not None and isinstance(_expr, ASTSimpleExpression.ASTSimpleExpression)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of simple expression provided!'
        if _expr.isFunctionCall():
            _expr.getFunctionCall().updateScope(_expr.getScope())
            cls.__visitFunctionCall(_expr.getFunctionCall())
        elif _expr.isVariable():
            _expr.getVariable().updateScope(_expr.getScope())
            cls.__visitVariable(_expr.getVariable())
        return

    @classmethod
    def __visitUnaryOperator(cls, _unaryOp=None):
        """
        Private method: Used to visit a single unary operator and update its scope.
        :param _unaryOp: a single unary operator. 
        :type _unaryOp: ASTUnaryOperator
        """
        assert (_unaryOp is not None and isinstance(_unaryOp, ASTUnaryOperator.ASTUnaryOperator)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of unary operator provided!'
        return

    @classmethod
    def __visitBitOperator(cls, _bitOp=None):
        """
        Private method: Used to visit a single unary operator and update its scope.
        :param _bitOp: a single bit operator. 
        :type _bitOp: ASTBitOperator
        """
        assert (_bitOp is not None and isinstance(_bitOp, ASTBitOperator.ASTBitOperator)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of bit operator provided!'
        return

    @classmethod
    def __visitComparisonOperator(cls, _comparisonOp=None):
        """
        Private method: Used to visit a single comparison operator and update its scope.
        :param _comparisonOp: a single comparison operator.
        :type _comparisonOp: ASTComparisonOperator
        """
        assert (_comparisonOp is not None and isinstance(_comparisonOp, ASTComparisonOperator.ASTComparisonOperator)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of comparison operator provided!'
        return

    @classmethod
    def __visitLogicalOperator(cls, _logicalOp=None):
        """
        Private method: Used to visit a single logical operator and update its scope.
        :param _logicalOp: a single logical operator.
        :type _logicalOp: ASTLogicalOperator
        """
        assert (_logicalOp is not None and isinstance(_logicalOp, ASTLogicalOperator.ASTLogicalOperator)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of logical operator provided!'
        return

    @classmethod
    def __visitVariable(cls, _variable=None):
        """
        Private method: Used to visit a single variable and update its scope.
        :param _variable: a single variable.
        :type _variable: ASTVariable
        """
        assert (_variable is not None and isinstance(_variable, ASTVariable.ASTVariable)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of variable provided!'
        return

    @classmethod
    def __visitOdeFunction(cls, _odeFunction=None):
        """
        Private method: Used to visit a single ode-function, create the corresponding symbol and update the scope.
        :param _odeFunction: a single ode-function.
        :type _odeFunction: ASTOdeFunction
        """
        assert (_odeFunction is not None and isinstance(_odeFunction, ASTOdeFunction.ASTOdeFunction)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of ode-function provided!'
        symbol = Symbol(_elementReference=_odeFunction, _scope=_odeFunction.getScope(),
                        _type=SymbolType.VARIABLE, _name=_odeFunction.getVariableName())
        _odeFunction.getScope().addSymbol(symbol)
        _odeFunction.getDataType().updateScope(_odeFunction.getScope())
        cls.__visitDataType(_odeFunction.getDataType())
        _odeFunction.getExpression().updateScope(_odeFunction.getScope())
        cls.__visitExpression(_odeFunction.getExpression())
        return

    @classmethod
    def __visitOdeShape(cls, _odeShape=None):
        """
        Private method: Used to visit a single ode-shape, create the corresponding symbol and update the scope.
        :param _odeShape: a single ode-shape.
        :type _odeShape: ASTOdeShape
        """
        assert (_odeShape is not None and isinstance(_odeShape, ASTOdeShape.ASTOdeShape)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of ode-shape provided!'
        symbol = Symbol(_elementReference=_odeShape, _scope=_odeShape.getScope(),
                        _type=SymbolType.VARIABLE, _name=_odeShape.getVariable().getName())
        _odeShape.getScope().addSymbol(symbol)
        _odeShape.getVariable().updateScope(_odeShape.getScope())
        cls.__visitVariable(_odeShape.getVariable())
        _odeShape.getExpression().updateScope(_odeShape.getScope())
        cls.__visitExpression(_odeShape.getExpression())
        return

    @classmethod
    def __visitOdeEquation(cls, _equation=None):
        """
        Private method: Used to visit a single ode-equation and update the corresponding scope.
        :param _equation: a single ode-equation.
        :type _equation: ASTOdeEquation
        """
        assert (_equation is not None and isinstance(_equation, ASTOdeEquation.ASTOdeEquation)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of ode-equation handed over!'
        _equation.getLhs().updateScope(_equation.getScope())
        cls.__visitDerivative(_equation.getLhs())
        _equation.getRhs().updateScope(_equation.getScope())
        cls.__visitExpression(_equation.getRhs())
        return

    @classmethod
    def __visitBlockWithVariable(cls, _block=None):
        """
        Private method: Used to visit a single block of variables and update its scope.
        :param _block: a block with declared variables.
        :type _block: ASTBlockWithVariables
        """
        assert (_block is not None and isinstance(_block, ASTBlockWithVariables.ASTBlockWithVariables)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of block with variables provided!'
        for decl in _block.getDeclarations():
            decl.updateScope(_block.getScope())
            cls.__visitDeclaration(decl)
        return

    @classmethod
    def __visitEquationsBlock(cls, _block=None):
        """
        Private method: Used to visit a single equations block and update its scope.
        :param _block: a single equations block.
        :type _block: ASTEquationsBlock
        """
        assert (_block is not None and isinstance(_block, ASTEquationsBlock.ASTEquationsBlock)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of equations block provided!'
        for decl in _block.getDeclarations():
            decl.updateScope(_block.getScope())
            if isinstance(decl, ASTOdeFunction.ASTOdeFunction):
                cls.__visitOdeFunction(decl)
            elif isinstance(decl, ASTOdeShape.ASTOdeShape):
                cls.__visitOdeShape(decl)
            else:
                cls.__visitOdeEquation(decl)
        return

    @classmethod
    def __visitInputBlock(cls, _block=None):
        """
        Private method: Used to visit a single input block and update its scope.
        :param _block: a single input block.
        :type _block: ASTInputBlock
        """
        assert (_block is not None and isinstance(_block, ASTInputBlock.ASTInputBlock)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of input-block provided!'
        for line in _block.getInputLines():
            line.updateScope(_block.getScope())
            cls.__visitInputLine(line)
        return

    @classmethod
    def __visitOutputBlock(cls, _block=None):
        """
        Private method: Used to visit a single output block and visit its scope.
        :param _block: a single output block. 
        :type _block: ASTOutputBlock
        """
        assert (_block is not None and isinstance(_block, ASTOutputBlock.ASTOutputBlock)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of output-block provided!'
        return

    @classmethod
    def __visitInputLine(cls, _line=None):
        """
        Private method: Used to visit a single input line, create the corresponding symbol and update the scope.
        :param _line: a single input line.
        :type _line: ASTInputLine
        """
        assert (_line is not None and isinstance(_line, ASTInputLine.ASTInputLine)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of input-line provided!'
        symbol = Symbol(_elementReference=_line, _scope=_line.getScope(),
                        _type=SymbolType.VARIABLE, _name=_line.getName())
        _line.getScope().addSymbol(symbol)
        for inputType in _line.getInputTypes():
            cls.__visitInputType(inputType)
            inputType.updateScope(_line.getScope())
        return

    @classmethod
    def __visitInputType(cls, _type=None):
        """
        Private method: Used to visit a single input type and update its scope.
        :param _type: a single input-type.
        :type _type: ASTInputType
        """
        assert (_type is not None and isinstance(_type, ASTInputType.ASTInputType)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of input-type provided!'
        return

    @classmethod
    def __visitDerivative(cls, _derivative=None):
        """
        Private method: Used to visit a single derivative and update its scope.
        :param _derivative: a single derivative.
        :type _derivative: ASTDerivative
        """
        assert (_derivative is not None and isinstance(_derivative, ASTDerivative.ASTDerivative)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of derivative provided!'
        return

    @classmethod
    def __visitArithmeticOperator(cls, _arithmeticOp=None):
        """
        Private method: Used to visit a single arithmetic operator and update its scope.
        :param _arithmeticOp: a single arithmetic operator.
        :type _arithmeticOp: ASTArithmeticOperator
        """
        assert (_arithmeticOp is not None and isinstance(_arithmeticOp, ASTArithmeticOperator.ASTArithmeticOperator)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of arithmetic operator provided!'
        return