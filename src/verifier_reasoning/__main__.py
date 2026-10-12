"""Solve and validate small arithmetic puzzles with exact rational arithmetic."""
import argparse
import json
from .solver import solve, verify_steps
from .dp import solve_dp
from .certificate import make_certificate


def main():
    parser = argparse.ArgumentParser(description="Find and verify an exact arithmetic solution")
    parser.add_argument("numbers", type=int, nargs="*", default=[3, 3, 8, 8])
    parser.add_argument("--target", type=int, default=24)
    parser.add_argument("--method", choices=("dfs", "dp"), default="dfs")
    parser.add_argument("--max-states", type=int, default=100000)
    parser.add_argument("--json", action="store_true", help="emit a machine-verifiable JSON certificate")
    args = parser.parse_args()
    if args.max_states < 1:
        parser.error("max-states must be positive")
    result = (
        solve_dp(args.numbers, target=args.target, max_candidates=args.max_states)
        if args.method == "dp"
        else solve(args.numbers, target=args.target, max_states=args.max_states)
    )
    if result is None:
        print("No solution found (possibly limited by search budget).")
        return
    if args.json:
        print(json.dumps(make_certificate(args.numbers, result, args.target), indent=2))
    else:
        print("Expression:", result.expression)
        for number, step in enumerate(result.steps, start=1):
            print(f"  {number}. {step}")
        print("Verified:", verify_steps(args.numbers, result.steps, args.target))
        print("Explored candidates / states:", result.explored_states)


if __name__ == "__main__":
    main()
