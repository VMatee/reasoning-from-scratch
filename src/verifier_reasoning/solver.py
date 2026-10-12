"""Game-24 search with exact fractions and a separate solution checker.

This is symbolic reasoning, not a claim about language-model chain-of-thought.
"""
from dataclasses import dataclass
from fractions import Fraction
from typing import Sequence


@dataclass(frozen=True)
class Step:
    left: Fraction
    operator: str
    right: Fraction
    result: Fraction

    def __str__(self) -> str:
        return f"{self.left} {self.operator} {self.right} = {self.result}"


@dataclass(frozen=True)
class Solution:
    expression: str
    steps: tuple[Step, ...]
    explored_states: int


@dataclass(frozen=True)
class _Node:
    value: Fraction
    expr: str


def _apply(a: Fraction, op: str, b: Fraction) -> Fraction:
    if op == "+":
        return a + b
    if op == "-":
        return a - b
    if op == "*":
        return a * b
    if op == "/" and b != 0:
        return a / b
    raise ValueError("Invalid operation or division by zero")


def _candidates(a: _Node, b: _Node):
    for left, op, right in [
        (a, "+", b), (a, "*", b),
        (a, "-", b), (b, "-", a),
        (a, "/", b), (b, "/", a),
    ]:
        if op == "/" and right.value == 0:
            continue
        value = _apply(left.value, op, right.value)
        yield _Node(value, f"({left.expr} {op} {right.expr})"), Step(left.value, op, right.value, value)


def solve(numbers: Sequence[int], target: int = 24, max_states: int = 100000) -> Solution | None:
    """Try to combine every supplied number once with + - * / to reach target.

    Returns the first exact solution, or None if not found within max_states.
    None therefore need not prove mathematical unsatisfiability if budget exhausted.
    """
    if len(numbers) < 1 or max_states < 1:
        raise ValueError("Provide numbers and a positive max_states")
    nodes = [_Node(Fraction(n), str(n)) for n in numbers]
    desired = Fraction(target)
    visited: set[tuple[Fraction, ...]] = set()
    explored = 0

    def search(current: list[_Node], steps: tuple[Step, ...]):
        nonlocal explored
        state = tuple(sorted(node.value for node in current))
        if state in visited or explored >= max_states:
            return None
        visited.add(state)
        explored += 1
        if len(current) == 1:
            if current[0].value == desired:
                return Solution(current[0].expr, steps, explored)
            return None
        for i in range(len(current)):
            for j in range(i + 1, len(current)):
                rest = [node for k, node in enumerate(current) if k not in (i, j)]
                for merged, step in _candidates(current[i], current[j]):
                    result = search(rest + [merged], steps + (step,))
                    if result is not None:
                        return result
        return None

    return search(nodes, ())


def verify_steps(numbers: Sequence[int], steps: Sequence[Step], target: int = 24) -> bool:
    """Independently verify each arithmetic step against the available multiset.

    An expression string is display-only and is not trusted by this checker.
    """
    values = [Fraction(n) for n in numbers]
    if not values or len(steps) != len(values) - 1:
        return False
    for step in steps:
        try:
            i = values.index(step.left)
            values.pop(i)
            j = values.index(step.right)
            values.pop(j)
            actual = _apply(step.left, step.operator, step.right)
            if actual != step.result:
                return False
            values.append(actual)
        except (ValueError, ZeroDivisionError):
            return False
    return len(values) == 1 and values[0] == Fraction(target)
