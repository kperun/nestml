package org.nest.codegeneration.helpers.LEMSElements;

import java.util.*;

import org.nest.codegeneration.helpers.Collector;
import org.nest.codegeneration.helpers.Expressions.*;
import org.nest.commons._ast.ASTExpr;
import org.nest.nestml._ast.*;
import org.nest.ode._ast.ASTEquation;
import org.nest.ode._ast.ASTOdeFunction;
import org.nest.ode._ast.ASTShape;
import org.nest.spl._ast.ASTStmt;
import org.nest.spl.prettyprinter.LEMS.LEMSExpressionsPrettyPrinter;
import org.nest.symboltable.symbols.TypeSymbol;
import org.nest.symboltable.symbols.VariableSymbol;
import org.nest.units._ast.ASTDatatype;
import org.nest.units._ast.ASTUnitType;

import static com.google.common.base.Preconditions.checkNotNull;

/**
 * This class provides an infrastructure which generates an internal,processed representation of an input model, which
 * is further used in the template.
 * It further utilizes org.nest.spl.prettyprinter.LEMS.ExpressionPrettyPrinterCustom in order to convert
 * declarations and function-calls as well as instructions to a proper syntax used by LEMS.
 *
 * @author perun
 */
public class LEMSCollector extends Collector {
    private LEMSSyntaxContainer syntax = new LEMSSyntaxContainer();

    private String neuronName;

    private Optional<String> extendedModel = Optional.empty();

    private LEMSExpressionsPrettyPrinter prettyPrint;//used in order to convert expressions to LEMS syntax

    private DynamicRoutine routine;//An internal representation of the update-block.

    private Set<Unit> unitsSet = null;//Collects all units

    private Set<Dimension> dimensionsSet = null;//Collects all dimension

    private List<Constant> constantsList = null;//Collects all constants

    private List<DerivedElement> derivedElementList = null;//Collects all derived variables

    private List<StateVariable> stateVariablesList = null;//Collects all state variables

    private List<EventPort> portsList = null;//Collects all event-ports

    private List<String> notConverted = null;//List of not converted elements

    private Map<String, Expression> equation = null;//a map of variables and the corresponding equation

    private List<String> localTimeDerivative = null;//a list of time derivatives which are only invoked in certain steps

    private List<Attachment> attachments = null;//a list of attachments to the neuron

    private SimulationConfiguration config = null;// the configuration of the simulation

    private List<String> booleanElements = null;

    private Map<Expression, String> guards = null;


    public LEMSCollector(ASTNeuron neuron, SimulationConfiguration config) {
        //set the system language to english in order to avoid problems with "," instead of "." in double representation
        Locale.setDefault(Locale.ENGLISH);
        this.portsList = new ArrayList<>();
        this.unitsSet = new HashSet<>();
        this.dimensionsSet = new HashSet<>();
        this.constantsList = new ArrayList<>();
        this.derivedElementList = new ArrayList<>();
        this.stateVariablesList = new ArrayList<>();
        this.notConverted = new ArrayList<>();
        this.prettyPrint = new LEMSExpressionsPrettyPrinter(this);
        this.equation = new HashMap<>();
        this.localTimeDerivative = new ArrayList<>();
        this.attachments = new ArrayList<>();
        this.config = config;
        this.booleanElements = new ArrayList<>();
        this.guards = new HashMap<>();
        this.handleNeuron(neuron);
    }

    /**
     * This is the main procedure which invokes all subroutines for processing of concrete elements of the model.
     * All elements are collected, transformed to internal representation and stored in corresponding containers.
     *
     * @param neuron The neuron which will be processed.
     */
    private void handleNeuron(ASTNeuron neuron) {
        neuronName = neuron.getName();

        //first adapt the settings according to the handed over artifact if required
        config.adaptSettings(this);

        //checks whether the model extends an other model
        if (neuron.getBase().isPresent()) {
            extendedModel = Optional.of(neuron.getBase().get());//store the name of the extended model
        }
        ASTBody neuronBody = neuron.getBody();

        //process user defined functions in simple way
        //we process user defined functions at the beginning in order to mark them as supported
        this.handleUserDefinedFunctions(neuronBody);

        //collect all boolean elements
        this.collectBooleanElements(neuronBody);

        //processes all non-alias elements of the state block
        this.handleStateNonAliases(neuronBody);

        //processes all alias elements of the state block
        this.handleStateAliases(neuronBody);

        //process the equations block
        if (!neuronBody.getEquations().isEmpty()) {
            //create a new constant in order to achieve a correct dimension of the equation:
            ASTUnitType tempType = new ASTUnitType();
            tempType.setUnit("ms");
            this.addConstant(new Constant(HelperCollection.PREFIX_CONSTANT + "1_ms", HelperCollection.PREFIX_DIMENSION + "ms", new NumericalLiteral(1, tempType), false));
            Dimension msDimension = new Dimension(HelperCollection.PREFIX_DIMENSION + "ms", 0, 0, 1, 0, 0, 0, 0);
            this.addDimension(msDimension);
            this.addUnit(new Unit("ms", HelperCollection.powerConverter("ms"), msDimension));

            //first process all shapes of the model
            this.handleShapes(neuronBody);

            //process the defining differential equation, i.e. non "shapes"
            this.handleEquations(neuronBody);

            //finally process all "function" declarations inside the equations block
            this.handleODEFunctions(neuronBody);
        }

        //processes all non-aliases in the parameter block, namely the constants
        this.handleParameterNonAliases(neuronBody);

        //processes all aliases in the parameter, namely the derived constants
        this.handleParameterAliases(neuronBody);

        //processes all non-alias declarations of the internal block
        this.handleInternalNonAliases(neuronBody);

        //processes all alias declarations of the internal block
        this.handleInternalAliases(neuronBody);

        //process the buffers
        this.handleBuffers(neuronBody);

        //check whether the modeled neuron contains a dynamic routine, and if so, generate a corresponding routine
        this.handleDynamicsBlock(neuronBody);

        //if no spike directive is present, an artificial event out directive has to be added in order to activate the port
        this.addPortActivator();

        //finally process all guards
        this.handleGuards(neuronBody);

    }

