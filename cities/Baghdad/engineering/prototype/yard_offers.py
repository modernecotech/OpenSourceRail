"""Compare casting capacity offers for a specified quantity of accepted 10 m box beams."""
import argparse
from dataclasses import asdict, dataclass, replace
from fractions import Fraction
from hashlib import sha256
from heapq import heapreplace
import json
from math import ceil
from pathlib import Path
import tomllib

from cities.Baghdad.engineering.prototype import factory
from cities.Baghdad.engineering.simulation import production

SHOP = Path(__file__).parent / "infrastructure/civil-resources.toml"
POLICY = tomllib.loads(SHOP.read_text())
RESOURCES = {r["id"]: r for r in POLICY["resource"]}
MOULD = RESOURCES["civil-beam-position"]
POUR = RESOURCES["civil-pour-crew"]


@dataclass(frozen=True)
class Offer:
    name: str
    moulds: int
    cycle_hours: float
    crews: int
    shifts: int
    shift_hours: float
    availability: float
    yield_rate: float
    pour_hours: float
    quote_usd: float | None = None


def reference_offer():
    quantities = {"beam_count": 0}
    # The issued workcell's daily target sets its planning counts; offers can
    # change each of those resource assumptions independently.
    return Offer("Issued workcell example", factory.daily_capacity(MOULD, POLICY, quantities)["required_units"],
                 MOULD["load"][0]["hours"], factory.daily_capacity(POUR, POLICY, quantities)["required_units"],
                 1, POLICY["hours_per_day"], POLICY["utilisation"], 1., POUR["load"][0]["hours"])


def evaluate(offer, beams, deadline_days=None):
    if not isinstance(offer.name, str) or not offer.name.strip():
        raise ValueError("Include an offer name")
    if type(beams) is not int or beams <= 0:
        raise ValueError("Accepted beams must be a positive whole count")
    for key in ("moulds", "crews", "shifts"):
        if type(getattr(offer, key)) is not int or getattr(offer, key) < 0:
            raise ValueError(f"{key} must be a nonnegative whole count")
    cycle, shift_hours, pour = (factory.number(getattr(offer, key)) for key in ("cycle_hours", "shift_hours", "pour_hours"))
    availability, yield_rate = (factory.number(getattr(offer, key), zero=True) for key in ("availability", "yield_rate"))
    if availability > 1 or yield_rate > 1 or offer.shifts*shift_hours > 24 or cycle < pour:
        raise ValueError("Use fractions from 0 to 1, at most 24 staffed hours/day and a cycle at least as long as the pour")
    if offer.quote_usd is not None:
        factory.number(offer.quote_usd, zero=True)
    if deadline_days is not None:
        factory.number(deadline_days)
    result = dict(offer=asdict(offer), accepted_target=beams, deadline_days=deadline_days,
                  price_status="offered" if offer.quote_usd is not None else "quote requested",
                  capital_or_service_total_usd=offer.quote_usd,
                  attempted_castings=None, finish_days=None, meets_deadline=None, schedule=None)
    if not (offer.moulds and offer.crews and offer.shifts and yield_rate and availability):
        result.update(status="no output with offered capacity", meets_deadline=False if deadline_days is not None else None)
        return result
    attempts = ceil(beams/yield_rate)
    staffed_window = shift_hours*availability
    if pour > staffed_window:
        result.update(status="no uninterrupted pour slot in offered shift",
                      meets_deadline=False if deadline_days is not None else None)
        return result
    # The whole production dispatcher has resource bookings but no daily
    # shift openings. Release jobs into it at the earliest staffed pour slot.
    crews_free = [Fraction(0)]*min(offer.crews, attempts)
    moulds_free = [Fraction(0)]*min(offer.moulds, attempts)
    jobs = []
    for i in range(attempts):
        earliest = max(crews_free[0], moulds_free[0])
        day, hour = divmod(earliest, 24)
        shift, offset = divmod(hour, shift_hours)
        if offset+pour > staffed_window:
            shift += 1
            offset = 0
        if shift >= offer.shifts:
            day, shift, offset = day+1, 0, 0
        start = day*24 + shift*shift_hours + offset
        heapreplace(crews_free, start+pour)
        heapreplace(moulds_free, start+cycle)
        accepted = (i+1)*yield_rate // 1 > i*yield_rate // 1
        jobs.append((float(start/24), [production.Step("pour", float(pour/24), {"crew": 1}, hold=("mould",)),
                         production.Step("release and inspect", float((cycle-pour)/24), {}, unhold=("mould",),
                                         complete=("accepted" if accepted else "rejected", 1))]))
    schedule = production.schedule(jobs, {"crew": offer.crews, "mould": offer.moulds}, 0, {})
    # Sum rational planning inputs; suppress floating event accumulation at a deadline boundary.
    finish = round(schedule["last_completion_workday"], 9)
    result.update(status="scheduled", attempted_castings=attempts, finish_days=finish, schedule=schedule,
                  meets_deadline=finish <= deadline_days if deadline_days is not None else None)
    return result


def report(offers, beams, deadline_days):
    paths = (SHOP, Path(__file__), Path(production.__file__), Path(factory.__file__))
    bundle = dict(article_physical_id=POLICY["source"]["civil_article_physical_id"],
                  scope="10 m box casting and release with shared pour crews and independently occupied moulds",
                  source_sha256={p.name: sha256(p.read_bytes()).hexdigest() for p in paths},
                  comparisons=[evaluate(offer, beams, deadline_days) for offer in offers])
    bundle["evaluation_id"] = sha256(json.dumps(bundle, sort_keys=True, allow_nan=False).encode()).hexdigest()
    return bundle


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    example = reference_offer()
    parser.add_argument("--beams", type=int, required=True, help="accepted castings required")
    parser.add_argument("--deadline-days", type=float, help="effective production days available")
    for field in ("moulds", "cycle_hours", "crews", "shifts", "shift_hours", "availability", "yield_rate", "pour_hours", "quote_usd"):
        parser.add_argument("--"+field.replace("_", "-"), type=int if field in ("moulds", "crews", "shifts") else float,
                            default=getattr(example, field))
    parser.add_argument("--name", default="Entered workcell")
    parser.add_argument("--offer", action="append", type=Path, default=[], help="additional complete supplier offer JSON")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        entered = replace(example, **{key: getattr(args, key) for key in asdict(example)})
        offers = [entered] + [Offer(**json.loads(path.read_text())) for path in args.offer]
        bundle = report(offers, args.beams, args.deadline_days)
    except (ValueError, TypeError, OSError) as error:
        parser.error(str(error))
    if args.json:
        print(json.dumps(bundle, indent=2, allow_nan=False))
        return
    print("Workcell | Accepted target | Attempts | Finish (effective days) | Meets deadline | Offer (USD)")
    for row in bundle["comparisons"]:
        finish = row["finish_days"]
        deadline = row["meets_deadline"]
        price = row["capital_or_service_total_usd"]
        print(" | ".join(map(str, (row["offer"]["name"], row["accepted_target"], row["attempted_castings"] or "—",
                                  f"{finish:.2f}" if finish is not None else row["status"],
                                  "—" if deadline is None else ("yes" if deadline else "no"),
                                  row["price_status"] if price is None else f"{price:,.2f}"))))
    print("Casting and release only. Pours occupy uninterrupted staffed slots. Curing continues off shift. Strength tests remain open.")


if __name__ == "__main__":
    main()
