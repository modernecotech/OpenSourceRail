"""Priceable stock-bar cutting patterns for the prototype cage, by individual beam kit."""

import argparse
from collections import Counter
import csv
from decimal import Decimal, ROUND_CEILING
from hashlib import sha256
from io import StringIO
import json
from pathlib import Path
from zipfile import ZipFile


HERE = Path(__file__).resolve().parent
PACKET = HERE.parent / "airport-prototype.zip"


def plan(civil, stock_mm, cut_loss_mm, end_trim_mm):
    if any(type(n) is not int or n < 0 for n in (cut_loss_mm, end_trim_mm, stock_mm)):
        raise ValueError("Use whole, nonnegative millimetres")
    usable = stock_mm - end_trim_mm
    bars = []
    seen = set()
    for row in civil["bar_schedule_one_beam"]:
        mark = row["mark"]
        pieces = row["pieces"]
        if mark in seen or type(pieces) is not int or pieces <= 0:
            raise ValueError(f"Invalid or repeated cage mark {mark}")
        seen.add(mark)
        # Round up for the stock estimate only. The drawing controls finished shape.
        blank = int((Decimal(str(row["developed_length_m"])) * 1000).to_integral_value(rounding=ROUND_CEILING))
        diameter = row["diameter_mm"]
        if blank <= 0 or blank + cut_loss_mm > usable or diameter <= 0:
            raise ValueError(f"Stock cannot furnish the unspliced {mark} blank")
        bars.extend([(blank, diameter, mark)] * pieces)
    stocks = []
    for length, diameter, mark in sorted(bars, reverse=True):
        needed = length + cut_loss_mm
        # First-fit decreasing per beam. Do not carry remainders into the next kit.
        for stock in stocks:
            if stock["diameter_mm"] == diameter and stock["offcut_mm"] >= needed:
                break
        else:
            stock = dict(diameter_mm=diameter, offcut_mm=usable, marks=[])
            stocks.append(stock)
        stock["offcut_mm"] -= needed
        stock["marks"].append((mark, length))
    patterns = Counter((s["diameter_mm"], tuple(s["marks"]), s["offcut_mm"]) for s in stocks)
    total = len(stocks) * stock_mm
    blank_total = sum(length for length, _, _ in bars)
    loss = len(stocks) * end_trim_mm + len(bars) * cut_loss_mm
    offcut = sum(s["offcut_mm"] for s in stocks)
    if blank_total + loss + offcut != total:
        raise ValueError("Stock length does not balance")
    count = civil["quantities"]["repeat_beams"]
    inputs = dict(civil_evaluation_id=civil["evaluation_id"], method="one-beam-first-fit-decreasing-v1",
                  stock_mm=stock_mm, cut_loss_mm=cut_loss_mm, end_trim_mm=end_trim_mm)
    scenario_id = sha256(json.dumps(inputs, sort_keys=True).encode()).hexdigest()
    return dict(scenario_id=scenario_id, stock_mm=stock_mm, end_trim_mm_per_stock=end_trim_mm, cut_loss_mm_per_blank=cut_loss_mm,
                candidate_id=civil["candidate_id"], civil_evaluation_id=civil["evaluation_id"],
                repeat_beams=count, stock_bars_per_beam=len(stocks), stock_bars_for_repeat=count * len(stocks),
                purchased_mm_per_beam=total, blanks_mm_per_beam=blank_total, process_loss_mm_per_beam=loss,
                offcut_mm_per_beam=offcut, blanks_per_beam=len(bars), yard_price_per_stock_bar=None,
                estimated_stock_utilisation=blank_total / total,
                fabrication_released=False,
                patterns=[dict(pattern_id=f"P{i:02}", diameter_mm=d, stock_bars_per_beam=n,
                               cuts=[dict(mark=m, blank_mm=l) for m, l in cuts], offcut_mm=rest)
                          for i, ((d, cuts, rest), n) in enumerate(patterns.items(), 1)])


def artifacts(raw):
    civil = json.loads(raw)
    cases = [plan(civil, length, 3, 20) for length in (12000, 14000)]
    record = dict(source_member="civil-article.json", source_sha256=sha256(raw).hexdigest(),
                  basis="One beam per kit; common reinforcement specification for bars of equal diameter subject to supplier confirmation.",
                  strand_bed_extra_stock_m=civil["strand"]["long_line_bed_extra_stock_m"],
                  embedded_strand_m_per_beam=civil["strand"]["embedded_strand_stock_m"], cases=cases)
    tags = StringIO(newline="")
    writer = csv.writer(tags, lineterminator="\n")
    writer.writerow(["candidate_id", "civil_evaluation_id", "scenario_id", "diameter_mm", "cut_loss_mm", "end_trim_mm", "beam_serial", "material_grade", "mill_heat", "certificate_ref",
                     "stock_mm", "pattern", "stock_bars_per_beam", "sequence", "bar_mark", "blank_mm",
                     "stock_offcut_mm_after_pattern", "operator", "inspection_record"])
    for case in cases:
        for p in case["patterns"]:
            for seq, cut in enumerate(p["cuts"], 1):
                writer.writerow([case["candidate_id"], case["civil_evaluation_id"], case["scenario_id"], p["diameter_mm"],
                                 case["cut_loss_mm_per_blank"], case["end_trim_mm_per_stock"], "", "", "", "", case["stock_mm"], p["pattern_id"],
                                 p["stock_bars_per_beam"], seq, cut["mark"], cut["blank_mm"], p["offcut_mm"], "", ""])
    return {"infrastructure/stock-cases.json": (json.dumps(record, indent=2) + "\n").encode(),
            "infrastructure/bar-cut-tags.csv": tags.getvalue().encode()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stock-mm", type=int, default=12000)
    parser.add_argument("--end-trim-mm", type=int, default=20, help="combined end allowance on each stock bar")
    parser.add_argument("--cut-loss-mm", type=int, default=3)
    args = parser.parse_args()
    with ZipFile(PACKET) as packet:
        raw = packet.read("civil-article.json")
        manifest = json.loads(packet.read("manifest.json"))
    if sha256(raw).hexdigest() != manifest["sha256"]["civil-article.json"]:
        parser.error("Civil schedule digest differs from prototype issue")
    try:
        result = plan(json.loads(raw), args.stock_mm, args.cut_loss_mm, args.end_trim_mm)
    except ValueError as error:
        parser.error(str(error))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