    /**
     * Handles all non-aliases located in the state block of the model.
     *
     * @param neuronBody a neuron body containing a state block.
     */
    private void handleStateNonAliases(ASTBody neuronBody) {
        checkNotNull(neuronBody);
        for (VariableSymbol var : neuronBody.getStateNonAliasSymbols()) {
            if (var.isVector()) {//arrays are not supported by LEMS
                HelperCollection.printArrayNotSupportedMessage(var, this);
                this.addNotConverted(HelperCollection.getArrayNotSupportedMessage(var));
            } else {
                //otherwise process the object to a state variable
                this.addStateVariable(new StateVariable(var, this));
                handleType(var.getType());//handle the type of the variable
            }
        }

    }


    /**
     * Handles all aliases stated in the state block of the model.
     *
     * @param neuronBody a neuron body containing a state block
     */
    private void handleStateAliases(ASTBody neuronBody) {
        checkNotNull(neuronBody);
        for (VariableSymbol var : neuronBody.getStateAliasSymbols()) {
            this.addDerivedElement(new DerivedElement(var, this, true, false));
            handleType(var.getType());//handle the type
        }
    }

    /**
     * Handles user defined functions as stated in the source model. This method converts a stated user defined functions
     * to a set of derived variables.
     *
     * @param neuronBody a neuron body containing a "user-defined functions" block
     */
    private void handleUserDefinedFunctions(ASTBody neuronBody) {
        checkNotNull(neuronBody);
        for (ASTFunction func : neuronBody.getFunctions()) {
            //first handle the signature of the function
            if (func.parametersIsPresent()) {
                for (ASTParameter param : func.getParameters().get().getParameters()) {
                    //not all params have to have a unit
                    Optional<Unit> tempUnit = handleType(param.getDatatype());
                    Expression defaultValue;
                    StateVariable paramStateVar;
                    if (tempUnit.isPresent()) {
                        defaultValue = new NumericalLiteral(0, param.getDatatype().getUnitType().get());
                        defaultValue = HelperCollection.replaceConstantsWithReferences(this, defaultValue);
                        paramStateVar = new StateVariable(param.getName(),
                                HelperCollection.typeToDimensionConverter(param.getDatatype()),
                                defaultValue, Optional.of(tempUnit.get().getSymbol()));

                    } else {
                        defaultValue = new NumericalLiteral(0, null);
                        paramStateVar = new StateVariable(param.getName(),
                                HelperCollection.typeToDimensionConverter(param.getDatatype()),
                                defaultValue, Optional.empty());
                    }
                    this.addStateVariable(paramStateVar);
                }


            }
            //handle the return type of the function
            this.handleType(func.getReturnType().get());

            //for each statement in the declaration, execute the following
            for (ASTStmt stmt : func.getBlock().getStmts()) {
                //we only support small statements
                if (stmt.small_StmtIsPresent()) {
                    if (stmt.getSmall_Stmt().get().declarationIsPresent()) {
                        this.handleType(stmt.getSmall_Stmt().get().getDeclaration().get().getDatatype());
                        for (String name : stmt.getSmall_Stmt().get().getDeclaration().get().getVars()) {
                            DerivedElement tempVar = new DerivedElement(name, stmt.getSmall_Stmt().get().getDeclaration().get(), this);
                            this.addDerivedElement(tempVar);
                        }
                    } else if (stmt.getSmall_Stmt().get().returnStmtIsPresent()) {
                        Expression tempExpr = new Expression(stmt.getSmall_Stmt().get().getReturnStmt().get().getExpr().get());
                        tempExpr = HelperCollection.replacementRoutine(this,tempExpr);

                        DerivedElement tempVar = new DerivedElement(func.getName(), HelperCollection.typeToDimensionConverter(func.getReturnType().get()),
                                tempExpr, true, false);
                        this.addDerivedElement(tempVar);

                    }
                } else {
                    System.err.println("LEMS-Error ( " + this.neuronName + " )): compound statement in function declaration not supported.");
                }
            }
        }

    }

