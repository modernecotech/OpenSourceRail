#!/usr/bin/env python3
"""Losslessly compact the three historical research snapshots into shared CAS.

Original seals and every byte remain reconstructable. Historical verification
checks integrity, never current design applicability or engineering acceptance.
"""

from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from engineering.generative_design import (
    evidence_store,
    review,
    queue_campaign,
    architecture_campaign,
)

PACKETS = ("generative-campaign", "queued-systems", "architecture-feedback")


def size(folder):
    return (
        sum(p.stat().st_size for p in folder.rglob("*") if p.is_file())
        if folder.exists()
        else 0
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("migrate", "repack", "verify", "prune"))
    parser.add_argument("--delete-unreferenced", action="store_true")
    args = parser.parse_args()
    if args.action == "prune":
        print(
            json.dumps(
                evidence_store.collect_unreferenced(delete=args.delete_unreferenced),
                indent=2,
                sort_keys=True,
            )
        )
        return
    if args.delete_unreferenced:
        parser.error("--delete-unreferenced requires prune")
    records = []
    for name in PACKETS:
        folder = ROOT / "docs/design-engine" / name
        before = size(folder)
        if args.action in {"migrate", "repack"}:
            result = evidence_store.migrate(folder, reencode=args.action == "repack")
        else:
            result = evidence_store.verify_projection(folder)
        if name == "generative-campaign":
            historical = review.verify_snapshot(folder, current=False)
        elif name == "queued-systems":
            historical = queue_campaign.verify(folder, current=False, snapshot=True)
        else:
            historical = architecture_campaign.verify(
                folder, current=False, snapshot=True
            )
        records.append(
            dict(
                folder=name,
                bytes_before=before,
                bytes_after=size(folder),
                storage=result,
                original_seal_historical_verification=historical,
            )
        )
    print(
        json.dumps(
            dict(
                schema="osr-evidence-migration/1",
                packets=records,
                shared_store_bytes=size(evidence_store.STORE),
                physical_release=False,
            ),
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
