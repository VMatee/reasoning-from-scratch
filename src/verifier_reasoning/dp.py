"""Subset dynamic programming for Game-24-style exact arithmetic reasoning.

Independent of the existing DFS state-memoization strategy: every nonempty
subset of input positions stores one expression per reachable Fraction value.
"""
from dataclasses import dataclass
from fractions import Fraction
from typing import Sequence

from .solver import Solution, Step


@dataclass(frozen=True)
class _Expression:
    value: Fraction
    text: str
    steps: tuple[Step, ...]


def _combine(a: _Expression, b: _Expression):
    """Enumerate both orders for noncommutative operators."""
    actions = [(a, "+", b), (a, "*", b), (a, "-", b), (b, "-", a)]
    if b.value:
        actions.append((a, "/", b))
    if a.value:
        actions.append((b, "/", a))
    for left, operation, right in actions:
        if operation == "+":
            value = left.value + right.value
        elif operation == "*":
            value = left.value * right.value
        elif operation == "-":
            value = left.value - right.value
        else:
            value = left.value / right.value
        yield _Expression(
            value,
            f"({left.text} {operation} {right.text})",
            left.steps + right.steps + (Step(left.value, operation, right.value, value),),
        )


def solve_dp(numbers: Sequence[int], target: int = 24, max_candidates: int = 50000) -> Solution | None:
    """Find a complete exact expression using each given number exactly once.

    Dynamic programming uses input *indices* as bitmask states, preserving
    repeated numbers. A candidate budget bounds work; reaching the budget
    does not prove that the puzzle is mathematically impossible.
    """
    if not numbers or max_candidates < 1:
        raise ValueError("Provide numbers and positive max_candidates")
    if len(numbers) > 8:
        raise ValueError("Subset DP is limited to eight input numbers")
    if any(not isinstance(value, int) for value in numbers):
        raise TypeError("Numbers must be integers")
    full = (1 << len(numbers)) - 1
    table: dict[int, dict[Fraction, _Expression]] = {}
    attempts = 0
    for mask in range(1, full + 1):
        if mask.bit_count() == 1:
            position = mask.bit_length() - 1
            number = Fraction(numbers[position])
            table[mask] = {number: _Expression(number, str(numbers[position]), ())}
            continue
        matches: dict[Fraction, _Expression] = {}
        left_mask = (mask - 1) & mask
        while left_mask:
            right_mask = mask ^ left_mask
            if left_mask < right_mask:
                for left in table[left_mask].values():
                    for right in table[right_mask].values():
                        for candidate in _combine(left, right):
                            attempts += 1
                            if attempts > max_candidates:
                                return None
                            matches.setdefault(candidate.value, candidate)
            left_mask = (left_mask - 1) & mask
        table[mask] = matches
    found = table[full].get(Fraction(target))
    if found is None:
        return None
    return Solution(found.text, found.steps, attempts)