    /**
     * Handles all shapes of the given neuron model, i.e. all non-equations and all non-ode-functions of the model
     * as located in the equations block.
     *
     * @param neuronBody a neuron body with defined equations block.
     */
    private void handleShapes(ASTBody neuronBody) {
        checkNotNull(neuronBody);
        for (int i = 0; i < neuronBody.getShapes().size(); i++) {
            ASTShape eq = neuronBody.getShapes().get(i);
            if (HelperCollection.containsFunctionCall(eq.getRhs(), true, this)) {
                HelperCollection.printNotSupportedFunctionCallInEquations(eq, this);
                this.addNotConverted("Not supported function call(s) found in shape of \"" + eq.getLhs().getName().toString() + "\" in lines" + eq.get_SourcePositionStart() + " to " + eq.get_SourcePositionEnd() + ".");
                equation.put(eq.getLhs().getName().toString(), new Expression(eq.getRhs()));
            } else {
                Expression tempExpression = HelperCollection.replaceResolutionByConstantReference(this, new Expression(eq.getRhs()));
                DerivedElement shapeVariable = new DerivedElement(eq.getLhs().getName().toString(), HelperCollection.DIMENSION_NONE, tempExpression, true, false);
                //store the shape
                this.addDerivedElement(shapeVariable);
            }

        }
    }

    /**
     * Handles the equations located in the equations block, i.e. non-shapes and non ode-functions.
     *
     * @param neuronBody a neuron body containing equations.
     */
    private void handleEquations(ASTBody neuronBody) {
        checkNotNull(neuronBody);
        for (int i = 0; i < neuronBody.getEquations().size(); i++) {
            ASTEquation eq = neuronBody.getEquations().get(i);
            if (HelperCollection.containsFunctionCall(eq.getRhs(), true, this)) {
                HelperCollection.printNotSupportedFunctionCallFoundMessage(eq, this);
                this.addNotConverted("Not supported function call(s) found in differential equation of \"" + eq.getLhs().getName().toString() + "\" in lines " + eq.get_SourcePositionStart() + " to " + eq.get_SourcePositionEnd() + ".");
                equation.put(eq.getLhs().toString(), new Expression(eq.getRhs()));
            } else {
                List<String> tempList = new ArrayList<>();
                tempList.add(eq.getLhs().getSimpleName());// a list is required, since method blockContains requires lists of args.
                //check if somewhere in the update block an integrate directive has been used, if so, the equation has to be local
                if (HelperCollection.blockContainsFunction("integrate", tempList, neuronBody.getDynamicsBlock().get().getBlock(), this)) {
                    Expression expr = new Expression(eq.getRhs());
                    expr = HelperCollection.buildExpressionWithActivator(eq.getLhs().toString(), expr);
                    expr = HelperCollection.extendExpressionByCON1ms(expr);
                    expr = HelperCollection.replaceConstantsWithReferences(this, expr);
                    expr = HelperCollection.replaceResolutionByConstantReference(this, expr);
                    //only ode, i.e. integrate directives have to be manipulated
                    equation.put(eq.getLhs().getSimpleName(), expr);
                    //now generate the corresponding activator
                    this.stateVariablesList.add(new StateVariable(HelperCollection.PREFIX_ACT + eq.getLhs().getSimpleName(),
                            HelperCollection.DIMENSION_NONE, new NumericalLiteral(1, null), Optional.empty()));
                    this.localTimeDerivative.add(eq.getLhs().getSimpleName());
                } else {
                    //otherwise the integration is global, no further steps required
                    Expression expr = new Expression(eq.getRhs());
                    expr = HelperCollection.extendExpressionByCON1ms(expr);
                    expr = HelperCollection.replaceConstantsWithReferences(this, expr);
                    expr = HelperCollection.replaceResolutionByConstantReference(this, expr);
                    equation.put(eq.getLhs().getSimpleName(), expr);
                }
            }
        }
    }

    /**
     * Checks if there are any ODE functions present in the model and transforms them to LEMS counter pieces.
     *
     * @param neuronBody a neuron body containing ODE functions
     */
    private void handleODEFunctions(ASTBody neuronBody) {
        checkNotNull(neuronBody);
        for (int i = 0; i < neuronBody.getODEBlock().get().getOdeFunctions().size(); i++) {
            ASTOdeFunction tempFunction = neuronBody.getODEBlock().get().getOdeFunctions().get(i);
            DerivedElement tempDerivedVar;
            if (tempFunction.getDatatype().getUnitType().isPresent()) {
                Dimension tempDimension;
                Unit tempUnit;
                int[] dec = HelperCollection.convertTypeDeclToArray(
                        tempFunction.getDatatype().getUnitType().get().getSerializedUnit());

                if (tempFunction.getDatatype().getUnitType().get().unitIsPresent()) {
                    //create the required units and dimensions
                    tempDimension = new Dimension(HelperCollection.PREFIX_DIMENSION
                            + tempFunction.getDatatype().getUnitType().get().getUnit().get(),
                            dec[2], dec[3], dec[1], dec[6], dec[0], dec[5], dec[4]);
                    tempUnit = new Unit(tempFunction.getDatatype().getUnitType().get().getUnit().get(),
                            dec[7], tempDimension);
                } else {//it is a combined unit, e.g. mV/s
                    Expression tempExr = HelperCollection.getExpressionFromUnitType(tempFunction.getDatatype().
                            getUnitType().get());
                    tempDimension = new Dimension(HelperCollection.PREFIX_DIMENSION
                            + (HelperCollection.formatComplexUnit(tempExr.print())),
                            dec[2], dec[3], dec[1], dec[6], dec[0], dec[5], dec[4]);
                    //in order to retrieve the name of the unit getExpressionFromUnitType is called
                    tempUnit = new Unit(HelperCollection.formatComplexUnit(tempExr.print()), dec[7], tempDimension);
                }
                if (tempFunction.getExpr().conditionIsPresent()) {
                    tempDerivedVar = new DerivedElement(
                            tempFunction.getVariableName(),
                            tempDimension.getName(),
                            tempFunction.getExpr(),
                            this, false);
                } else {
                    Expression tempExpression = new Expression(tempFunction.getExpr());
                    tempExpression = HelperCollection.replaceResolutionByConstantReference(this, tempExpression);
                    tempExpression = HelperCollection.replaceConstantsWithReferences(this, tempExpression);
                    tempDerivedVar = new DerivedElement(
                            tempFunction.getVariableName(),
                            tempDimension.getName(),
                            tempExpression,
                            true,
                            false);
                }


                this.addDimension(tempDimension);
                this.addUnit(tempUnit);
            } else {
                //otherwise it is a non dimensional function, e.g. real
                if (tempFunction.getExpr().conditionIsPresent()) {
                    tempDerivedVar = new DerivedElement(
                            tempFunction.getVariableName(),
                            HelperCollection.DIMENSION_NONE,
                            tempFunction.getExpr(),
                            this, false);
                } else {
                    tempDerivedVar = new DerivedElement(
                            tempFunction.getVariableName(),
                            HelperCollection.DIMENSION_NONE,
                            new Expression(tempFunction.getExpr()),
                            true,
                            false);
                }


            }
            this.addDerivedElement(tempDerivedVar);
        }
    }


