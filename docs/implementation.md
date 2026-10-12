# Verifiable reasoning: two search algorithms implemented from scratch

This project is an exact arithmetic solver, not a language model. Python fractions avoid floating-point roundoff and enable mechanical verification.

## Algorithm A: depth-first search and canonicalization

src/verifier_reasoning/solver.py enumerates binary arithmetic operations on pairs of currently available values. It removes those values and inserts their result, recursively exploring until one remains. Canonical multiset states are memoized to reduce duplicate work.

## Algorithm B: subset dynamic programming

src/verifier_reasoning/dp.py represents each subset of input *indices* as a bitmask. The table stores reachable exact Fraction values and a witness expression for each subset. For each non-singleton subset, enumerate unordered partitions into nonempty left/right masks; then apply addition, multiplication, both subtraction directions and valid division directions.

Bitmasks distinguish repeated values at different input positions. The DP solver limits inputs to eight numbers and has a candidate budget, so failure at the budget is inconclusive.

## Independent proof certificate

src/verifier_reasoning/certificate.py stores every arithmetic operation as Fraction numerator/denominator text in JSON. verify_certificate reconstructs the numeric steps and uses verify_steps to check that each operation consumes two currently available values, produces the claimed exact value, and leaves the requested target. The human-readable expression string is for display and is not itself trusted.

## Run

~~~bash
python -m pip install -e ".[dev]"
python -m pytest -q
python -m verifier_reasoning 3 3 8 8 --target 24 --method dfs
python -m verifier_reasoning 3 3 8 8 --target 24 --method dp
python -m verifier_reasoning 3 3 8 8 --target 24 --method dp --json
~~~

The two methods can emit different valid expressions and do not have identical computational complexity. Tests verify exact answers and certificates rather than claiming equal runtimes.
