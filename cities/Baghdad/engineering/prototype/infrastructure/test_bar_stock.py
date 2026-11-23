from collections import Counter
import json
from zipfile import ZipFile

import pytest

from cities.Baghdad.engineering.prototype.infrastructure import bar_stock


def test_each_mark_and_each_millimetre_accounted_for_in_both_orders():
    with ZipFile(bar_stock.PACKET) as packet:
        raw = packet.read("civil-article.json")
    civil = json.loads(raw)
    cases = json.loads(bar_stock.artifacts(raw)["infrastructure/stock-cases.json"])["cases"]
    assert [c["stock_bars_per_beam"] for c in cases] == [103, 88]
    for case in cases:
        marks = Counter()
        for pattern in case["patterns"]:
            cuts = pattern["cuts"]
            marks.update({m: n * pattern["stock_bars_per_beam"] for m, n in Counter(c["mark"] for c in cuts).items()})
            assert pattern["offcut_mm"] + sum(c["blank_mm"] + 3 for c in cuts) + 20 == case["stock_mm"]
        assert marks == {r["mark"]: r["pieces"] for r in civil["bar_schedule_one_beam"]}
        assert case["purchased_mm_per_beam"] == sum(case[k] for k in
                ("blanks_mm_per_beam", "process_loss_mm_per_beam", "offcut_mm_per_beam"))
    with pytest.raises(ValueError, match="unspliced"):
        bar_stock.plan(civil, 9800, 0, 0)