    /**
     * Handles all non aliases of the parameter block.
     *
     * @param neuronBody a neuron body containing a parameter block.
     */
    private void handleParameterNonAliases(ASTBody neuronBody) {
        checkNotNull(neuronBody);
        for (VariableSymbol var : neuronBody.getParameterNonAliasSymbols()) {
            if (var.isVector()) {//arrays are not supported by LEMS
                //print error message
                HelperCollection.printArrayNotSupportedMessage(var, this);
                this.addNotConverted(HelperCollection.getArrayNotSupportedMessage(var));
            } else {
                Constant temp = null;
                DerivedElement tempDerivedElement = null;
                StateVariable tempStateVariable = null;
                if (var.getDeclaringExpression().isPresent()) {
                    //first check if a ternary operator is used
                    if (var.getDeclaringExpression().get().conditionIsPresent()) {
                        tempDerivedElement = new DerivedElement(var.getName(),
                                HelperCollection.typeToDimensionConverter(var.getType()),
                                var.getDeclaringExpression().get(),
                                this, false);
                        if (var.getType().getType() == TypeSymbol.Type.UNIT) {
                            tempStateVariable = new StateVariable(var.getName(), tempDerivedElement.getDimension(), new Variable(tempDerivedElement.getName()),
                                    Optional.of(var.getType().prettyPrint()));
                        } else {
                            tempStateVariable = new StateVariable(var.getName(), tempDerivedElement.getDimension(), new Variable(tempDerivedElement.getName()),
                                    Optional.empty());//no unit,therefore "" as 4th arg
                        }
                    } else if (var.getDeclaringExpression().get().exprIsPresent()) {
                        //in the case it is an expression, e.g. 10mV+V_m
                        tempDerivedElement = new DerivedElement(var, this, false, false);

                        //in the case it is a expression consisting of a left and a right hand side
                    } else if (var.getDeclaringExpression().get().leftIsPresent() && var.getDeclaringExpression().get().rightIsPresent()) {
                        Expression tempExpression = new Expression(var);
                        tempExpression = HelperCollection.replaceConstantsWithReferences(this, tempExpression);
                        tempExpression = HelperCollection.replaceResolutionByConstantReference(this, tempExpression);
                        tempDerivedElement = new DerivedElement(var.getName(), HelperCollection.typeToDimensionConverter(var.getType()),
                                tempExpression, false, false);
                        //in the case it is an exponential expression
                    } else if (var.getDeclaringExpression().get().baseIsPresent() && var.getDeclaringExpression().get().exponentIsPresent()) {
                        Expression tempExpression = new Expression(var);
                        tempExpression = HelperCollection.replaceConstantsWithReferences(this, tempExpression);
                        tempExpression = HelperCollection.replaceResolutionByConstantReference(this, tempExpression);
                        tempDerivedElement = new DerivedElement(var.getName(), HelperCollection.typeToDimensionConverter(var.getType()),
                                tempExpression, false, false);

                    } else {
                        //if a declaring value is present -> generate a constant
                        temp = new Constant(var, false, false, this);
                    }
                } else {
                    //otherwise generate a parameter
                    temp = new Constant(var, false, true, this);
                }
                //finally add the new constant
                if (temp != null)
                    this.addConstant(temp);
                if (tempDerivedElement != null)
                    this.addDerivedElement(tempDerivedElement);
                if (tempStateVariable != null)
                    this.addStateVariable(tempStateVariable);
            }
            handleType(var.getType());
        }

    }

