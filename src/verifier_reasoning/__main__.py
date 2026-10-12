import argparse
from .solver import solve, verify_steps


def main():
    parser = argparse.ArgumentParser(description="Find and verify a short exact arithmetic reasoning trace")
    parser.add_argument("numbers", type=int, nargs="*", default=[3, 3, 8, 8])
    parser.add_argument("--target", type=int, default=24)
    args = parser.parse_args()
    result = solve(args.numbers, target=args.target)
    if result is None:
        print("No solution found (possibly limited by search budget).")
        return
    print("Expression:", result.expression)
    for number, step in enumerate(result.steps, start=1):
        print(f"  {number}. {step}")
    print("Verified:", verify_steps(args.numbers, result.steps, args.target))
    print("Explored states:", result.explored_states)


if __name__ == "__main__":
    main()
