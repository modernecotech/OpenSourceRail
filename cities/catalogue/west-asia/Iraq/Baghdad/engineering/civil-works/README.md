# Baghdad detailed civil works plan

**Proposed planning methods; construction and complete opening remain unreleased.**

[Master plan](../../../../../../../docs/civil/civil-works-master-plan.md) connects detailed viaduct, station, other works, logistics, programme and inspection methods.

The 25 m average sizing basis reconciles to 10,128 identified catalogue bays, 422 unresolved specials/closures and 24.58 m actual running-span average. Orders retain span/track IDs and actual products.

| Line | At grade km | Elevated km | Bridge km | Catalogue bays | Special spans | Stations |
|---|---:|---:|---:|---:|---:|---:|
| line-1 | 23.195 | 21.223 | 4.650 | 700 | 29 | 21 |
| line-2 | 18.479 | 28.786 | 5.586 | 868 | 81 | 23 |
| line-3 | 23.386 | 24.989 | 1.121 | 770 | 21 | 23 |
| line-4 | 13.457 | 26.874 | 1.601 | 857 | 45 | 17 |
| line-5 | 20.636 | 24.249 | 2.460 | 737 | 30 | 24 |
| line-6 | 25.180 | 24.500 | 2.823 | 748 | 48 | 22 |
| line-7 | 13.529 | 24.273 | 2.155 | 767 | 22 | 17 |
| line-8 | 17.427 | 24.763 | 5.947 | 746 | 44 | 20 |
| line-9 | 26.182 | 66.964 | 4.539 | 2090 | 68 | 42 |
| line-10 | 0.000 | 6.499 | 0.000 | 191 | 4 | 5 |
| line-11 | 0.000 | 8.163 | 0.000 | 258 | 4 | 5 |
| line-12 | 0.000 | 8.590 | 0.000 | 240 | 6 | 7 |
| line-13 | 0.368 | 7.002 | 0.000 | 215 | 6 | 6 |
| line-14 | 0.000 | 8.294 | 0.000 | 262 | 4 | 5 |
| line-15 | 0.000 | 6.633 | 0.000 | 196 | 4 | 5 |
| line-16 | 0.000 | 6.146 | 0.000 | 211 | 2 | 3 |
| line-17 | 0.000 | 8.838 | 0.000 | 272 | 4 | 6 |

[Line quantities](line-quantities.json) separate running structures from elevated station/transition scope. [Run register](workfront-register.csv) retains the identified disconnected access/launcher boundary packages. [Station packages](station-work-packages.csv) retain individual layouts and equipment; [civil segments](civil-segments.csv) retain every class/chainage.

[Resources and logistics](resource-and-logistics.json) calculates required production positions, accepted/gross supply, concrete, cargo, complete transport cycles, vehicles, 10–15-bay buffers and six-day calendar lower bounds. These are illustrative requirements, not available supplier/route capacity or a completion forecast.

[Package dependencies](package-dependencies.json) connects fourteen civil scopes per line to complete opening interfaces. Unprovided durations, installed prices and accepted dates stay unknown. Fleet, systems qualification, testing and authority approvals remain additional requirements.

[Review register](review-register.json) preserves open support/structure, capacity, buffer, station/special, stabling, quantity, calendar and cost findings. [References](technical-references.json) are international method-development guidance; local adoption and actual site evidence are required.

Run `python tools/automation/civil-works-plan.py`; `--check` verifies deterministic bytes and source locks on a clean checkout. [Manifest](manifest.json) records content provenance independent of the containing commit.