    /**
     * Checks if any guards are given for parameters and constants ad if so, generates proper instructions.
     *
     * @param neuronBody a neuron body possibly containing guards
     */
    private void handleGuards(ASTBody neuronBody) {
        //now check all guards and generate corresponding counter pieces in LEMS
        if (!neuronBody.getParameterInvariants().isEmpty()) {
            //we need a variable for an assignment which results in a crash. in order to make such variables more obvious, we name named them specially
            StateVariable tempVar = new StateVariable(HelperCollection.GUARD_NAME, HelperCollection.DIMENSION_NONE,
                    new NumericalLiteral(0, null), Optional.empty());
            this.addStateVariable(tempVar);
            //finally process each guard
            Expression tempExpression;
            List<ASTExpr> rawGuards = new ArrayList<>();
            //now first collect from each block the guards
            rawGuards.addAll(neuronBody.getParameterInvariants());
            rawGuards.addAll(HelperCollection.getStateInvariants(neuronBody));
            rawGuards.addAll(HelperCollection.getInternalsInvariants(neuronBody));
            for (ASTExpr expr : rawGuards) {
                tempExpression = new Expression(expr);
                tempExpression.negateLogic();
                tempExpression = HelperCollection.replaceResolutionByConstantReference(this, tempExpression);
                tempExpression = HelperCollection.replaceConstantsWithReferences(this, tempExpression);
                this.addGuard(HelperCollection.GUARD_NAME, tempExpression);
            }
        }
    }


    /**
     * Handles all aliases in the parameter block of the neuron.
     *
     * @param neuronBody a neuron body containing a parameter block.
     */
    private void handleParameterAliases(ASTBody neuronBody) {
        checkNotNull(neuronBody);
        for (VariableSymbol var : neuronBody.getParameterAliasSymbols()) {
            this.addDerivedElement(new DerivedElement(var, this, false, false));
            handleType(var.getType());
        }
    }

