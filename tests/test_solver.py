from fractions import Fraction
from verifier_reasoning import Step, solve, verify_steps


def test_solves_nontrivial_game_24():
    values = [3, 3, 8, 8]
    result = solve(values)
    assert result is not None
    assert verify_steps(values, result.steps)
    assert result.explored_states > 0
    assert len(result.steps) == 3


def test_simple_problem_and_unsolvable():
    result = solve([2, 3], 5)
    assert result is not None and verify_steps([2, 3], result.steps, 5)
    assert solve([1, 1, 1, 1], target=24) is None


def test_checker_rejects_fabricated_step():
    invalid = Step(Fraction(2), "+", Fraction(3), Fraction(9))
    assert not verify_steps([2, 3], [invalid], target=9)
    assert not verify_steps([2, 3], [Step(Fraction(2), "/", Fraction(0), Fraction(0))], target=0)


def test_single_number_and_invalid_budget():
    assert verify_steps([24], [])
    assert solve([24]) is not None
    try:
        solve([1, 2], max_states=0)
    except ValueError:
        pass
    else:
        raise AssertionError("Expected validation of state budget")
