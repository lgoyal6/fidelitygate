#!/usr/bin/env python3
"""Generate or verify committed EnvMutationBench artifacts."""

from __future__ import annotations

import argparse
from pathlib import Path

from fidelitygate.benchmark import write_benchmark


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Fail if committed outputs are stale")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    write_benchmark(root, check=args.check)
    print("Benchmark artifacts are current." if args.check else "Benchmark artifacts generated.")


if __name__ == "__main__":
    main()
