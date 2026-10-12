# Architecture note — Verifiable arithmetic search

```text
numbers -> pairwise exact Fraction operations -> state pruning -> target comparison -> independent trace verifier
```

## Fidelity and assumptions

This is symbolic search and verification, not a trained reasoning LLM.

Read the source implementation and the tests together. New features should
add controlled experiments or unit tests before using benchmark claims.
