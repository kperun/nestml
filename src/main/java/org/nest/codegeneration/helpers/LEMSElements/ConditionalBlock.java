package org.nest.codegeneration.helpers.LEMSElements;

import java.util.ArrayList;
import java.util.List;

import org.nest.codegeneration.helpers.Expressions.Expression;
import org.nest.codegeneration.helpers.Expressions.LEMSSyntaxContainer;

/**
 * This class stores a block which will be evoked during the simulation on a certain mCondition. A condtional block is
 * a part of the dynamic routine.
 *
 * @author perun
 */
public class ConditionalBlock extends LEMSElement {
	//a conditional block consists of mInstructions
	private List<DynamicRoutine.Instruction> mInstructions;
	private Expression mCondition;

	/**
	 * A constructor which generates a new block storing several instructions.
	 * @param _instructions a set of instructions
	 * @param _condition the condition of the block
	 * @param _comment a comment or the raw source code printed next to the block
	 */
	public ConditionalBlock(List<DynamicRoutine.Instruction> _instructions, Expression _condition, String _comment) {
		this.mInstructions = _instructions;
		this.mCondition = _condition;
		super.setComment(_comment);
	}
    /**
     * A constructor which generates a new block storing a single instruction.
     * @param _instruction a set of instructions
     * @param _condition the condition of the block
     * @param _comment a comment or the raw source code printed next to the block
     */
	public ConditionalBlock(DynamicRoutine.Instruction _instruction,Expression _condition, String _comment){
		this.mInstructions = new ArrayList<>();
		this.mInstructions.add(_instruction);
		this.mCondition = _condition;
		super.setComment(_comment);
	}

	@SuppressWarnings("unused")//used in the template
	public Expression getCondition() {
		return this.mCondition;
	}

	@SuppressWarnings("unused")//used in the template
	public String printCondition() {
		return mCondition.print(new LEMSSyntaxContainer());
	}

	@SuppressWarnings("unused")//used in the template
	public List<DynamicRoutine.Instruction> getInstructions() {
		return this.mInstructions;
	}

	@SuppressWarnings("unused")//used in the template
	public String getInstructionType(DynamicRoutine.Instruction _instruction) {
		return _instruction.getClassIdentifier();
	}

}