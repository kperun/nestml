package org.nest.commons._visitor;

import org.nest.commons._ast.ASTExpr;
import org.nest.spl.symboltable.typechecking.Either;
import org.nest.symboltable.symbols.TypeSymbol;
import org.nest.utils.AstUtils;

import static org.nest.spl.symboltable.typechecking.TypeChecker.isBoolean;
import static org.nest.symboltable.predefined.PredefinedTypes.getBooleanType;
import static org.nest.symboltable.predefined.PredefinedTypes.getIntegerType;
import static org.nest.symboltable.predefined.PredefinedTypes.getRealType;

/**
 * @author ptraeder
 */
public class ComparisonOperatorVisitor implements CommonsVisitor{

  @Override
  public void visit(ASTExpr expr) {
    final Either<TypeSymbol, String> lhsType = expr.getLeft().get().getType();
    final Either<TypeSymbol, String> rhsType = expr.getRight().get().getType();

    if (lhsType.isError()) {
      expr.setType(lhsType);
      return;
    }
    if (rhsType.isError()) {
      expr.setType(rhsType);
      return;
    }

    if (
        ((lhsType.getValue().equals(getRealType()) || lhsType.getValue().equals(getIntegerType())) &&
        (rhsType.getValue().equals(getRealType()) || rhsType.getValue().equals(getIntegerType())))
            ||
        (lhsType.getValue().getName().equals(rhsType.getValue().getName()))
            ||
        isBoolean(lhsType.getValue()) && isBoolean(rhsType.getValue())) {
      expr.setType(Either.value(getBooleanType()));
      return;
    }

    //Error message for any other operation
    final String errorMsg = "\""+AstUtils.toString(expr)+"\" - Only numeric types can be compared, SI types must match exactly.";
    expr.setType(Either.error(errorMsg));
  }

}
