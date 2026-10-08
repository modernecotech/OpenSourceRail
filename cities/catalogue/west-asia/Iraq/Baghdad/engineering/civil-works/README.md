# Baghdad detailed civil works plan

**Proposed planning methods; construction and complete opening remain unreleased.**

[Master plan](../../../../../../../docs/civil/civil-works-master-plan.md) connects detailed viaduct, station, other works, logistics, programme and inspection methods.

The 25 m average sizing basis reconciles to 8,501 identified catalogue bays, 375 unresolved specials/closures and 24.55 m actual running-span average. Orders retain span/track IDs and actual products.

| Line | At grade km | Elevated km | Bridge km | Catalogue bays | Special spans | Stations |
|---|---:|---:|---:|---:|---:|---:|
| line-1 | 23.195 | 21.223 | 4.650 | 726 | 28 | 20 |
| line-2 | 18.479 | 28.786 | 5.586 | 912 | 77 | 20 |
| line-3 | 23.386 | 24.989 | 1.121 | 794 | 20 | 20 |
| line-4 | 13.477 | 26.854 | 1.601 | 879 | 44 | 16 |
| line-5 | 20.636 | 24.249 | 2.460 | 774 | 27 | 20 |
| line-6 | 24.165 | 25.516 | 2.823 | 791 | 48 | 21 |
| line-7 | 13.529 | 24.273 | 2.155 | 777 | 22 | 16 |
| line-8 | 18.138 | 24.052 | 5.947 | 759 | 45 | 18 |
| line-9 | 28.406 | 64.779 | 4.539 | 2089 | 64 | 35 |

[Line quantities](line-quantities.json) separate running structures from elevated station/transition scope. [Run register](workfront-register.csv) retains 548 disconnected access/launcher boundary packages. [Station packages](station-work-packages.csv) retain individual layouts and equipment; [civil segments](civil-segments.csv) retain every class/chainage.

[Resources and logistics](resource-and-logistics.json) calculates required production positions, accepted/gross supply, concrete, cargo, complete transport cycles, vehicles, 10–15-bay buffers and six-day calendar lower bounds. These are illustrative requirements, not available supplier/route capacity or a completion forecast.

[Package dependencies](package-dependencies.json) connects fourteen civil scopes per line to complete opening interfaces. Unprovided durations, installed prices and accepted dates stay unknown. Fleet, systems qualification, testing and authority approvals remain additional requirements.

[Review register](review-register.json) preserves open support/structure, capacity, buffer, station/special, stabling, quantity, calendar and cost findings. [References](technical-references.json) are international method-development guidance; local adoption and actual site evidence are required.

Run `python tools/automation/civil-works-plan.py`; `--check` verifies deterministic bytes and source locks on a clean checkout. [Manifest](manifest.json) records content provenance independent of the containing commit.