    /**
     * Handles all non aliases located in the internal block.
     *
     * @param neuronBody a neuron body containing a internal block.
     */
    private void handleInternalNonAliases(ASTBody neuronBody) {
        checkNotNull(neuronBody);
        for (VariableSymbol var : neuronBody.getInternalNonAliasSymbols()) {
            if (var.isVector()) {//lems does not support arrays
                //print an adequate message
                HelperCollection.printArrayNotSupportedMessage(var, this);
                this.addNotConverted(HelperCollection.getArrayNotSupportedMessage(var));
            } else {//the declaration does not use arrays
                //is a right hand side present?
                if (var.getDeclaringExpression().isPresent()) {
                    //handle resolution()
                    if (var.getDeclaringExpression().get().functionCallIsPresent() &&
                            var.getDeclaringExpression().get().getFunctionCall().get().getName().toString().equals("resolution")) {
                        ASTUnitType tempType = new ASTUnitType();
                        tempType.setUnit(config.getSimulation_steps_unit().getSymbol());
                        NumericalLiteral tempNumerical = new NumericalLiteral(config.getSimulation_steps_length(), tempType);
                        Constant tempConstant = new Constant(var.getName(), config.getSimulation_steps_unit().
                                getDimensionName(), tempNumerical, false);
                        this.addConstant(tempConstant);
                        //handle steps()
                    } else if (var.getDeclaringExpression().get().functionCallIsPresent() &&
                            var.getDeclaringExpression().get().getFunctionCall().get().getName().toString().equals("steps")) {

                        List<ASTExpr> args = var.getDeclaringExpression().get().getFunctionCall().get().getArgs();
                        Expression lhs = null;
                        //handle a numerical lit, e.g. 10ms
                        if (args.get(0).nESTMLNumericLiteralIsPresent()) {
                            lhs = new NumericalLiteral(args.get(0).getNESTMLNumericLiteral().get());
                            //handle a variable ref, e.g. res_init
                        } else if (args.get(0).variableIsPresent()) {
                            lhs = new Variable(args.get(0).getVariable().get());
                            //handle an expression, e.g. 10ms + res_init
                        } else if (args.get(0).leftIsPresent() && args.get(0).rightIsPresent()) {
                            lhs = new Expression();
                            lhs.replaceLhs(new Expression(args.get(0).getLeft().get()));
                            lhs.replaceOp(new Operator(args.get(0)));
                            lhs.replaceRhs(new Expression(args.get(0).getRight().get()));
                        }
                        lhs = Expression.encapsulateInBrackets(lhs);
                        Operator tempOp = new Operator();
                        tempOp.setDivOp(true);

                        ASTUnitType tempType = new ASTUnitType();
                        tempType.setUnit(config.getSimulation_steps_unit().getSymbol());
                        NumericalLiteral rhs = new NumericalLiteral(config.getSimulation_steps_length(), tempType);

                        Expression tempExpr = new Expression();
                        tempExpr.replaceLhs(lhs);
                        tempExpr.replaceOp(tempOp);
                        tempExpr.replaceRhs(rhs);
                        tempExpr = HelperCollection.replaceConstantsWithReferences(this, tempExpr);
                        tempExpr = HelperCollection.replaceResolutionByConstantReference(this, tempExpr);
                        this.addDerivedElement(new DerivedElement(var.getName(), HelperCollection.typeToDimensionConverter(var.getType()),
                                tempExpr, false, false));


                    } else if (HelperCollection.containsFunctionCall(var.getDeclaringExpression().get(), true, this)) {
                        HelperCollection.printNotSupportedFunctionCallInExpression(var, this);
                    } else {// otherwise it is either an expression or does contain a yet different type of function call.
                        if (var.getDeclaringExpression().get().exprIsPresent()) {
                            Expression tempExpression = new Expression(var.getDeclaringExpression().get().getExpr().get());
                            tempExpression = HelperCollection.replaceConstantsWithReferences(this, tempExpression);
                            tempExpression = HelperCollection.replaceResolutionByConstantReference(this, tempExpression);
                            DerivedElement tempElem = new DerivedElement(var.getName(),
                                    HelperCollection.typeToDimensionConverter(var.getType()), tempExpression, true, false);
                            this.addDerivedElement(tempElem);
                        } else if (var.getDeclaringExpression().get().termIsPresent()) {
                            Expression tempExpression = new Expression(var.getDeclaringExpression().get().getTerm().get());
                            tempExpression = HelperCollection.replaceConstantsWithReferences(this, tempExpression);
                            tempExpression = HelperCollection.replaceResolutionByConstantReference(this, tempExpression);
                            DerivedElement tempElem = new DerivedElement(var.getName(),
                                    HelperCollection.typeToDimensionConverter(var.getType()), tempExpression, true, false);
                            this.addDerivedElement(tempElem);
                            // handle ternary op
                        } else if (var.getDeclaringExpression().get().conditionIsPresent()) {
                            DerivedElement tempElem = new DerivedElement(var.getName(),
                                    HelperCollection.typeToDimensionConverter(var.getType()), var.getDeclaringExpression().get(), this, true);
                            this.addDerivedElement(tempElem);
                            if (var.getType().getType() == TypeSymbol.Type.UNIT) {
                                Unit tempUnit = new Unit(var.getType());
                                this.addStateVariable(new StateVariable(var.getName(), HelperCollection.typeToDimensionConverter(var.getType()),
                                        new Variable(tempElem.getName()), Optional.of(tempUnit.getSymbol())));
                            } else {
                                this.addStateVariable(new StateVariable(var.getName(), HelperCollection.typeToDimensionConverter(var.getType()),
                                        new Variable(tempElem.getName()), Optional.empty()));
                            }
                            // handle boolean literal or numLiteral, e.g. 1mV
                        } else if (var.getDeclaringExpression().get().booleanLiteralIsPresent() ||
                                var.getDeclaringExpression().get().nESTMLNumericLiteralIsPresent()) {
                            Expression tempExpression = new Expression(var.getDeclaringExpression().get());
                            Constant tempConstant = new Constant(var.getName(),
                                    HelperCollection.typeToDimensionConverter(var.getType()), tempExpression, false);
                            this.addConstant(tempConstant);
                            //e.g 1mV+50mV or 1mV+V_init
                        } else if (var.getDeclaringExpression().get().getLeft().isPresent() &&
                                var.getDeclaringExpression().get().getRight().isPresent()) {
                            Expression leftExpr = new Expression(var.getDeclaringExpression().get().getLeft().get());
                            Operator op = new Operator(var.getDeclaringExpression().get());
                            Expression rightExpr = new Expression(var.getDeclaringExpression().get().getRight().get());
                            Expression combined = new Expression();
                            combined.replaceLhs(leftExpr);
                            combined.replaceOp(op);
                            combined.replaceRhs(rightExpr);
                            combined = HelperCollection.replacementRoutine(this,combined);
                            DerivedElement tempElem = new DerivedElement(var.getName(), HelperCollection.typeToDimensionConverter(var.getType()),
                                    combined, false, false);
                            this.addDerivedElement(tempElem);
                            //e.g. v real = v_init
                        } else if (var.getDeclaringExpression().get().variableIsPresent()) {
                            StateVariable tempVariable = new StateVariable(var, this);
                            this.addStateVariable(tempVariable);
                        } else if (var.getDeclaringExpression().get().functionCallIsPresent()) {
                            if (HelperCollection.containsFunctionCall(var.getDeclaringExpression().get(), true, this)) {
                                HelperCollection.printNotSupportedFunctionCallInExpression(var, this);
                                this.addNotConverted("Not supported function call in internals, line: " +
                                        var.getSourcePosition().getLine());
                            }
                            //TODO: here add replacement!!!
                            Expression tempExpression = new Expression(var.getDeclaringExpression().get());
                            DerivedElement tempElem = new DerivedElement(var.getName(), HelperCollection.typeToDimensionConverter(var.getType()),
                                    tempExpression, false, false);
                            this.addDerivedElement(tempElem);
                        } else {
                            System.err.println("INTERNAL NOT SUPPORTED:" + var.getName() + ":" + var.getSourcePosition().getLine());
                        }
                        handleType(var.getType());
                    }

                } else {//no right hand site -> its a variable
                    this.addStateVariable(new StateVariable(var, this));
                    handleType(var.getType());
                }

            }

        }
    }

    /**
     * Checks if some aliases are present in the internal block and processes them in an appropriate way.
     *
     * @param neuronBody the body possibly containing aliases
     */
    private void handleInternalAliases(ASTBody neuronBody) {
        checkNotNull(neuronBody);
        for (VariableSymbol var : neuronBody.getInternalAliasSymbols()) {
            this.addDerivedElement(new DerivedElement(var, this, false, false));
            handleType(var.getType());
        }
    }

