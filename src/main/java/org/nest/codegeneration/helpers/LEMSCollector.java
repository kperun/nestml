package org.nest.codegeneration.helpers;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Set;

import org.nest.codegeneration.helpers.LEMSElements.ConditionalBlock;
import org.nest.codegeneration.helpers.LEMSElements.Constant;
import org.nest.codegeneration.helpers.LEMSElements.DerivedElement;
import org.nest.codegeneration.helpers.LEMSElements.Dimension;
import org.nest.codegeneration.helpers.LEMSElements.DynamicRoutine;
import org.nest.codegeneration.helpers.LEMSElements.EventPort;
import org.nest.codegeneration.helpers.LEMSElements.HelperCollection;
import org.nest.codegeneration.helpers.LEMSElements.SimulationConfiguration;
import org.nest.codegeneration.helpers.LEMSElements.StateVariable;
import org.nest.codegeneration.helpers.LEMSElements.Unit;
import org.nest.nestml._ast.ASTBody;
import org.nest.nestml._ast.ASTFunction;
import org.nest.nestml._ast.ASTInputLine;
import org.nest.nestml._ast.ASTNeuron;
import org.nest.nestml._ast.ASTOutput;
import org.nest.ode._ast.ASTEquation;
import org.nest.spl.prettyprinter.LEMS.LEMSExpressionsPrettyPrinter;
import org.nest.symboltable.symbols.TypeSymbol;
import org.nest.symboltable.symbols.VariableSymbol;

/**
 * This class provides an infrastructure which generates an internal,processed representation of an input model, which
 * is further used in the template.
 * It further utilizes org.nest.spl.prettyprinter.LEMS.ExpressionPrettyPrinterCustom in order to convert
 * declarations and function-calls as well as instructions to a proper syntax used by LEMS.
 *
 * @author perun
 */
public class LEMSCollector {
  private String neuronName="";

  private String extendedModel;

  private LEMSExpressionsPrettyPrinter prettyPrint;//used in order to convert expressions to LEMS syntax

  private DynamicRoutine automaton;//An internal representation of the update-block.

  private Set<Unit> unitsSet = null;//Collects all units

  private Set<Dimension> dimensionsSet = null;//Collects all dimension

  private List<Constant> constantsList = null;//Collects all constants

  private List<DerivedElement> derivedElementList = null;//Collects all derived variables

  private List<StateVariable> stateVariablesList = null;//Collects all state variables

  private List<EventPort> portsList = null;//Collects all event-ports

  private List<String> notConverted = null;//List of not converted elements

  private Map<String, String> equation = null;//a map of variables and the corresponding equation

  private List<String> localTimeDerivative = null;//a list of time derivatives which are only invoked in certain steps

  private Map<String, String> attachments = null;//a list of attachments to the neuron

  private SimulationConfiguration config = null;// the configuration of the simulation

