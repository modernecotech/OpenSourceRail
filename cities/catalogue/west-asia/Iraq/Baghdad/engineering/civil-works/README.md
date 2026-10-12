# Baghdad detailed civil works plan

**Proposed planning methods; construction and complete opening remain unreleased.**

[Master plan](../../../../../../../docs/civil/civil-works-master-plan.md) connects detailed viaduct, station, other works, logistics, programme and inspection methods.

The 25 m average sizing basis reconciles to 9,973 identified catalogue bays, 404 unresolved specials/closures and 24.64 m actual running-span average. Orders retain span/track IDs and actual products.

| Line | At grade km | Elevated km | Bridge km | Catalogue bays | Special spans | Stations |
|---|---:|---:|---:|---:|---:|---:|
| line-1 | 22.625 | 21.621 | 4.821 | 770 | 32 | 17 |
| line-2 | 18.284 | 28.987 | 5.579 | 988 | 76 | 14 |
| line-3 | 22.833 | 25.542 | 1.121 | 863 | 29 | 16 |
| line-4 | 13.480 | 26.810 | 1.641 | 943 | 44 | 12 |
| line-5 | 19.248 | 25.830 | 2.267 | 874 | 35 | 16 |
| line-6 | 24.426 | 25.388 | 2.689 | 846 | 60 | 16 |
| line-7 | 13.565 | 24.296 | 2.095 | 813 | 21 | 13 |
| line-8 | 18.200 | 23.633 | 6.303 | 811 | 39 | 15 |
| line-9 | 26.038 | 67.067 | 4.579 | 2280 | 61 | 26 |
| line-10 | 0.000 | 6.804 | 0.000 | 238 | 2 | 3 |
| line-11 | 2.828 | 4.057 | 0.000 | 153 | 1 | 2 |
| line-12 | 5.207 | 1.380 | 0.000 | 46 | 1 | 3 |
| line-13 | 4.299 | 3.743 | 0.000 | 123 | 2 | 4 |
| line-14 | 0.000 | 6.047 | 0.000 | 225 | 1 | 2 |

[Line quantities](line-quantities.json) separate running structures from elevated station/transition scope. [Run register](workfront-register.csv) retains the identified disconnected access/launcher boundary packages. [Station packages](station-work-packages.csv) retain individual layouts and equipment; [civil segments](civil-segments.csv) retain every class/chainage.

[Resources and logistics](resource-and-logistics.json) calculates required production positions, accepted/gross supply, concrete, cargo, complete transport cycles, vehicles, 10–15-bay buffers and six-day calendar lower bounds. These are illustrative requirements, not available supplier/route capacity or a completion forecast.

[Package dependencies](package-dependencies.json) connects fourteen civil scopes per line to complete opening interfaces. Unprovided durations, installed prices and accepted dates stay unknown. Fleet, systems qualification, testing and authority approvals remain additional requirements.

[Review register](review-register.json) preserves open support/structure, capacity, buffer, station/special, stabling, quantity, calendar and cost findings. [References](technical-references.json) are international method-development guidance; local adoption and actual site evidence are required.

Run `python tools/automation/civil-works-plan.py`; `--check` verifies deterministic bytes and source locks on a clean checkout. [Manifest](manifest.json) records content provenance independent of the containing commit.
