package org.nest.commons._visitor;

import org.nest.commons._ast.ASTExpr;
import org.nest.spl.symboltable.typechecking.Either;
import org.nest.symboltable.symbols.TypeSymbol;
import org.nest.utils.AstUtils;

import static com.google.common.base.Preconditions.checkState;
import static org.nest.spl.symboltable.typechecking.TypeChecker.isCompatible;
import static org.nest.symboltable.predefined.PredefinedTypes.getBooleanType;

/**
 *  @author ptraeder
 * */
public class ConditionVisitor implements CommonsVisitor{

  @Override
  public void visit(ASTExpr expr) {
    if (expr.getCondition().isPresent()) {
      final Either<TypeSymbol, String> condition = expr.getCondition().get().getType();
      final Either<TypeSymbol, String> ifTrue = expr.getIfTrue().get().getType();
      final Either<TypeSymbol, String> ifNot = expr.getIfNot().get().getType();

      if (condition.isError()) {
        expr.setType(condition);
        return;
      }
      if (ifTrue.isError()) {
        expr.setType(ifTrue);
        return;
      }
      if (ifNot.isError()) {
        expr.setType(ifNot);
        return;
      }

      if (!condition.getValue().equals(getBooleanType())) {
        expr.setType(Either.error("\""+AstUtils.toString(expr)+"\" - The ternary operator condition must be boolean."));
        return;
      }
      if (!isCompatible(ifTrue.getValue(), ifNot.getValue())) {
        expr.setType(Either.error("\""+AstUtils.toString(expr)+"\" - The ternary operator results must be of the same type. " + ifTrue.getValue().prettyPrint() + " and " + ifNot.getValue().prettyPrint()+" are incompatible"));
        return;
      }
      expr.setType(ifTrue);
      return;
    }
  }
}