    /**
     * Handles the buffers located in the neuron.
     *
     * @param neuronBody the ast body of a neuron
     */
    private void handleBuffers(ASTBody neuronBody) {
        checkNotNull(neuronBody);
        // processes all input-buffers
        Attachment tempAttachment = null;
        DerivedElement tempDerivedVar = null;
        Dimension tempDimesion = null;
        Unit tempUnit = null;
        for (ASTInputLine var : neuronBody.getInputLines()) {
            if (var.isCurrent()) {
                //a current input buffer has the dimension of pA, thus generate such a unit and dimension
                if (tempDimesion == null) {
                    tempDimesion = new Dimension(HelperCollection.PREFIX_DIMENSION + "pA",
                            0, 0, 0, 1, 0, 0, 0);
                    tempUnit = new Unit("pA", -12, tempDimesion);
                }
                tempAttachment = new Attachment(var.getName(), "baseSynapse");//TODO: here further changes can be done
            } else {//is spike
                tempAttachment = new Attachment(var.getName(), "baseSynapse");
            }
            tempDerivedVar = new DerivedElement(var);
            this.addDerivedElement(tempDerivedVar);
            this.addAttachment(tempAttachment);

            if (tempDimesion != null & tempUnit != null) {
                this.addDimension(tempDimesion);
                this.addUnit(tempUnit);
            }

        }
        //processes all output-buffers
        for (ASTOutput var : neuronBody.getOutputs()) {
            this.addEventPort(new EventPort(var));
        }

    }

    /**
     * Checks if a dynamic routine is present and handles it.
     *
     * @param neuronBody the body of a neuron
     */
    private void handleDynamicsBlock(ASTBody neuronBody) {
        checkNotNull(neuronBody);
        if (neuronBody.getDynamicsBlock().isPresent()) {
            routine = new DynamicRoutine(neuronBody.getDynamics(), this);
        }
    }

    /**
     * This sub-routine handles the processing of a unit, thus converts it to an adequate internal representation.
     *
     * @param var The variable which will processed.
     */
    private Optional<Unit> handleType(TypeSymbol var) {
        // in case that a provided variable uses a concrete unit, this unit has to be processed.
        // otherwise, nothing happens
        checkNotNull(var);
        if (var.getType() == TypeSymbol.Type.UNIT) {
            Unit temp = new Unit(var);
            this.addDimension(temp.getDimension());
            this.addUnit(temp);
            return Optional.of(temp);
        }
        return Optional.empty();
    }

    /**
     * This sub-routine handles the processing of a unit, thus converts it to an adequate internal representation.
     *
     * @param var The variable which will processed, here the type is stored as an ASTDatatype object.
     */
    private Optional<Unit> handleType(ASTDatatype var) {
        checkNotNull(var);
        if (var.getUnitType().isPresent()) {
            Unit temp = new Unit(var.getUnitType().get());
            this.addDimension(temp.getDimension());
            this.addUnit(temp);
            return Optional.of(temp);
        }
        return Optional.empty();
    }

    /**
     * A pre-processing function.
     * Collects all boolean variables located in the model for further computations.
     */
    private void collectBooleanElements(ASTBody neuronBody) {
        for (VariableSymbol var : neuronBody.getStateAliasSymbols()) {
            if (var.getType().getName().equals("boolean")) {
                booleanElements.add(var.getName());
            }
        }
        for (VariableSymbol var : neuronBody.getStateNonAliasSymbols()) {
            if (var.getType().getName().equals("boolean")) {
                booleanElements.add(var.getName());
            }
        }
        for (VariableSymbol var : neuronBody.getParameterAliasSymbols()) {
            if (var.getType().getName().equals("boolean")) {
                booleanElements.add(var.getName());
            }
        }
        for (VariableSymbol var : neuronBody.getParameterNonAliasSymbols()) {
            if (var.getType().getName().equals("boolean")) {
                booleanElements.add(var.getName());
            }
        }
        for (VariableSymbol var : neuronBody.getInternalAliasSymbols()) {
            if (var.getType().getName().equals("boolean")) {
                booleanElements.add(var.getName());
            }
        }
        for (VariableSymbol var : neuronBody.getInternalNonAliasSymbols()) {
            if (var.getType().getName().equals("boolean")) {
                booleanElements.add(var.getName());
            }
        }

    }

    public List<String> getBooleanElements() {
        return this.booleanElements;
    }

    @SuppressWarnings("unused")//Used in the template
    public String getNeuronName() {
        return this.neuronName.replace("_nestml", "");
    }

    @SuppressWarnings("unused")//Used in the template
    public String getExtendedModel() {
        return this.extendedModel.get();
    }

    @SuppressWarnings("unused")//Used in the template
    public boolean getModelIsExtension() {
        return this.extendedModel.isPresent();
    }

    @SuppressWarnings("unused")//Used in the template
    public boolean getDynamicElementsArePresent() {
        return this.routine != null;
    }

    @SuppressWarnings("unused")//Used in the template
    public DynamicRoutine getAutomaton() {
        return this.routine;
    }

    @SuppressWarnings("unused")//Used in the template
    public List<ConditionalBlock> getConditionalBlocks() {
        return this.getAutomaton().getConditionalBlocks();
    }

    @SuppressWarnings("unused")//Used in the template
    public boolean conditionsPresent() {
        return (this.routine != null) && (this.routine.getConditionalBlocks().size() > 0);
    }

    @SuppressWarnings("unused")//Used in the template
    public List<EventPort> getPortsList() {
        return portsList;
    }

    @SuppressWarnings("unused")//Used in the template
    public Set<Unit> getUnitsSet() {
        return unitsSet;
    }

    @SuppressWarnings("unused")//Used in the template
    public Set<Dimension> getDimensionsSet() {
        return dimensionsSet;
    }

    @SuppressWarnings("unused")//Used in the template
    public List<Constant> getConstantsList() {
        return constantsList;
    }

    @SuppressWarnings("unused")//Used in the template
    public List<DerivedElement> getDerivedParametersList() {
        ArrayList<DerivedElement> temp = new ArrayList<>();
        for (DerivedElement elem : derivedElementList) {
            if (!elem.isDynamic()) {
                temp.add(elem);
            }
        }
        return temp;
    }

