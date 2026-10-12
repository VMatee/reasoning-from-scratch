"""Second independent solver and portable verifiable certificates."""
import json
import pytest
from verifier_reasoning import solve, verify_steps
from verifier_reasoning.dp import solve_dp
from verifier_reasoning.certificate import make_certificate, verify_certificate


@pytest.mark.parametrize("numbers,target", [
    ([3, 3, 8, 8], 24), ([2, 3], 5), ([4, 2, 2], 8), ([24], 24),
])
def test_dp_and_dfs_both_find_verified_solutions(numbers, target):
    for solver in (solve, solve_dp):
        result = solver(numbers, target)
        assert result is not None
        assert verify_steps(numbers, result.steps, target)
        assert len(result.steps) == len(numbers) - 1


def test_known_impossibility_and_budget():
    assert solve_dp([1, 1, 1, 1], 24) is None
    assert solve_dp([3, 3, 8, 8], 24, max_candidates=1) is None
    with pytest.raises(ValueError):
        solve_dp([1], max_candidates=0)
    with pytest.raises(ValueError):
        solve_dp([1] * 9)


def test_certificate_roundtrip_and_step_tampering():
    numbers = [3, 3, 8, 8]
    result = solve_dp(numbers)
    assert result is not None
    document = json.loads(json.dumps(make_certificate(numbers, result)))
    assert verify_certificate(document)
    document["steps"][0]["result"] = "99999"
    assert not verify_certificate(document)


def test_certificate_rejects_wrong_input_and_invalid_operator():
    result = solve([2, 3], target=5)
    certificate = make_certificate([2, 3], result, target=5)
    assert verify_certificate(certificate)
    certificate["numbers"] = [2, 4]
    assert not verify_certificate(certificate)
    certificate["steps"][0]["operator"] = "eval"
    assert not verify_certificate(certificate)
