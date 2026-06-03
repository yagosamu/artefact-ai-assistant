"""Safe arithmetic evaluator.

Using ast instead of eval() - eval() runs arbitrary code, so if the LLM
ever passes something like "__import__('os').system(...)" we'd be done.
This parses the expression into a syntax tree and walks it, only allowing
number literals and basic arithmetic ops. Anything else raises.
"""

import ast
import operator
from typing import Union
from langchain_core.tools import tool

Number = Union[int, float]

_BIN_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}

_UNARY_OPS = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}


def _eval(node: ast.AST) -> Number:
    if isinstance(node, ast.Constant):
        # bool is a subclass of int in Python — skip it so True/False
        # don't sneak through as numbers.
        if isinstance(node.value, bool) or not isinstance(node.value, (int, float)):
            raise ValueError(f"Unsupported constant: {node.value!r}")
        return node.value

    if isinstance(node, ast.BinOp):
        op = _BIN_OPS.get(type(node.op))
        if op is None:
            raise ValueError(f"Unsupported operator: {type(node.op).__name__}")
        return op(_eval(node.left), _eval(node.right))

    if isinstance(node, ast.UnaryOp):
        op = _UNARY_OPS.get(type(node.op))
        if op is None:
            raise ValueError(f"Unsupported operator: {type(node.op).__name__}")
        return op(_eval(node.operand))

    raise ValueError(f"Unsupported expression: {type(node).__name__}")


def safe_calculate(expression: str) -> Number:
    """Evaluate an arithmetic expression. Supports + - * / // % ** and parens."""
    tree = ast.parse(expression, mode="eval")
    return _eval(tree.body)


@tool
def calculator(expression: str) -> str:
    """Evaluate a math expression and return the result.

    Use this whenever the user asks for a numerical computation -
    arithmetic, percentages, math involving units, etc. Don't use
    for general knowledge questions.

    Args:
        expression: Math expression as a string. Supports + - * / // % **
            and parentheses. Examples: "128 * 46", "(1+2)**3", "1500 * 1.07".
    """
    try:
        return str(safe_calculate(expression))
    except ZeroDivisionError:
        return "Error: division by zero"
    except (ValueError, SyntaxError) as e:
        return f"Error: invalid expression — {e}"