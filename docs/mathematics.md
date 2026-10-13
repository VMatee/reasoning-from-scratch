# Exact arithmetic reasoning: search, dynamic programming and verification

*Two independent algorithms for constructing arithmetic expressions, with proof-like traces that can be checked without trusting the solver.*

A reasoning system should be judged not only by whether it proposes an answer, but also by whether its intermediate steps are valid. This repository makes that distinction concrete with Game-24-style arithmetic puzzles. Given several integers and a target, it builds expressions using each supplied number once, then independently checks every operation.

There is no language model behind this implementation. The interesting algorithms are ordinary but powerful: recursive search, state deduplication, subset dynamic programming, exact rational arithmetic and an independent certificate verifier.

## 1. Define the mathematical problem

Let the supplied values be a multiset

```math
X=\{a_1,a_2,\ldots,a_n\},
```

and let the requested result be an integer target $T$. We want an expression constructed from the numbers in $X$ using each input occurrence **exactly once**, and using binary operations

```math
\mathcal{O}=\{+,-,\times,\div\}
```

subject to the condition that no division uses a zero denominator.

An expression is a binary tree. Its leaves are the supplied numbers, and each internal node applies one permitted operation to the values of its two children. With $n$ leaves, a complete expression has exactly $n-1$ internal operations.

### A worked solution, checked by hand

Consider the input $[3,3,8,8]$ with target $24$. One valid expression is

```math
8\div\left(3-\frac{8}{3}\right)=24.
```

To verify this without relying on a floating-point approximation, write the intermediate values as exact fractions:

```math
8\div 3=\frac{8}{3},
```

```math
3-\frac{8}{3}=\frac{9}{3}-\frac{8}{3}=\frac{1}{3},
```

```math
8\div\frac{1}{3}=8\times3=24.
```

Notice that the two 3s and two 8s are **different input occurrences**, even though their numerical values match. The sequence consumes each occurrence once. The program may discover another equally valid expression; these steps are one human-readable example, not a hard-coded solver output.

## 2. Represent numbers as exact rational values

Many implementations make a subtle mistake by using ordinary floating-point equality to decide whether an expression reaches the target. An expression involving thirds, for example, cannot always be represented exactly in binary floating point.

Python's standard-library **Fraction** represents a rational value as

```math
q=\frac{p}{r},
\qquad p,r\in\mathbb{Z},\quad r\neq0,
```

with normalization performed automatically. Arithmetic then uses exact numerator/denominator relationships:

```math
\frac{a}{b}+\frac{c}{d}=\frac{ad+bc}{bd},
\qquad
\frac{a}{b}\times\frac{c}{d}=\frac{ac}{bd}.
```

The [original solver](../src/verifier_reasoning/solver.py) and the [DP solver](../src/verifier_reasoning/dp.py) both use exact Fractions. The checker can therefore compare final results using exact equality, rather than a hand-chosen floating-point tolerance.

## 3. Solver A: recursive search with memoized states

The depth-first solver begins with one node per supplied number. Each node stores an exact value and a printable expression.

At a search state containing $m$ nodes, it picks a pair, applies every valid operation (including both orientations of subtraction and division), and places the resulting node into the remaining $m-2$ nodes. The next state therefore has $m-1$ nodes.

Conceptually, the transition is

```math
S'=(S\setminus\{x,y\})\cup\{x\circ y\},
\qquad \circ\in\mathcal{O},
```

where the subtraction and division cases must consider both operand orders.

The search succeeds only when one node remains and its exact value equals $T$.

### Why memoization matters

Different sequences of arithmetic operations can lead to the same multiset of remaining values. If we revisit that same numerical state, searching it again cannot reveal different *reachable final values* within this operation set. The implementation uses a sorted tuple of Fractions as a canonical key:

```math
\mathrm{key}(S)
=\mathrm{sort}\bigl(\mathrm{value}(x_1),\ldots,\mathrm{value}(x_m)\bigr).
```

Caching these keys reduces repeated exploration. The solver tracks the number of visited states and stops at a configurable budget. Importantly, returning **None** when that budget is exhausted means *no solution was found within the budget*, not *no mathematical solution exists*.

The implementation is in [solver.py](../src/verifier_reasoning/solver.py).

## 4. Solver B: subset dynamic programming

The [independent second implementation](../src/verifier_reasoning/dp.py) approaches the same problem in a different way. Instead of following one recursive path, it tabulates reachable values for every subset of **input positions**.

Represent a subset $S\subseteq\{0,\ldots,n-1\}$ by an integer bitmask. The $i$th bit is set exactly when input occurrence $a_i$ belongs to the subset. This is important because equal values at different positions still have different bits.

