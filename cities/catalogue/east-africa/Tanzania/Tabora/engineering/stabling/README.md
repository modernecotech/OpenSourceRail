# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **48 trainsets at stations + 46 at depots = 94 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0707-0423-s009182 | line-1 | declared-depot | 15 | 735.0 | 4 |
| line-2-0418-0315-s000000 | line-2 | declared-depot | 5 | 245.0 | 2 |
| line-3-0391-0244-s000000 | line-3 | declared-depot | 5 | 245.0 | 3 |
| line-4-0392-0303-s000000 | line-4 | declared-depot | 7 | 343.0 | 3 |
| line-5-0465-0283-s000000 | line-5 | declared-depot | 5 | 245.0 | 2 |
| line-6-0526-0356-s000000 | line-6 | declared-depot | 9 | 441.0 | 3 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0425-0237-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0465-0283-s001380 | station | forward | revenue | 1 |
| line-1 | line-1-0465-0283-s001380 | station | reverse | revenue | 1 |
| line-1 | line-1-0526-0356-s003510 | station | forward | revenue | 1 |
| line-1 | line-1-0526-0356-s003510 | station | reverse | revenue | 1 |
| line-1 | line-1-0707-0423-s009182 | station | reverse | revenue | 2 |
| line-2 | line-2-0367-0469-s003538 | station | reverse | revenue | 2 |
| line-2 | line-2-0394-0387-s001651 | station | forward | revenue | 1 |
| line-2 | line-2-0394-0387-s001651 | station | reverse | revenue | 1 |
| line-2 | line-2-0395-0383-s001562 | station | forward | revenue | 1 |
| line-2 | line-2-0395-0383-s001562 | station | reverse | revenue | 1 |
| line-2 | line-2-0418-0315-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0391-0244-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0392-0303-s001188 | station | forward | revenue | 1 |
| line-3 | line-3-0392-0303-s001188 | station | reverse | revenue | 1 |
| line-3 | line-3-0395-0383-s002825 | station | forward | revenue | 1 |
| line-3 | line-3-0395-0383-s002825 | station | reverse | revenue | 1 |
| line-3 | line-3-0395-0387-s002905 | station | forward | revenue | 1 |
| line-3 | line-3-0395-0387-s002905 | station | reverse | revenue | 1 |
| line-3 | line-3-0396-0442-s004013 | station | reverse | revenue | 2 |
| line-4 | line-4-0314-0187-s003893 | station | forward | revenue | 1 |
| line-4 | line-4-0314-0187-s003893 | station | reverse | revenue | 1 |
| line-4 | line-4-0314-0262-s002393 | station | forward | revenue | 1 |
| line-4 | line-4-0314-0262-s002393 | station | reverse | revenue | 1 |
| line-4 | line-4-0389-0164-s005584 | station | reverse | revenue | 2 |
| line-4 | line-4-0392-0303-s000000 | station | forward | revenue | 2 |
| line-5 | line-5-0465-0283-s000000 | station | forward | revenue | 2 |
| line-5 | line-5-0488-0164-s002963 | station | reverse | revenue | 2 |
| line-5 | line-5-0511-0238-s001293 | station | forward | revenue | 1 |
| line-5 | line-5-0511-0238-s001293 | station | reverse | revenue | 1 |
| line-6 | line-6-0263-0260-s007448 | station | reverse | revenue | 2 |
| line-6 | line-6-0315-0387-s004477 | station | forward | revenue | 1 |
| line-6 | line-6-0315-0387-s004477 | station | reverse | revenue | 1 |
| line-6 | line-6-0394-0387-s002897 | station | forward | revenue | 1 |
| line-6 | line-6-0394-0387-s002897 | station | reverse | revenue | 1 |
| line-6 | line-6-0526-0356-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0707-0423-s009182 | depot | — | revenue | 12 |
| line-1 | line-1-0707-0423-s009182 | depot | — | spare | 2 |
| line-1 | line-1-0707-0423-s009182 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0418-0315-s000000 | depot | — | revenue | 3 |
| line-2 | line-2-0418-0315-s000000 | depot | — | spare | 1 |
| line-2 | line-2-0418-0315-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0391-0244-s000000 | depot | — | revenue | 3 |
| line-3 | line-3-0391-0244-s000000 | depot | — | spare | 1 |
| line-3 | line-3-0391-0244-s000000 | depot | — | cold_reserve | 1 |
| line-4 | line-4-0392-0303-s000000 | depot | — | revenue | 5 |
| line-4 | line-4-0392-0303-s000000 | depot | — | spare | 1 |
| line-4 | line-4-0392-0303-s000000 | depot | — | cold_reserve | 1 |
| line-5 | line-5-0465-0283-s000000 | depot | — | revenue | 3 |
| line-5 | line-5-0465-0283-s000000 | depot | — | spare | 1 |
| line-5 | line-5-0465-0283-s000000 | depot | — | cold_reserve | 1 |
| line-6 | line-6-0526-0356-s000000 | depot | — | revenue | 7 |
| line-6 | line-6-0526-0356-s000000 | depot | — | spare | 1 |
| line-6 | line-6-0526-0356-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/tabora-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **94 trainsets at 24 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **81 revenue, 7 spare, 6 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **48 positions**; **46 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **18 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0425-0237-s000000 | forward | revenue | 4 | pending |
| line-1 | line-1-0465-0283-s001380 | forward | revenue | 4 | pending |
| line-1 | line-1-0465-0283-s001380 | reverse | revenue | 3 | pending |
| line-1 | line-1-0526-0356-s003510 | forward | revenue | 3 | pending |
| line-1 | line-1-0526-0356-s003510 | reverse | revenue | 3 | pending |
| line-1 | line-1-0707-0423-s009182 | reverse | revenue | 3 | pending |
| line-1 | line-1-0465-0283-s001380 | reverse | spare | 1 | pending |
| line-1 | line-1-0526-0356-s003510 | forward | spare | 1 | pending |
| line-1 | line-1-0526-0356-s003510 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0418-0315-s000000 | forward | revenue | 2 | pending |
| line-2 | line-2-0395-0383-s001562 | forward | revenue | 2 | pending |
| line-2 | line-2-0395-0383-s001562 | reverse | revenue | 2 | pending |
| line-2 | line-2-0394-0387-s001651 | forward | revenue | 2 | pending |
| line-2 | line-2-0394-0387-s001651 | reverse | revenue | 2 | pending |
| line-2 | line-2-0367-0469-s003538 | reverse | revenue | 1 | pending |
| line-2 | line-2-0367-0469-s003538 | reverse | spare | 1 | pending |
| line-2 | line-2-0418-0315-s000000 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0391-0244-s000000 | forward | revenue | 2 | pending |
| line-3 | line-3-0392-0303-s001188 | forward | revenue | 2 | pending |
| line-3 | line-3-0392-0303-s001188 | reverse | revenue | 2 | pending |
| line-3 | line-3-0395-0383-s002825 | forward | revenue | 2 | pending |
| line-3 | line-3-0395-0383-s002825 | reverse | revenue | 2 | pending |
| line-3 | line-3-0395-0387-s002905 | forward | revenue | 1 | pending |
| line-3 | line-3-0395-0387-s002905 | reverse | revenue | 1 | pending |
| line-3 | line-3-0396-0442-s004013 | reverse | revenue | 1 | pending |
| line-3 | line-3-0395-0387-s002905 | forward | spare | 1 | pending |
| line-3 | line-3-0395-0387-s002905 | reverse | cold_reserve | 1 | pending |
| line-4 | line-4-0392-0303-s000000 | forward | revenue | 3 | pending |
| line-4 | line-4-0314-0262-s002393 | forward | revenue | 2 | pending |
| line-4 | line-4-0314-0262-s002393 | reverse | revenue | 2 | pending |
| line-4 | line-4-0314-0187-s003893 | forward | revenue | 2 | pending |
| line-4 | line-4-0314-0187-s003893 | reverse | revenue | 2 | pending |
| line-4 | line-4-0389-0164-s005584 | reverse | revenue | 2 | pending |
| line-4 | line-4-0314-0262-s002393 | forward | spare | 1 | pending |
| line-4 | line-4-0314-0262-s002393 | reverse | cold_reserve | 1 | pending |
| line-5 | line-5-0465-0283-s000000 | forward | revenue | 3 | pending |
| line-5 | line-5-0511-0238-s001293 | forward | revenue | 2 | pending |
| line-5 | line-5-0511-0238-s001293 | reverse | revenue | 2 | pending |
| line-5 | line-5-0488-0164-s002963 | reverse | revenue | 2 | pending |
| line-5 | line-5-0511-0238-s001293 | forward | spare | 1 | pending |
| line-5 | line-5-0511-0238-s001293 | reverse | cold_reserve | 1 | pending |
| line-6 | line-6-0526-0356-s000000 | forward | revenue | 3 | pending |
| line-6 | line-6-0394-0387-s002897 | forward | revenue | 3 | pending |
| line-6 | line-6-0394-0387-s002897 | reverse | revenue | 3 | pending |
| line-6 | line-6-0315-0387-s004477 | forward | revenue | 2 | pending |
| line-6 | line-6-0315-0387-s004477 | reverse | revenue | 2 | pending |
| line-6 | line-6-0263-0260-s007448 | reverse | revenue | 2 | pending |
| line-6 | line-6-0315-0387-s004477 | forward | spare | 1 | pending |
| line-6 | line-6-0315-0387-s004477 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**31 trainsets exceed the reference platform envelope**, requiring **1,519.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0425-0237-s000000 | 4 | 2 | 2 | 98.0 |
| line-1-0465-0283-s001380 | 8 | 4 | 4 | 196.0 |
| line-1-0526-0356-s003510 | 8 | 4 | 4 | 196.0 |
| line-1-0707-0423-s009182 | 3 | 2 | 1 | 49.0 |
| line-2-0367-0469-s003538 | 2 | 2 | 0 | 0.0 |
| line-2-0394-0387-s001651 | 4 | 4 | 0 | 0.0 |
| line-2-0395-0383-s001562 | 4 | 4 | 0 | 0.0 |
| line-2-0418-0315-s000000 | 3 | 2 | 1 | 49.0 |
| line-3-0391-0244-s000000 | 2 | 2 | 0 | 0.0 |
| line-3-0392-0303-s001188 | 4 | 4 | 0 | 0.0 |
| line-3-0395-0383-s002825 | 4 | 4 | 0 | 0.0 |
| line-3-0395-0387-s002905 | 4 | 4 | 0 | 0.0 |
| line-3-0396-0442-s004013 | 1 | 2 | 0 | 0.0 |
| line-4-0314-0187-s003893 | 4 | 2 | 2 | 98.0 |
| line-4-0314-0262-s002393 | 6 | 2 | 4 | 196.0 |
| line-4-0389-0164-s005584 | 2 | 2 | 0 | 0.0 |
| line-4-0392-0303-s000000 | 3 | 2 | 1 | 49.0 |
| line-5-0465-0283-s000000 | 3 | 2 | 1 | 49.0 |
| line-5-0488-0164-s002963 | 2 | 2 | 0 | 0.0 |
| line-5-0511-0238-s001293 | 6 | 2 | 4 | 196.0 |
| line-6-0263-0260-s007448 | 2 | 2 | 0 | 0.0 |
| line-6-0315-0387-s004477 | 6 | 2 | 4 | 196.0 |
| line-6-0394-0387-s002897 | 6 | 4 | 2 | 98.0 |
| line-6-0526-0356-s000000 | 3 | 2 | 1 | 49.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Tanzania/Tabora/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
