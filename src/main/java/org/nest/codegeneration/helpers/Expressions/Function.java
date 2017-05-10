package org.nest.codegeneration.helpers.Expressions;

import java.util.ArrayList;
import java.util.List;

import org.nest.commons._ast.ASTExpr;
import org.nest.commons._ast.ASTFunctionCall;

/**
 * This class is used to store function calls of an expression.
 *
 * @author perun
 */
public class Function extends Expression {
	private String functionName;
	private List<Expression> arguments;

	public Function(ASTFunctionCall expr) {
		functionName = expr.getName().toString();
		arguments = new ArrayList<>();
		for (ASTExpr arg : expr.getArgs()) {
			Expression temp = new Expression(arg);
			arguments.add(temp);
		}
	}

	public Function(String functionName, List<Expression> args) {
		this.functionName = functionName;
		this.arguments = args;
	}

	public String getFunctionName() {
		return functionName;
	}

	public List<Expression> getArguments() {
		return arguments;
	}

	/**
	 * The print method as utilized in the template to print the function.
	 *
	 * @param container determines which syntax shall be used.
	 * @return a string representation of the function call
	 */
	public String print(SyntaxContainer container) {
		return container.print(this);
	}

	public int hashCode() {
		int ret = this.functionName.hashCode();
		for (Expression exp : arguments) {
			ret = ret + exp.hashCode();
		}
		return ret;
	}

	public boolean equals(Object obj) {
		return obj.getClass().equals(this.getClass()) &&
				((Function) obj).getFunctionName().equals(this.functionName) &&
				this.arguments.equals(((Function) obj).getArguments());
	}

	/**
	 * This is a deepClone method which generates a clone of this object whenever required, e.g. when it has to be
	 * mirrored to other parts of the expression tree.
	 * @return a deep clone of this
	 */
	public Function deepClone(){
		List<Expression> args = new ArrayList<>();
		for(Expression arg:arguments){
			args.add(arg.deepClone());
		}
		Function temp = new Function(String.valueOf(this.functionName),args);
		return temp;
	}
}