Let $\mathcal{R}(S)$ denote the set of values obtainable from exactly the numbers indexed by $S$. The base case is

```math
\mathcal{R}(\{i\})=\{a_i\}.
```

For any subset with at least two indices, enumerate every partition into two nonempty, disjoint subsets $A$ and $B$:

```math
A\cap B=\varnothing,\qquad A\cup B=S.
```

Combine reachable left and right values:

```math
\mathcal{R}(S)
=
\bigcup_{\substack{A\cup B=S\\A\cap B=\varnothing\\A,B\neq\varnothing}}
\left\{
x\circ y:
x\in\mathcal{R}(A),\
y\in\mathcal{R}(B),\
\circ\in\mathcal{O}
\right\},
```

with undefined divisions removed and both operand orders considered where relevant.

The table stores one witness expression for each distinct reachable Fraction value. Once the full-set entry contains the target, its witness can be returned as a solution.

The number of subsets is $2^n$, and possible partitions across all subsets grow on the order of $3^n$. Moreover, the number of distinct reachable rational values can grow rapidly. The implementation therefore limits inputs to eight numbers and stops when its candidate budget is exceeded. It should not be described as a polynomial-time solver.

## 5. Separate proposing an answer from checking it

A solver is an algorithm that *proposes* arithmetic steps. A verifier is a separate algorithm that *tests* whether those steps are legitimate.

The [verify_steps](../src/verifier_reasoning/solver.py) function maintains a multiset of currently available Fractions. For every submitted step $(\ell,\circ,r,z)$ it checks that:

1. Both the left and right operands are presently available as separate occurrences.
2. The specified operation is permitted and any denominator is nonzero.
3. Applying that operation gives the claimed exact result $z$.
4. The two operands are removed and their result is added back to the multiset.

After $n-1$ steps, exactly one value must remain and must equal the target. In logical notation, an accepted certificate satisfies

```math
\mathrm{verify}(X,\mathrm{steps},T)=\mathrm{True}
\quad\Longrightarrow\quad
\text{the recorded arithmetic operations transform }X\text{ into }T.
```

This implication is limited to the checker's explicit arithmetic rules. It does not prove that the supplied *expression string* has the same syntax as the step trace; in this project, expression strings are display text and **the verifier does not trust them**.

## 6. Portable JSON certificates

The [certificate module](../src/verifier_reasoning/certificate.py) serializes each intermediate value as an exact fraction string, such as **8/3**, plus its operands and operator. This makes it possible to transmit a proposed solution and verify it independently of the solving method.

The verifier reconstructs the Fractions and repeats the arithmetic checks. Replacing a legitimate step result with an invented value, changing the input numbers or inserting an unsupported operation causes the certificate check to fail.

A JSON certificate can carry additional metadata, such as an expression or explored-state count. Only the arithmetic step sequence and input/target fields are established by the current verifier; other metadata should not be mistaken for independently authenticated facts.

## 7. Evaluate behavior rather than claim "AI reasoning" accuracy

This repository contains tests for solvable puzzles, known unsolvable examples, invalid steps, division by zero, search budgets, duplicate numbers and JSON tampering. Two independent methods can return different expressions, provided that their verified results match.

For a collection of labeled puzzles, a simple solve rate would be

```math
\mathrm{SolveRate}
=\frac{1}{Q}\sum_{i=1}^{Q}
\mathbf{1}[\text{a valid target expression is found for puzzle }i].
```

That quantity must be accompanied by the puzzle distribution, search budgets and timeout policy. The existing small tests are regression checks; they are not a standardized reasoning benchmark and do not evaluate a generative language model.

### Run both algorithms

~~~bash
python -m pip install -e ".[dev]"
python -m pytest -q
python -m verifier_reasoning 3 3 8 8 --target 24 --method dfs
python -m verifier_reasoning 3 3 8 8 --target 24 --method dp
python -m verifier_reasoning 3 3 8 8 --target 24 --method dp --json
~~~

**Source crosswalk:** [recursive solver and independent arithmetic checker](../src/verifier_reasoning/solver.py) · [subset DP](../src/verifier_reasoning/dp.py) · [JSON certificate verifier](../src/verifier_reasoning/certificate.py) · [regression tests](../tests/test_dp_certificate.py).

**Interpretation.** The system implements exact symbolic search and mechanically checkable arithmetic traces. Its methods are relevant to verification in larger AI systems, but it is not an LLM, a chain-of-thought training method or evidence of general-purpose reasoning.
