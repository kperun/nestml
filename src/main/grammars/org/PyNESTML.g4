
/**
  Grammar representing the Simple Programming Language (SPL). It is easy to learn imperative
  language which leans on the Python syntax.
*/
grammar PyNESTML;

  import Tokens;

  nestmlCompilationUnit : (neuron | NEWLINE )* EOF;
  /*********************************************************************************************************************
  * Units-Language
  *********************************************************************************************************************/

  /**
    ASTDatatype. Represents predefined datatypes and gives a possibility to use an unit
    datatype.
    @attribute boolean getters for integer, real, ...
    @attribute unitType a SI datatype
  */
  datatype : 'integer'
           | 'real'
           | 'string'
           | 'boolean'
           | 'void'
           | unitType;
  /**
    ASTUnitType. Represents an unit datatype. It can be a plain datatype as 'mV' or a
    complex data type as 'mV/s'
  */
  unitType : leftParentheses='(' unitType rightParentheses=')'
           | base=unitType powOp='**' exponent=NUMERIC_LITERAL
           | left=unitType (timesOp='*' | divOp='/') right=unitType
           | unitlessLiteral=NUMERIC_LITERAL divOp='/' right=unitType
           | unit=NAME;

  /*********************************************************************************************************************
  * Expressions-Language
  *********************************************************************************************************************/
  expr : leftParentheses='(' expr rightParentheses=')'
         | <assoc=right> base=expr powOp='**' exponent=expr
         | unaryOperator term=expr
         | left=expr (timesOp='*' | divOp='/' | moduloOp='%') right=expr
         | left=expr (plusOp='+'  | minusOp='-') right=expr
         | left=expr bitOperator right=expr
         | left=expr comparisonOperator right=expr
         | logicalNot='not' expr
         | left=expr logicalOperator right=expr
         | condition=expr '?' ifTrue=expr ':' ifNot=expr
         | functionCall
         | BOOLEAN_LITERAL // true & false;
         | NUMERIC_LITERAL (variable)?
         | NAME
         | 'inf'
         | variable;

  unaryOperator : (unaryPlus='+' | unaryMinus='-' | unaryTilde='~');

  bitOperator : (bitAnd='&'| bitXor='^' | bitOr='|' | bitShiftLeft='<<' | bitShiftRight='>>');

  comparisonOperator : (lt='<' | le='<=' | eq='==' | ne='!=' | ne2='<>' | ge='>=' | gt='>');

  logicalOperator : (logicalAnd='and' | logicalOr='or');

  /**
    ASTVariable Provides a 'marker' AST node to identify variables used in expressions.
    @attribute name
  */
  variable : NAME (differentialOrder='\'')*;

  /**
    ASTFunctionCall Represents a function call, e.g. myFun("a", "b").
    @attribute name The (qualified) name of the fucntions
    @attribute args Comma separated list of expressions representing parameters.
  */
  functionCall : calleeName=NAME '(' (args=arguments)? ')';

  arguments : expr (',' expr)*;


  /*********************************************************************************************************************
  * Equations-Language
  *********************************************************************************************************************/
  /** ASTOdeDeclaration. Represents a block of equations and differential equations.

    @attribute Equation      List with equations, e.g. "I = exp(t)" od differential equations.
  */
  odeDeclaration  : (equation | shape | odeFunction | NEWLINE)+;

  odeFunction : (recordable='recordable')? 'function' variableName=NAME datatype '=' expr;

  /** ASTeq Represents an equation, e.g. "I = exp(t)" or represents an differential equations, e.g. "V_m' = V_m+1".
    @attribute lhs      Left hand side, e.g. a Variable.
    @attribute rhs      Expression defining the right hand side.
  */
  equation : lhs=derivative '=' rhs=expr;

  derivative : name=NAME (differentialOrder='\'')*;

  shape : 'shape' lhs=variable '=' rhs=expr;

  /*********************************************************************************************************************
  * Procedural-Language
  *********************************************************************************************************************/

  block : ( stmt | NEWLINE )*;

  stmt : small_Stmt | compound_Stmt;

  compound_Stmt : if_Stmt
                | for_Stmt
                | while_Stmt;

  small_Stmt : assignment
             | functionCall
             | declaration
             | returnStmt;

  assignment : lhsVariable=variable
    (directAssignment='='       |
     compoundSum='+='     |
     compoundMinus='-='   |
     compoundProduct='*=' |
     compoundQuotient='/=') expr;


  /** ASTDeclaration A variable declaration. It can be a simple declaration defining one or multiple variables:
   'a,b,c real = 0'. Or an function declaration 'function a = b + c'.
    @attribute hide is true iff. declaration is not trackable.
    @attribute function is true iff. declaration is an function.
    @attribute vars          List with variables
    @attribute Datatype      Obligatory data type, e.g. 'real' or 'mV/s'
    @attribute sizeParameter An optional array parameter. E.g. 'tau_syn ms[n_receptros]'
    @attribute expr An optional initial expression, e.g. 'a real = 10+10'
    @attribute invariants List with optional invariants.
   */
  declaration :
    ('recordable')? ('function')?
    variable (',' variable)*
    datatype
    ('[' sizeParameter=NAME ']')?
    ( '=' expr)? SL_COMMENT?
    ('[[' invariant=expr ']]')?;

  /** ATReturnStmt Models the return statement in a function.

    @attribute minus An optional sing
    @attribute definingVariable Name of the variable
   */
  returnStmt : 'return' expr?;

  if_Stmt : if_Clause
            elif_Clause*
            (else_Clause)?
            BLOCK_CLOSE;

  if_Clause : 'if' expr BLOCK_OPEN block;

  elif_Clause : 'elif' expr BLOCK_OPEN block;

  else_Clause : 'else' BLOCK_OPEN block;

  for_Stmt : 'for' var=NAME 'in' vrom=expr '...' to=expr 'step' step=signedNumericLiteral BLOCK_OPEN block BLOCK_CLOSE;

  while_Stmt : 'while' expr BLOCK_OPEN block BLOCK_CLOSE;

  signedNumericLiteral : (negative='-') NUMERIC_LITERAL;

  /*********************************************************************************************************************
  * Nestml-Language
  *********************************************************************************************************************/
  /** ASTNeuron represents neuron.
    @attribute Name    The name of the neuron
    @attribute Body    The body of the neuron, e.g. internal, state, parameter...
  */
  neuron : 'neuron' NAME body;

  /** ASTBody The body of the neuron, e.g. internal, state, parameter...
  */
  body : BLOCK_OPEN
           (NEWLINE | var_Block | dynamics | equations | inputBuffer | outputBuffer | function)*
         BLOCK_CLOSE;

  /** ASTVar_Block represent a block with variables, e.g.:
    state:
      y0, y1, y2, y3 mV [y1 > 0; y2 > 0]
    end

    @attribute state true if the varblock ist a state.
    @attribute parameter true if the varblock ist a parameter.
    @attribute internal true if the varblock ist a state internal.
    @attribute AliasDecl a list with variable declarations.
  */
  var_Block:
    ('state'|'parameters'|'internals')
    BLOCK_OPEN
      (declaration | NEWLINE)*
    BLOCK_CLOSE;

  /** ASTDynamics a special function definition:
      update:
        if r == 0: # not refractory
          integrate(V)
        end
      end
     @attribute block Implementation of the dynamics.
   */
  dynamics:
    'update'
    BLOCK_OPEN
      block
    BLOCK_CLOSE;

  /** ASTEquations a special function definition:
       equations:
         G = (e/tau_syn) * t * exp(-1/tau_syn*t)
         V' = -1/Tau * V + 1/C_m * (I_sum(G, spikes) + I_e + currents)
       end
     @attribute odeDeclaration Block with equations and differential equations.
   */
  equations:
    'equations'
    BLOCK_OPEN
      odeDeclaration
    BLOCK_CLOSE;

  /** ASTInput represents the input block:
    input:
      spikeBuffer   <- inhibitory excitatory spike
      currentBuffer <- current
    end

    @attribute inputLine set of input lines.
  */
  inputBuffer: 'input'
    BLOCK_OPEN
      (inputLine | NEWLINE)*
    BLOCK_CLOSE;

  /** ASTInputLine represents a single line form the input, e.g.:
      spikeBuffer   <- inhibitory excitatory spike

    @attribute sizeParameter Optional parameter representing  multisynapse neuron.
    @attribute sizeParameter Type of the inputchannel: e.g. inhibitory or excitatory (or both).
    @attribute spike true iff the neuron is a spike.
    @attribute current true iff. the neuron is a current.
  */
  inputLine :
    NAME
    ('[' sizeParameter=NAME ']')?
    '<-' inputType*
    ('spike' | 'current');

  /** ASTInputType represents the type of the inputline e.g.: inhibitory or excitatory:
    @attribute inhibitory true iff the neuron is a inhibitory.
    @attribute excitatory true iff. the neuron is a excitatory.
  */
  inputType : ('inhibitory' | 'excitatory');

  /** ASTOutput represents the output block of the neuron:
        output: spike
      @attribute spike true iff the neuron has a spike output.
      @attribute current true iff. the neuron is a current output.
    */
  outputBuffer: 'output' BLOCK_OPEN ('spike' | 'current') ;

  /** ASTFunction a function definition:
      function set_V_m(v mV):
        y3 = v - E_L
      end
    @attribute name Functionname.
    @attribute parameters List with function parameters.
    @attribute returnType Complex return type, e.g. String
    @attribute primitiveType Primitive return type, e.g. int
    @attribute block Implementation of the function.
  */
  function: 'function' NAME '(' parameters? ')' (returnType=datatype)?
           BLOCK_OPEN
             block
           BLOCK_CLOSE;

  /** ASTParameters models parameter list in function declaration.
    @attribute parameters List with parameters.
  */
  parameters : parameter (',' parameter)*;

  /** ASTParameter represents singe:
      output: spike
    @attribute compartments Lists with compartments.
  */
  parameter : NAME datatype;