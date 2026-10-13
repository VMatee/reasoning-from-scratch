# Reasoning from Scratch — Search + Verifier

This repository implements **verifiable symbolic arithmetic reasoning** with two independent search algorithms. It constructs complete expressions from the supplied numbers, records each operation using exact rational arithmetic, and verifies the solution independently of the search method.

**This is not an LLM.** It demonstrates two general concepts useful for reasoning systems: **proposing candidate solutions** and **verifying their intermediate steps**. It does not perform language-model fine-tuning, chain-of-thought distillation, or natural-language reasoning.

## Run

```bash
python -m pip install -e '.[dev]'
python -m pytest -q
python -m verifier_reasoning 3 3 8 8 --target 24
python -m verifier_reasoning 3 3 8 8 --target 24 --method dp --json
```

Example output describes an expression, individual arithmetic steps, `Verified: True`, and the count of explored states. Output trace is computed dynamically; there are no hard-coded solutions.

## Mathematical formulation

Given numbers $a_1,\ldots,a_n$ and a target $T$, the objective is to construct an arithmetic expression using each input occurrence once. The two solvers explore equivalent reachable results in different ways, and every reported solution must satisfy:

```math
\mathrm{verify}(a_1,\ldots,a_n,\text{steps},T)=\mathrm{True}.
```

The full walkthrough derives the DFS state transition and subset-DP recurrence, proves the worked $[3,3,8,8]\mapsto24$ example using exact fractions, and explains which parts of a JSON certificate are actually checked.

**[Read the mathematical and verification walkthrough →](docs/mathematics.md)**

## Two independent solvers and verifiable certificates

The project includes **DFS with state memoization** and an independent
**subset dynamic-programming solver** built from scratch with Python bitmasks
and exact rational arithmetic. Both produce stepwise solutions, while JSON
certificates can be independently verified for arithmetic correctness.

Read the [implementation and proof-certificate walkthrough](docs/implementation.md).

## Algorithm

- Represent each number as an exact fraction with an expression string.
- Select a pair of remaining numbers and try `+`, `-`, `*`, `/` in valid orientations.
- Recurse on the reduced multiset and memoize states.
- Verify that every step uses two currently available values and produces the stated result.
- Reject division by zero and fabricated arithmetic.

The `max_states` budget bounds search. An absent solution when a budget is exhausted does **not** prove impossibility.

## Future ML extensions

Connect a small policy network to prioritize branches, train a verifier from labeled incorrect steps, or compare symbolic search to token-based generation. Measure accuracy over held-out puzzles and report search budgets, not just anecdotes.

## Reproducible notebook

Open [the step-by-step notebook](notebooks/01_walkthrough.ipynb) in Jupyter after installing this repository with `python -m pip install -e ".[dev]"`.

## Architecture walk-through

See [the implementation map](docs/architecture.md) for a component-by-component overview.

## Related educational reading

Sebastian Raschka maintains a useful [independent educational reference](https://github.com/rasbt/reasoning-from-scratch). This repository uses its own small code examples and does not reproduce his book content.
