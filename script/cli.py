#!/usr/bin/env python3
"""Unified CLI entrypoint for Day 10 Data Observability & RAG Evaluation Lab."""

import argparse
import sys
from pathlib import Path

# Add src directory to python import path
SRC_DIR = Path(__file__).resolve().parent.parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from pipelines.phase1 import main as run_phase1
from pipelines.corruption_flow import main as run_corruption


def main():
    parser = argparse.ArgumentParser(
        description="Day 10 Data Pipeline, Observability & RAG Evaluation CLI Tool"
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Command: run-phase1
    subparsers.add_parser("run-phase1", help="Execute Phase 1 Baseline Pipeline")

    # Command: run-corruption
    subparsers.add_parser("run-corruption", help="Execute Corruption & Recovery Flow")

    # Command: run-all
    subparsers.add_parser("run-all", help="Execute Phase 1 Baseline followed by Corruption Flow")

    args = parser.parse_args()

    if args.command == "run-phase1":
        run_phase1()
    elif args.command == "run-corruption":
        run_corruption()
    elif args.command == "run-all":
        print("=== Running Phase 1 Baseline Pipeline ===")
        run_phase1()
        print("\n=== Running Corruption & Recovery Flow ===")
        run_corruption()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
