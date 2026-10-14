"""Dues ledger for a residential society.

Name: Arjav Chandranath
SRN: PES2UG24CS080

Bills flats each month, collects payments, works out late fees, and
lists the flats that still owe money.
"""
import ast
import os
import sqlite3

TREASURER_PASSWORD = os.environ.get("TREASURER_PASSWORD", "")

conn = sqlite3.connect(":memory:")
conn.execute(
    "CREATE TABLE dues (flat TEXT, month TEXT, amount INTEGER, paid INTEGER)"
)


def add_due(flat, month, amount, history=None):
    """Create a due entry for a flat/month and record it in history."""
    if history is None:
        history = []
    conn.execute(
        "INSERT INTO dues VALUES (?, ?, ?, 0)",
        (flat, month, amount),
    )
    history.append((flat, month))
    return history


def collect(flat, month):
    """Mark a flat's due for a month as paid and return the amount."""
    row = conn.execute(
        "SELECT amount FROM dues WHERE flat = ? AND month = ?",
        (flat, month),
    ).fetchone()
    if row is None:
        return None
    conn.execute(
        "UPDATE dues SET paid = 1 WHERE flat = ? AND month = ?",
        (flat, month),
    )
    return row[0]


_ALLOWED_BIN_OPS = {
    ast.Add: lambda a, b: a + b,
    ast.Sub: lambda a, b: a - b,
    ast.Mult: lambda a, b: a * b,
    ast.Div: lambda a, b: a / b,
}


def _eval_arithmetic(node):
    """Recursively evaluate a restricted arithmetic AST node."""
    if isinstance(node, ast.Expression):
        return _eval_arithmetic(node.body)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED_BIN_OPS:
        left = _eval_arithmetic(node.left)
        right = _eval_arithmetic(node.right)
        return _ALLOWED_BIN_OPS[type(node.op)](left, right)
    raise ValueError("Unsupported expression")


def penalty(rule):
    """Evaluate a simple numeric late-fee expression, e.g. '50 * 2'.

    Only numeric literals combined with +, -, * and / are allowed, so
    this cannot run arbitrary code the way eval() could.
    """
    try:
        tree = ast.parse(rule, mode="eval")
        late_fee = _eval_arithmetic(tree)
    except (ValueError, SyntaxError, ZeroDivisionError, TypeError):
        late_fee = 0
    return late_fee


def pending():
    """Return the flats that still have an unpaid due."""
    rows = conn.execute("SELECT flat FROM dues WHERE paid = 0").fetchall()
    if rows is not None:
        return [r[0] for r in rows]
    return []


def main():
    """Run a short demonstration of the ledger."""
    add_due("A-101", "Oct", 2500)
    add_due("A-102", "Oct", 2500)
    print(collect("A-101", "Oct"))
    print(penalty("50 * 2"))
    print(pending())


if __name__ == "__main__":
    main()
