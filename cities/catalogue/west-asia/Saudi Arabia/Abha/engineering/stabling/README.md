# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **46 trainsets at stations + 183 at depots = 229 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0558-1011-s000000 | line-1 | declared-depot | 58 | 3,451.0 | 10 |
| line-2-0558-0087-s025767 | line-2 | declared-depot | 61 | 3,629.5 | 11 |
| line-3-0476-1027-s000000 | line-3 | declared-depot | 38 | 2,261.0 | 7 |
| line-4-0598-0928-s000000 | line-4 | declared-depot | 26 | 1,547.0 | 5 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0460-0278-s023025 | station | reverse | revenue | 2 |
| line-1 | line-1-0558-1011-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0565-0475-s016038 | station | forward | revenue | 1 |
| line-1 | line-1-0565-0475-s016038 | station | reverse | revenue | 1 |
| line-1 | line-1-0565-0562-s013438 | station | forward | revenue | 1 |
| line-1 | line-1-0565-0562-s013438 | station | reverse | revenue | 1 |
| line-1 | line-1-0584-0675-s010023 | station | forward | revenue | 1 |
| line-1 | line-1-0584-0675-s010023 | station | reverse | revenue | 1 |
| line-1 | line-1-0598-0928-s003279 | station | forward | revenue | 1 |
| line-1 | line-1-0598-0928-s003279 | station | reverse | revenue | 1 |
| line-2 | line-2-0558-0087-s025767 | station | reverse | revenue | 2 |
| line-2 | line-2-0620-0317-s018168 | station | forward | revenue | 1 |
| line-2 | line-2-0620-0317-s018168 | station | reverse | revenue | 1 |
| line-2 | line-2-0707-0415-s014676 | station | forward | revenue | 1 |
| line-2 | line-2-0707-0415-s014676 | station | reverse | revenue | 1 |
| line-2 | line-2-0708-0561-s010062 | station | forward | revenue | 1 |
| line-2 | line-2-0708-0561-s010062 | station | reverse | revenue | 1 |
| line-2 | line-2-0734-0762-s005026 | station | forward | revenue | 1 |
| line-2 | line-2-0734-0762-s005026 | station | reverse | revenue | 1 |
| line-2 | line-2-0737-0508-s011662 | station | forward | revenue | 1 |
| line-2 | line-2-0737-0508-s011662 | station | reverse | revenue | 1 |
| line-2 | line-2-0740-0671-s007046 | station | forward | revenue | 1 |
| line-2 | line-2-0740-0671-s007046 | station | reverse | revenue | 1 |
| line-2 | line-2-0768-0815-s003013 | station | forward | revenue | 1 |
| line-2 | line-2-0768-0815-s003013 | station | reverse | revenue | 1 |
| line-2 | line-2-0841-0891-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0374-0402-s014819 | station | reverse | revenue | 2 |
| line-3 | line-3-0406-0611-s010123 | station | forward | revenue | 1 |
| line-3 | line-3-0406-0611-s010123 | station | reverse | revenue | 1 |
| line-3 | line-3-0476-1027-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0479-0994-s000685 | station | forward | revenue | 1 |
| line-3 | line-3-0479-0994-s000685 | station | reverse | revenue | 1 |
| line-3 | line-3-0481-0718-s007017 | station | forward | revenue | 1 |
| line-3 | line-3-0481-0718-s007017 | station | reverse | revenue | 1 |
| line-4 | line-4-0188-1040-s010650 | station | reverse | revenue | 2 |
| line-4 | line-4-0479-0994-s004073 | station | forward | revenue | 1 |
| line-4 | line-4-0479-0994-s004073 | station | reverse | revenue | 1 |
| line-4 | line-4-0598-0928-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0558-1011-s000000 | depot | — | revenue | 51 |
| line-1 | line-1-0558-1011-s000000 | depot | — | spare | 6 |
| line-1 | line-1-0558-1011-s000000 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0558-0087-s025767 | depot | — | revenue | 53 |
| line-2 | line-2-0558-0087-s025767 | depot | — | spare | 7 |
| line-2 | line-2-0558-0087-s025767 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0476-1027-s000000 | depot | — | revenue | 33 |
| line-3 | line-3-0476-1027-s000000 | depot | — | spare | 4 |
| line-3 | line-3-0476-1027-s000000 | depot | — | cold_reserve | 1 |
| line-4 | line-4-0598-0928-s000000 | depot | — | revenue | 23 |
| line-4 | line-4-0598-0928-s000000 | depot | — | spare | 2 |
| line-4 | line-4-0598-0928-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/abha-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **229 trainsets at 23 stations**; largest initial station queue **16**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **206 revenue, 19 spare, 4 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **46 positions**; **183 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **23 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0558-1011-s000000 | forward | revenue | 7 | pending |
| line-1 | line-1-0598-0928-s003279 | forward | revenue | 7 | pending |
| line-1 | line-1-0598-0928-s003279 | reverse | revenue | 7 | pending |
| line-1 | line-1-0584-0675-s010023 | forward | revenue | 6 | pending |
| line-1 | line-1-0584-0675-s010023 | reverse | revenue | 6 | pending |
| line-1 | line-1-0565-0562-s013438 | forward | revenue | 6 | pending |
| line-1 | line-1-0565-0562-s013438 | reverse | revenue | 6 | pending |
| line-1 | line-1-0565-0475-s016038 | forward | revenue | 6 | pending |
| line-1 | line-1-0565-0475-s016038 | reverse | revenue | 6 | pending |
| line-1 | line-1-0460-0278-s023025 | reverse | revenue | 6 | pending |
| line-1 | line-1-0584-0675-s010023 | forward | spare | 1 | pending |
| line-1 | line-1-0584-0675-s010023 | reverse | spare | 1 | pending |
| line-1 | line-1-0565-0562-s013438 | forward | spare | 1 | pending |
| line-1 | line-1-0565-0562-s013438 | reverse | spare | 1 | pending |
| line-1 | line-1-0565-0475-s016038 | forward | spare | 1 | pending |
| line-1 | line-1-0565-0475-s016038 | reverse | spare | 1 | pending |
| line-1 | line-1-0460-0278-s023025 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0841-0891-s000000 | forward | revenue | 5 | pending |
| line-2 | line-2-0768-0815-s003013 | forward | revenue | 5 | pending |
| line-2 | line-2-0768-0815-s003013 | reverse | revenue | 5 | pending |
| line-2 | line-2-0734-0762-s005026 | forward | revenue | 5 | pending |
| line-2 | line-2-0734-0762-s005026 | reverse | revenue | 5 | pending |
| line-2 | line-2-0740-0671-s007046 | forward | revenue | 5 | pending |
| line-2 | line-2-0740-0671-s007046 | reverse | revenue | 5 | pending |
| line-2 | line-2-0708-0561-s010062 | forward | revenue | 4 | pending |
| line-2 | line-2-0708-0561-s010062 | reverse | revenue | 4 | pending |
| line-2 | line-2-0737-0508-s011662 | forward | revenue | 4 | pending |
| line-2 | line-2-0737-0508-s011662 | reverse | revenue | 4 | pending |
| line-2 | line-2-0707-0415-s014676 | forward | revenue | 4 | pending |
| line-2 | line-2-0707-0415-s014676 | reverse | revenue | 4 | pending |
| line-2 | line-2-0620-0317-s018168 | forward | revenue | 4 | pending |
| line-2 | line-2-0620-0317-s018168 | reverse | revenue | 4 | pending |
| line-2 | line-2-0558-0087-s025767 | reverse | revenue | 4 | pending |
| line-2 | line-2-0708-0561-s010062 | forward | spare | 1 | pending |
| line-2 | line-2-0708-0561-s010062 | reverse | spare | 1 | pending |
| line-2 | line-2-0737-0508-s011662 | forward | spare | 1 | pending |
| line-2 | line-2-0737-0508-s011662 | reverse | spare | 1 | pending |
| line-2 | line-2-0707-0415-s014676 | forward | spare | 1 | pending |
| line-2 | line-2-0707-0415-s014676 | reverse | spare | 1 | pending |
| line-2 | line-2-0620-0317-s018168 | forward | spare | 1 | pending |
| line-2 | line-2-0620-0317-s018168 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0476-1027-s000000 | forward | revenue | 6 | pending |
| line-3 | line-3-0479-0994-s000685 | forward | revenue | 6 | pending |
| line-3 | line-3-0479-0994-s000685 | reverse | revenue | 6 | pending |
| line-3 | line-3-0481-0718-s007017 | forward | revenue | 5 | pending |
| line-3 | line-3-0481-0718-s007017 | reverse | revenue | 5 | pending |
| line-3 | line-3-0406-0611-s010123 | forward | revenue | 5 | pending |
| line-3 | line-3-0406-0611-s010123 | reverse | revenue | 5 | pending |
| line-3 | line-3-0374-0402-s014819 | reverse | revenue | 5 | pending |
| line-3 | line-3-0481-0718-s007017 | forward | spare | 1 | pending |
| line-3 | line-3-0481-0718-s007017 | reverse | spare | 1 | pending |
| line-3 | line-3-0406-0611-s010123 | forward | spare | 1 | pending |
| line-3 | line-3-0406-0611-s010123 | reverse | spare | 1 | pending |
| line-3 | line-3-0374-0402-s014819 | reverse | cold_reserve | 1 | pending |
| line-4 | line-4-0598-0928-s000000 | forward | revenue | 8 | pending |
| line-4 | line-4-0479-0994-s004073 | forward | revenue | 7 | pending |
| line-4 | line-4-0479-0994-s004073 | reverse | revenue | 7 | pending |
| line-4 | line-4-0188-1040-s010650 | reverse | revenue | 7 | pending |
| line-4 | line-4-0479-0994-s004073 | forward | spare | 1 | pending |
| line-4 | line-4-0479-0994-s004073 | reverse | spare | 1 | pending |
| line-4 | line-4-0188-1040-s010650 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**177 trainsets exceed the reference platform envelope**, requiring **10,531.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0460-0278-s023025 | 7 | 2 | 5 | 297.5 |
| line-1-0558-1011-s000000 | 7 | 2 | 5 | 297.5 |
| line-1-0565-0475-s016038 | 14 | 2 | 12 | 714.0 |
| line-1-0565-0562-s013438 | 14 | 2 | 12 | 714.0 |
| line-1-0584-0675-s010023 | 14 | 2 | 12 | 714.0 |
| line-1-0598-0928-s003279 | 14 | 4 | 10 | 595.0 |
| line-2-0558-0087-s025767 | 4 | 2 | 2 | 119.0 |
| line-2-0620-0317-s018168 | 10 | 2 | 8 | 476.0 |
| line-2-0707-0415-s014676 | 10 | 2 | 8 | 476.0 |
| line-2-0708-0561-s010062 | 10 | 2 | 8 | 476.0 |
| line-2-0734-0762-s005026 | 10 | 2 | 8 | 476.0 |
| line-2-0737-0508-s011662 | 10 | 2 | 8 | 476.0 |
| line-2-0740-0671-s007046 | 10 | 2 | 8 | 476.0 |
| line-2-0768-0815-s003013 | 10 | 2 | 8 | 476.0 |
| line-2-0841-0891-s000000 | 5 | 2 | 3 | 178.5 |
| line-3-0374-0402-s014819 | 6 | 2 | 4 | 238.0 |
| line-3-0406-0611-s010123 | 12 | 2 | 10 | 595.0 |
| line-3-0476-1027-s000000 | 6 | 2 | 4 | 238.0 |
| line-3-0479-0994-s000685 | 12 | 4 | 8 | 476.0 |
| line-3-0481-0718-s007017 | 12 | 2 | 10 | 595.0 |
| line-4-0188-1040-s010650 | 8 | 2 | 6 | 357.0 |
| line-4-0479-0994-s004073 | 16 | 4 | 12 | 714.0 |
| line-4-0598-0928-s000000 | 8 | 2 | 6 | 357.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Saudi Arabia/Abha/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
