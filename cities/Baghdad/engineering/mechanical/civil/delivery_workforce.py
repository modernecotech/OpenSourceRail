"""Export the current Baghdad construction crews to the Rust and Arrow workplan."""

import argparse
import json
from hashlib import sha256
from math import ceil
from pathlib import Path

from cities.Baghdad.engineering.mechanical.civil import network_delivery as delivery


ACTIVE = delivery.ROOT / "cities/Baghdad/metropolitan-network.json"


def plan(network="active"):
    source = ACTIVE if network == "active" else delivery.OUTPUT / "network-delivery.json"
    data = source.read_bytes()
    study = json.loads(data)
    for path, expected in study["source_sha256"].items():
        if sha256((delivery.ROOT / path).read_bytes()).hexdigest() != expected:
            raise ValueError(f"Regenerate the current Baghdad delivery study. Changed source: {path}")

    rows = []
    if network == "active":
        programme = study["civil"]
        network = study["planning_selection"]["candidate_id"]
        if programme["candidate_id"] != network:
            raise ValueError("The booked shifts and selected metropolitan layout differ")
        expected_hours = programme["workforce"]["paid_deck_and_casting_hours"]
    else:
        programme = study["networks"][network]
        expected_hours = programme["totals"]["paid_total_method_and_casting_hours"]
    for section in programme["orders"]:
        crews = [*section["crew_shifts"], *section["casting_shifts"]]
        for index, crew in enumerate(crews, 1):
            paid = crew["paid_hours"]
            if paid == 0:
                continue
            rates = [crew["cost_usd"][case] for case in delivery.CASES]
            rate = [round(cost * 100 / paid) for cost in rates] if None not in rates else None
            minutes = round(paid * 60)
            posts = crew["posts_per_front"]
            shift_minutes = delivery.erection.SHIFT_H * 60
            rows.append(dict(
                work_id=f"{section['section']}:{index}", phase=crew["phase"], role=crew["role"],
                shift=f"{section['section']} · {crew['shift']}", start_minute=crew["start_minute"],
                minutes_per_shift=shift_minutes, days=ceil(minutes / (posts * shift_minutes)),
                assigned_posts=posts, paid_minutes=minutes, required_minutes=minutes,
                utilisation_bps=10_000, rates_cents_per_hour=rate,
                rate_basis=crew["price_basis"], cost_account="Deck delivery and casting",
            ))
    expected_minutes = round(expected_hours * 60)
    if sum(row["paid_minutes"] for row in rows) != expected_minutes:
        raise ValueError("The workforce plan must conserve the construction study's paid hours")
    sources = {**study["source_sha256"], str(source.relative_to(delivery.ROOT)): sha256(data).hexdigest(),
               str(Path(__file__).resolve().relative_to(delivery.ROOT)): sha256(Path(__file__).read_bytes()).hexdigest()}
    return dict(
        schema="osr-workforce-plan/1",
        plan_id=f"{study.get('evaluation_id', programme.get('evaluation_id'))}:{network}:deck-crews",
        source_sha256=sources, rows=rows,
        scope=dict(network=network, label="20 m deck-fed construction and casting",
                   calendar_basis="Crew minutes across all fronts. The delivery report carries the gantry schedules.",
                   cost_basis="Launcher payroll is already included in civil prices. Road and casting payroll are embedded in supplier rates.",
                   scope_boundaries="The capacity sensitivity measures losses against booked crew minutes. Foundations, stations, and railway operations have distinct accounts."),
        gaps=[dict(phase="Civil works", work="Confirm crew coverage, access and productivity from contractor returns",
                   owner="Launcher, works and precast suppliers",
                   cost_basis="Return individual trade rates and identify which hours are embedded in operated equipment and ex-yard prices")],
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("network", nargs="?", choices=("active", *delivery.NETWORKS), default="active")
    args = parser.parse_args()
    print(json.dumps(plan(args.network), indent=2, sort_keys=True, allow_nan=False))


if __name__ == "__main__":
    main()