  public static HelperCollection helper = null;//a set of assisting functions

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
    this.attachments = new HashMap<>();
    this.config = config;
    this.helper = new HelperCollection(this);
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
    /*
     * checks whether the model extends an other model
     */
    if (neuron.getBase().isPresent()) {
      extendedModel = neuron.getBase().get();//store the name of the extended model
    }
    ASTBody neuronBody = neuron.getBody();
    /*
     * processes all non-alias elements of the state block
     */
    for (VariableSymbol var : neuronBody.getStateNonAliasSymbols()) {
      if (var.isVector()) {//arrays are not supported by LEMS
        System.err.println("Not supported array-declaration found \"" + var.getName() + "\".");
        this.addNotConverted("Not supported array-declaration found: " + var.getName()
            + " in lines " + var.getAstNode().get().get_SourcePositionStart() + " to " + var.getAstNode().get()
            .get_SourcePositionEnd() + ".");
      }
      else {
        //otherwise process the object to a state variable
        this.addStateVariable(new StateVariable(var, this));
        handleType(var.getType());//handle the type of the variable
      }
    }
    /*
     * processes all alias elements of the state block
     */
    for (VariableSymbol var : neuronBody.getStateAliasSymbols()) {
      this.addDerivedElement(new DerivedElement(var, this, true,false));
      handleType(var.getType());//handle the type
    }
    /*
     * user-defined functions are not supported by LEMS (yet)
     */
    for (ASTFunction func : neuronBody.getFunctions()) {
      //print an error message an store a corresponding message for the generation
      System.err.println("Not supported function-declaration found \"" + func.getName() + "\".");
      this.addNotConverted("Not supported function-declaration found: " + func.getName()
          + " in lines " + func.get_SourcePositionStart() + " to " + func.get_SourcePositionEnd() + ".");
    }
    /*
     * process the equations block
     */
    if (!neuronBody.getEquations().isEmpty()) {
      //create a new constant in order to achieve a correct dimension of the equation:
      this.addConstant(new Constant("CON1ms","DimensionOfms","1","ms",false));
      /*
       * process all sub-elements used in the actual ODE expression
       */
      //TODO:this whole block is currently not used<----
      for(int i=100;i<neuronBody.getEquations().size();i++){
        String temp = "";//required during the computation
        ASTEquation eq = neuronBody.getEquations().get(i);

        if (helper.containsFunctionCall(eq.getRhs(), true)) {
          //print a proper warning
          System.err
              .println("Not supported function call in expression found: " + prettyPrint.print(eq.getRhs(), false));
          temp ="not_supported:" + prettyPrint.print(eq.getRhs(), false);
          this.addNotConverted(
              "Not supported function call(s) found in differential equation of \"" + eq.getLhs().getName().toString()
                  + "\" in lines" + eq.get_SourcePositionStart() + " to " + eq.get_SourcePositionEnd() + ".");
          equation.put(eq.getLhs().toString(),temp);
        }
        else{
          temp = temp + prettyPrint.print(eq.getRhs(), false);
          //replace constants with references
          //store the differential equation and its variable
          equation.put(eq.getLhs().toString(),"(" +helper.replaceConstantsWithReferences(this, temp)+")/CON1ms");
        }
      }
      /*
       * process the defining differential equation
       */
      for(int i=0;i<neuronBody.getEquations().size();i++){
        ASTEquation eq = neuronBody.getEquations().get(i);
        String temp = "";//required during the computation
        if (helper.containsFunctionCall(eq.getRhs(), true)) {//check whether the equation contains a function call
          //print a proper warning
          System.err
              .println("Not supported function call in expression found: " + prettyPrint.print(eq.getRhs(), false));
          temp = temp + "not_supported:" + prettyPrint.print(eq.getRhs(), false);
          this.addNotConverted(
              "Not supported function call(s) found in differential equation of \"" + eq.getLhs().getName().toString()
                  + "\" in lines " + eq.get_SourcePositionStart() + " to " + eq.get_SourcePositionEnd() + ".");
          equation.put(eq.getLhs().toString(), temp);
        }
        else {
          temp = temp + prettyPrint.print(eq.getRhs(), false);//replace constants with references
          List<String> tempList = new ArrayList<>();
          tempList.add(eq.getLhs().toString());// a list is required, since method blockContains requires lists of args.
          //check if somewhere in the update block an integrate directive has been used, if so, the equation has to be local
          if (helper.blockContainsFunction("integrate", tempList, neuronBody.getDynamicsBlock().get().getBlock())) {
            //only ode, i.e. integrate directives have to be manipulated
            equation.put(eq.getLhs().toString(),
                "ACT" + eq.getLhs().toString() + "*(" + helper.replaceConstantsWithReferences(this, temp) + ")/CON1ms");
            //now generate the corresponding activator
            this.stateVariablesList.add(
                new StateVariable("ACT" + eq.getLhs().toString(), "none", "1", "", this));
            this.localTimeDerivative.add(eq.getLhs().toString());
          }
          else {
            //otherwise the integration is global, no further steps required
            equation.put(eq.getLhs().toString(),"("+helper.replaceConstantsWithReferences(this, temp)+ ")/CON1ms");
          }
        }
      }
    }
    /*
     * processes all non-aliases in the parameter block, namely the constants
     */
    for (VariableSymbol var : neuronBody.getParameterNonAliasSymbols()) {
      if (var.isVector()) {//arrays are not supported by LEMS
        //print error message
        System.err.println("Not supported array-declaration found \"" + var.getName() + "\".");
        this.addNotConverted("/parameter-block/" + var.getName()
            + " in lines " + var.getAstNode().get().get_SourcePositionStart() + " to " + var.getAstNode().get()
            .get_SourcePositionEnd() + " of type array.");
      }
      else {
        Constant temp;
        if (var.getDeclaringExpression().isPresent()) {
          //if a declaring value is present -> generate a constant
          temp = new Constant(var, false, false, this);
        }
        else {
          //otherwise generate a parameter
          temp = new Constant(var, false, true, this);
        }
        String varName = null;
        //now check if a state variable has been initialized with this value
        for (VariableSymbol tempVar : neuronBody.getStateNonAliasSymbols()) {
          if (tempVar.getDeclaringExpression().isPresent()
              &&var.getName().equals(this.prettyPrint.print(tempVar.getDeclaringExpression().get(), false))) {
            varName = tempVar.getName();
          }
        }
        //if a variable has been initialized with this value, reset its default value
        if (varName != null) {
          for (StateVariable stateVar : stateVariablesList) {
            if (stateVar.getName().equals(varName)) {
              stateVar.setDefaultValue(temp.getName());
            }
          }
        }
        //now, in order to avoid constants which are not used, delete them
        int tempIndex = -1;
        for (Constant v : constantsList) {//search for the index
          if (v.getName().equals("INIT"+varName)) {
            tempIndex = constantsList.indexOf(v);
          }
        }//delete the the element
        if (tempIndex != -1) {
          constantsList.remove(tempIndex);//remove the previously generated init value
        }
        //finally add the new constant
        this.addConstant(temp);
      }
      handleType(var.getType());
    }

