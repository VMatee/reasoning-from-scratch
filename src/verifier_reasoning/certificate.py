"""Serialize and independently verify exact rational reasoning certificates."""
from fractions import Fraction
from typing import Any, Sequence

from .solver import Solution, Step, verify_steps


def make_certificate(numbers: Sequence[int], solution: Solution, target: int = 24) -> dict[str, Any]:
    """Capture a checkable trace. The expression text is not trusted."""
    if not verify_steps(numbers, solution.steps, target):
        raise ValueError("Cannot certify an invalid solution")
    return {
        "numbers": list(numbers), "target": target, "expression": solution.expression,
        "steps": [
            {
                "left": str(s.left), "operator": s.operator,
                "right": str(s.right), "result": str(s.result),
            }
            for s in solution.steps
        ],
        "explored_states": solution.explored_states,
        "verified": True,
    }


def verify_certificate(document: dict[str, Any]) -> bool:
    """Decode each Fraction and check every arithmetic step from scratch."""
    try:
        numbers = document["numbers"]
        target = document["target"]
        if (not isinstance(numbers, list) or any(type(n) is not int for n in numbers)
                or type(target) is not int or not isinstance(document["steps"], list)):
            return False
        steps = [
            Step(
                Fraction(row["left"]), row["operator"],
                Fraction(row["right"]), Fraction(row["result"])
            )
            for row in document["steps"]
        ]
        if any(step.operator not in ("+", "-", "*", "/") for step in steps):
            return False
        return verify_steps(numbers, steps, target)
    except (KeyError, ValueError, TypeError, ZeroDivisionError):
        return False
