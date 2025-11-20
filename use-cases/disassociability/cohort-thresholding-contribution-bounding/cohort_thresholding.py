#!/usr/bin/env python3
"""
Cohort thresholding and contribution bounding demo tool.

This small utility illustrates two common disassociability techniques:
  1. Contribution bounding: limiting how many times a single user can
     contribute to a cohort.
  2. Cohort thresholding: only reporting cohorts with at least k
     (bounded) contributions.

The tool is intended as a simple, readable reference implementation
rather than a production-ready system.
"""

import argparse
import csv
from collections import defaultdict
from dataclasses import dataclass
from typing import Iterable, Dict, List, Tuple


@dataclass
class Event:
    """Single event record."""
    user_id: str
    cohort_id: str
    value: float


def load_events(path: str) -> List(Event]:
    """Loads events from a CSV file with header.

    Expected columns: user_id, cohort_id, value
    """
    events: List(Event] = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            events.append(
                Event(
                    user_id=str(row["user_id"]),
                    cohort_id=str(row["cohort_id"]),
                    value=float(row["value"]),
                )
            )
    return events


def apply_contribution_bounding(
    events: Iterable[Event],
    max_contribution: int = 1,
) -> List[Event]:
    """Applies per-user, per-cohort contribution bounding.

    Each (user_id, cohort_id) pair is allowed to contribute to at most
    `max_contribution` events. Extra events from the same user to the
    same cohort are dropped.
    """
    counts: Dict[Tuple[str, str], int] = defaultdict(int)
    bounded: List[Event] = []

    for ev in events:
        key = (ev.user_id, ev.cohort_id)
        if counts[key] < max_contribution:
            counts[key] += 1
            bounded.append(ev)

    return bounded


def aggregate_with_threshold(
    events: Iterable[Event],
    k_threshold: int = 5,
) -> Dict[str, Dict[str, float]]:
    """Aggregates events by cohort with a k-anonymity-style threshold.

    Returns a mapping:
        cohort_id -> {"num_events": ..., "sum_value": ...}

    Only cohorts with at least `k_threshold` events are included.
    """
    cohort_values: Dict[str, List[float]] = defaultdict(list)

    for ev in events:
        cohort_values[ev.cohort_id].append(ev.value)

    result: Dict[str, Dict[str, float]] = {}
    for cohort_id, values in cohort_values.items():
        if len(values) >= k_threshold:
            result[cohort_id] = {
                "num_events": float(len(values)),
                "sum_value": float(sum(values)),
            }

    return result


def write_aggregates_to_csv(
    aggregates: Dict[str, Dict[str, float]],
    path: str,
) -> None:
    """Writes aggregated cohort metrics to CSV."""
    fieldnames = ["cohort_id", "num_events", "sum_value"]
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for cohort_id, metrics in sorted(aggregates.items()):
            row = {"cohort_id": cohort_id}
            row.update(metrics)
            writer.writerow(row)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Demo tool for cohort thresholding and contribution bounding. "
            "Input CSV must have columns: user_id, cohort_id, value."
        )
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to input events CSV file.",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Path to output aggregated CSV file.",
    )
    parser.add_argument(
        "--k-threshold",
        type=int,
        default=5,
        help="Minimum number of bounded events required to report a cohort.",
    )
    parser.add_argument(
        "--max-contribution",
        type=int,
        default=1,
        help="Maximum number of events per (user, cohort) pair.",
    )

    args = parser.parse_args()

    events = load_events(args.input)
    bounded = apply_contribution_bounding(
        events, max_contribution=args.max_contribution
    )
    aggregates = aggregate_with_threshold(
        bounded, k_threshold=args.k_threshold
    )
    write_aggregates_to_csv(aggregates, args.output)


if __name__ == "__main__":
    main()