    /*
     * processes all aliases in the parameter, namely the derived constants
     */
    for (VariableSymbol var : neuronBody.getParameterAliasSymbols()) {
      this.addDerivedElement(new DerivedElement(var, this, false,false));
      handleType(var.getType());
    }
    /*
     * processes all non-alias declarations of the internal block
     */
    for (VariableSymbol var : neuronBody.getInternalNonAliasSymbols()) {
      if (var.isVector()) {//lems does not support arrays
        //print an adequate message
        System.err.println("Not supported array-declaration found \"" + var.getName() + "\".");
        this.addNotConverted("/internal-block/" + var.getName()
            + " in lines " + var.getAstNode().get().get_SourcePositionStart() + " to "
            + var.getAstNode().get().get_SourcePositionEnd() + " of type array.");
      }
      else {//the declaration does not use arrays
        //is a right hand side present?
        if (var.getDeclaringExpression().isPresent()) {
          // the function "resolution()" is not required by lems
          if (var.getDeclaringExpression().get().functionCallIsPresent() &&
              var.getDeclaringExpression().get().getFunctionCall().get().getName().toString().equals("resolution")) {
            //store an adequate message
            this.addNotConverted("Function call \"resolution()\" in lines "
                + var.getAstNode().get().get_SourcePositionStart()
                + " to " + var.getAstNode().get().get_SourcePositionEnd()
                + " not required by LEMS.");
          }
          else if (var.getDeclaringExpression().get().functionCallIsPresent() &&
              var.getDeclaringExpression().get().getFunctionCall().get().getName().toString().equals("steps")) {
            //the steps function is a special case, here we have derive the value by hand
            this.addConstant(new Constant("CON" + config.getSimSteps() + "ms",
                "DimensionOfms", helper.getNumberFormatted(config.getSimSteps()), "ms", false));
            //search for the constant to which steps refer
            for (Constant v : this.getConstantsList()) {
              if (v.getName()
                  .equals(this.getHelper().getArgs(var.getDeclaringExpression().get().getFunctionCall().get()))) {
                //create a new derived parameter for this expression
                this.addDerivedElement(new DerivedElement(var.getName(), helper.typeToDimensionConverter(var.getType()),
                    v.getName() + "/CON" + config.getSimSteps() + "ms", false, false));
              }
            }

          }
          else {//not a resolution call -> thus a normal constant
            this.addConstant(new Constant(var,false,false, this));
            handleType(var.getType());
          }

        }
        else {//no right hand site -> its a variable
          this.addStateVariable(new StateVariable(var, this));
          handleType(var.getType());
        }

      }

    }
    /*
     * processes all alias declarations of the internal block
    */
    for (VariableSymbol var : neuronBody.getInternalAliasSymbols()) {
      this.addDerivedElement(new DerivedElement(var, this, false,false));
      handleType(var.getType());
    }
    /*
    * processes all input-buffers
    */
    for (ASTInputLine var : neuronBody.getInputLines()) {
      //if(!var.isCurrent()){//current sources are not actual event ports, but rather variables derived externally
        this.addEventPort(new EventPort(var));//spike ports are added normally
      //}//current buffers are treated as derived variables and therefore have to be added with an artifact
    }
    /*
     * processes all output-buffers
    */
    for (ASTOutput var : neuronBody.getOutputs()) {
      this.addEventPort(new EventPort(var));
    }
    /*
     * now adapt the settings according to the handed over artifact
     */
    for(Object set:config.getInstructions()){
      List<String> tempList = (List<String>)set;//in order to avoid casting each time
      if(tempList.get(0).equals(this.neuronName)){//check whether the settings apply to this model
        for(int i=1;i<tempList.size();i++){
          this.adaptElementFromString(tempList.get(i));
        }
      }
    }
    /*
     * check whether the modeled neuron contains a dynamic routine, and if so, generate a corresponding automaton
     */
    if (neuronBody.getDynamicsBlock().isPresent()) {
      automaton = new DynamicRoutine(neuronBody.getDynamics(), this);
    }
  }

  /**
   * This sub-routine handles the processing of a unit, thus converts it to an adequate internal representation.
   *
   * @param var The variable which will processed.
   */
  public void handleType(TypeSymbol var) {
    /**
     * in case that a provided variable uses a concrete unit, this unit has to be processed. otherwise, nothing happens
     */
    if (var.getType() == TypeSymbol.Type.UNIT) {
      Unit temp = new Unit(var);
      this.addDimension(temp.getDimension());
      addUnit(temp);
    }
  }

  @SuppressWarnings("unused")//Used in the template
  public String getNeuronName() {
    return this.neuronName;
  }

  @SuppressWarnings("unused")//Used in the template
  public String getExtendedModel() {
    return this.extendedModel;
  }

  @SuppressWarnings("unused")//Used in the template
  public boolean getModelIsExtension() {
    return this.extendedModel != null;
  }

  @SuppressWarnings("unused")//Used in the template
  public boolean getDynamicElementsArePresent() {
    return this.automaton != null;
  }

  @SuppressWarnings("unused")//Used in the template
  public DynamicRoutine getAutomaton() {
    return this.automaton;
  }

  @SuppressWarnings("unused")//Used in the template
  public List<ConditionalBlock> getConditionalBlocks() {
    return this.getAutomaton().getConditionalBlocks();
  }

  @SuppressWarnings("unused")//Used in the template
  public boolean conditionsPresent() {
    return (this.automaton != null) && (this.automaton.getConditionalBlocks().size() > 0);
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
  public Map<String, String> getEquations() {
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
  @SuppressWarnings("unused")//used in the template
  public List<String> getNotConverted() {
    return notConverted;
  }

  public LEMSExpressionsPrettyPrinter getLEMSExpressionsPrettyPrinter() {
    return this.prettyPrint;
  }

  @SuppressWarnings("unused")//used in the template
  public Map<String, String> getAttachments() {
    return this.attachments;
  }

  public HelperCollection getHelper() {
    return this.helper;
  }

  /**
   * A list of functions which add elements to the corresponding lists.
   */

  public void addUnit(Unit var) {
    if (!this.unitsSet.contains(var)) {
      this.unitsSet.add(var);
    }
  }

  public void addDimension(Dimension var) {
    if (!this.dimensionsSet.contains(var)) {
      this.dimensionsSet.add(var);
    }
  }

  public void addConstant(Constant var) {
    if (!this.constantsList.contains(var)) {
      this.constantsList.add(var);
    }
  }

  public void addStateVariable(StateVariable var) {
    if (!this.stateVariablesList.contains(var)) {
      this.stateVariablesList.add(var);
    }
  }

  public void addEventPort(EventPort var) {
    if (!this.portsList.contains(var)) {
      this.portsList.add(var);
    }
  }

  public void addNotConverted(String elem) {
    if (!this.notConverted.contains(elem)) {
      this.notConverted.add(elem);
    }
  }

  public void addDerivedElement(DerivedElement var) {
    if (!this.derivedElementList.contains(var)) {
      this.derivedElementList.add(var);
    }
  }

  public void addAttachment(String name, String type) {
    if (!this.attachments.containsKey(name)) {
      this.attachments.put(name, type);
    }
  }

  /**
   * This method is used to parse a handed over string representing a element which has to be added to the model.
   * @param elem The element as a string.
   */
  private void adaptElementFromString(String elem) {
    String segmentTemp[] = elem.split("=|\"|\\s|\\t");//split in order to get each parameter
    segmentTemp[0] = segmentTemp[0].replaceAll("<", "");//format a little
    segmentTemp = formatArray(segmentTemp);//delete empty entries
    try {
      if (segmentTemp[0].equals("Attachments")) {
        this.addAttachment(segmentTemp[getIndex(segmentTemp,"name")+1],segmentTemp[getIndex(segmentTemp,"type")+1]);
      }
      else if (segmentTemp[0].equals("DerivedVariable")) {
        this.addDerivedElement(new DerivedElement(
            segmentTemp[getIndex(segmentTemp,"name")+1],
            segmentTemp[getIndex(segmentTemp,"dimension")+1],
            segmentTemp[getIndex(segmentTemp,"select")+1],
            true,true));
      }
    }
    catch (Exception exp) {
      System.err.println("External artifact has wrong format and is therefore not included!");
    }
  }

  /**
   * Formats a handed over array and deletes all occurrences of empty entries.
   * This method is only used in "adaptElementFromString" in order to include an external artifact.
   * @ari       an array of string entries
   * @return    an array of string entries without empty entries
   */
  private String[] formatArray(String[] ari){
    int currentIndex = 0;
    int newArraySize = 0;
    for(String e:ari){
      if(!e.equals("")&&!e.equals("/>")){
        newArraySize++;
      }
    }
    String[] ret = new String[newArraySize];
    for(int i=0;i<ari.length;i++){
      if(!ari[i].equals("")&&!ari[i].equals("/>")){
        ret[currentIndex] = ari[i];
        currentIndex++;
      }
    }
    return ret;
  }

  /**
   * Returns the last index of a handed over element in a handed over array.
   * This method is only used in "adaptElementFromString" in order to include an external artifact.
   * @param ari The array of elements
   * @param elem the element whose index will be returned.
   * @return the index of the element
   */
  private int getIndex(String[] ari,String elem){
    int ret = -1;
    for(int i=0;i<ari.length;i++){
      if(ari[i].equals(elem)){
        ret = i;
      }
    }
    return ret;
  }

}