    @SuppressWarnings("unused")//Used in the template
    public List<StateVariable> getStateVariablesList() {
        return stateVariablesList;
    }

    @SuppressWarnings("unused")//Used in the template
    public List<DerivedElement> getDerivedVariablesList() {
        ArrayList<DerivedElement> temp = new ArrayList<>();
        for (DerivedElement elem : derivedElementList) {
            if (elem.isDynamic()) {
                temp.add(elem);
            }
        }
        return temp;
    }

    @SuppressWarnings("unused")//used in the template
    public List<String> getNotConvertedElements() {
        return this.notConverted;
    }

    public List<String> getLocalTimeDerivative() {
        return this.localTimeDerivative;
    }

    /**
     * Returns the sole output-port of the model
     *
     * @return The output-port.
     */
    @SuppressWarnings("unused")//used in the template
    public EventPort getOutputPort() {
        for (EventPort port : this.getPortsList()) {
            if (port.getDirection() == EventPort.Direction.out) {
                return port;
            }
        }
        System.err.print("No output buffer defined!");
        return null;
    }

    /**
     * Returns the sole output-port of the model
     *
     * @return The output-port.
     */
    @SuppressWarnings("unused")//used in the template
    public List<String> getInputPorts() {
        List<String> temp = new ArrayList<>();
        for (EventPort port : this.getPortsList()) {
            if (port.getDirection() == EventPort.Direction.in) {
                temp.add(port.getName());
            }
        }
        return temp;
    }

    public SimulationConfiguration getConfig() {
        return this.config;
    }

    public Map<Expression, String> getGuards() {
        return guards;
    }

    /**
     * Checks whether an output-port is defined.
     *
     * @return True, if output is present.
     */
    @SuppressWarnings("unused")//used in the template
    public boolean outputPortDefined() {
        for (EventPort port : this.getPortsList()) {
            if (port.getDirection() == EventPort.Direction.out) {
                return true;
            }
        }
        System.err.print("No output buffer defined!");
        return false;
    }

    @SuppressWarnings("unused")//used in the template
    public Map<String, Expression> getEquations() {
        return equation;
    }

    @SuppressWarnings("unused")//used in the template
    public LEMSExpressionsPrettyPrinter getPrettyPrint() {
        return prettyPrint;
    }

    @SuppressWarnings("unused")//used in the template
    public List<DerivedElement> getDerivedElementList() {
        return derivedElementList;
    }

    public LEMSExpressionsPrettyPrinter getLEMSExpressionsPrettyPrinter() {
        return this.prettyPrint;
    }

    @SuppressWarnings("unused")//used in the template
    public List<Attachment> getAttachments() {
        return this.attachments;
    }

    public LEMSSyntaxContainer getSyntaxContainer() {
        return this.syntax;
    }

    /**
     * A list of functions which add elements to the corresponding lists.
     */
    public void addUnit(Unit var) {
        checkNotNull(var);
        if (!this.unitsSet.contains(var)) {
            this.unitsSet.add(var);
        }
    }

    public void addDimension(Dimension var) {
        checkNotNull(var);
        if (!this.dimensionsSet.contains(var)) {
            this.dimensionsSet.add(var);
        }
    }

    public void addConstant(Constant var) {
        checkNotNull(var);
        if (!this.constantsList.contains(var)) {
            this.constantsList.add(var);
        }
    }

    public void addStateVariable(StateVariable var) {
        checkNotNull(var);
        if (!this.stateVariablesList.contains(var)) {
            this.stateVariablesList.add(var);
        }
    }

    public void addEventPort(EventPort var) {
        checkNotNull(var);
        if (!this.portsList.contains(var)) {
            this.portsList.add(var);
        }
    }

    public void addNotConverted(String elem) {
        checkNotNull(elem);
        if (!this.notConverted.contains(elem)) {
            this.notConverted.add(elem);
        }
    }

    public void addDerivedElement(DerivedElement var) {
        checkNotNull(var);
        if (!this.derivedElementList.contains(var)) {
            this.derivedElementList.add(var);
        }
    }

    public void addAttachment(Attachment var) {
        checkNotNull(var);
        if (!this.attachments.contains(var)) {
            this.attachments.add(var);
        }
    }

    public void addBooleanElement(String element) {
        checkNotNull(element);
        this.booleanElements.add(element);
    }

    public void addLocalTimeDerivative(String var) {
        checkNotNull(var);
        this.localTimeDerivative.add(var);
    }

    public void addEquation(String var, Expression expr) {
        checkNotNull(var);
        checkNotNull(expr);
        this.equation.put(var, expr);
    }


    public void addGuard(String guardVar, Expression guardCond) {
        checkNotNull(guardVar);
        checkNotNull(guardCond);
        this.guards.put(guardCond, guardVar);
    }

    /**
     * Activates a port for the LEMS simulator, for more details read git hub issue.
     */
    private void addPortActivator() {
        if (outputPortDefined() && !HelperCollection.containsNamedFunction("emit_spike", routine.getAllInstructions())) {
            routine.addPortActivator();
        }
    }

    @SuppressWarnings("unused")//used in the template
    public String printGuardName(Expression expr) {
        if (this.getGuards().containsKey(expr)) {
            return this.getGuards().get(expr);
        }
        throw new NullPointerException();//this case should never happen
    }


}