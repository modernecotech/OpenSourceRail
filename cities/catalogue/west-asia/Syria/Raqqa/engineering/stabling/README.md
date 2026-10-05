# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **36 trainsets at stations + 99 at depots = 135 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0529-0080-s000000 | line-1 | declared-depot | 31 | 1,844.5 | 7 |
| line-2-0628-0393-s000000 | line-2 | declared-depot | 28 | 1,666.0 | 6 |
| line-3-0480-0367-s015672 | line-3 | declared-depot | 40 | 2,380.0 | 8 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0529-0080-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0532-0339-s005453 | station | forward | revenue | 1 |
| line-1 | line-1-0532-0339-s005453 | station | reverse | revenue | 1 |
| line-1 | line-1-0548-0492-s008657 | station | forward | revenue | 1 |
| line-1 | line-1-0548-0492-s008657 | station | reverse | revenue | 1 |
| line-1 | line-1-0554-0550-s009867 | station | forward | revenue | 1 |
| line-1 | line-1-0554-0550-s009867 | station | reverse | revenue | 1 |
| line-1 | line-1-0564-0648-s011921 | station | forward | revenue | 1 |
| line-1 | line-1-0564-0648-s011921 | station | reverse | revenue | 1 |
| line-1 | line-1-0565-0653-s012029 | station | forward | revenue | 1 |
| line-1 | line-1-0565-0653-s012029 | station | reverse | revenue | 1 |
| line-1 | line-1-0571-0716-s013339 | station | reverse | revenue | 2 |
| line-2 | line-2-0294-0806-s011917 | station | reverse | revenue | 2 |
| line-2 | line-2-0458-0603-s006054 | station | forward | revenue | 1 |
| line-2 | line-2-0458-0603-s006054 | station | reverse | revenue | 1 |
| line-2 | line-2-0525-0520-s003674 | station | forward | revenue | 1 |
| line-2 | line-2-0525-0520-s003674 | station | reverse | revenue | 1 |
| line-2 | line-2-0548-0492-s002854 | station | forward | revenue | 1 |
| line-2 | line-2-0548-0492-s002854 | station | reverse | revenue | 1 |
| line-2 | line-2-0628-0393-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0480-0367-s015672 | station | reverse | revenue | 2 |
| line-3 | line-3-0525-0520-s012228 | station | forward | revenue | 1 |
| line-3 | line-3-0525-0520-s012228 | station | reverse | revenue | 1 |
| line-3 | line-3-0564-0648-s009310 | station | forward | revenue | 1 |
| line-3 | line-3-0564-0648-s009310 | station | reverse | revenue | 1 |
| line-3 | line-3-0565-0653-s009201 | station | forward | revenue | 1 |
| line-3 | line-3-0565-0653-s009201 | station | reverse | revenue | 1 |
| line-3 | line-3-0591-1029-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0594-0750-s007009 | station | forward | revenue | 1 |
| line-3 | line-3-0594-0750-s007009 | station | reverse | revenue | 1 |
| line-1 | line-1-0529-0080-s000000 | depot | — | revenue | 26 |
| line-1 | line-1-0529-0080-s000000 | depot | — | spare | 4 |
| line-1 | line-1-0529-0080-s000000 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0628-0393-s000000 | depot | — | revenue | 24 |
| line-2 | line-2-0628-0393-s000000 | depot | — | spare | 3 |
| line-2 | line-2-0628-0393-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0480-0367-s015672 | depot | — | revenue | 35 |
| line-3 | line-3-0480-0367-s015672 | depot | — | spare | 4 |
| line-3 | line-3-0480-0367-s015672 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/raqqa-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **135 trainsets at 18 stations**; largest initial station queue **11**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **121 revenue, 11 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **36 positions**; **99 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **18 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0529-0080-s000000 | forward | revenue | 4 | pending |
| line-1 | line-1-0532-0339-s005453 | forward | revenue | 4 | pending |
| line-1 | line-1-0532-0339-s005453 | reverse | revenue | 4 | pending |
| line-1 | line-1-0548-0492-s008657 | forward | revenue | 4 | pending |
| line-1 | line-1-0548-0492-s008657 | reverse | revenue | 3 | pending |
| line-1 | line-1-0554-0550-s009867 | forward | revenue | 3 | pending |
| line-1 | line-1-0554-0550-s009867 | reverse | revenue | 3 | pending |
| line-1 | line-1-0564-0648-s011921 | forward | revenue | 3 | pending |
| line-1 | line-1-0564-0648-s011921 | reverse | revenue | 3 | pending |
| line-1 | line-1-0565-0653-s012029 | forward | revenue | 3 | pending |
| line-1 | line-1-0565-0653-s012029 | reverse | revenue | 3 | pending |
| line-1 | line-1-0571-0716-s013339 | reverse | revenue | 3 | pending |
| line-1 | line-1-0548-0492-s008657 | reverse | spare | 1 | pending |
| line-1 | line-1-0554-0550-s009867 | forward | spare | 1 | pending |
| line-1 | line-1-0554-0550-s009867 | reverse | spare | 1 | pending |
| line-1 | line-1-0564-0648-s011921 | forward | spare | 1 | pending |
| line-1 | line-1-0564-0648-s011921 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0628-0393-s000000 | forward | revenue | 5 | pending |
| line-2 | line-2-0548-0492-s002854 | forward | revenue | 5 | pending |
| line-2 | line-2-0548-0492-s002854 | reverse | revenue | 4 | pending |
| line-2 | line-2-0525-0520-s003674 | forward | revenue | 4 | pending |
| line-2 | line-2-0525-0520-s003674 | reverse | revenue | 4 | pending |
| line-2 | line-2-0458-0603-s006054 | forward | revenue | 4 | pending |
| line-2 | line-2-0458-0603-s006054 | reverse | revenue | 4 | pending |
| line-2 | line-2-0294-0806-s011917 | reverse | revenue | 4 | pending |
| line-2 | line-2-0548-0492-s002854 | reverse | spare | 1 | pending |
| line-2 | line-2-0525-0520-s003674 | forward | spare | 1 | pending |
| line-2 | line-2-0525-0520-s003674 | reverse | spare | 1 | pending |
| line-2 | line-2-0458-0603-s006054 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0591-1029-s000000 | forward | revenue | 5 | pending |
| line-3 | line-3-0594-0750-s007009 | forward | revenue | 5 | pending |
| line-3 | line-3-0594-0750-s007009 | reverse | revenue | 5 | pending |
| line-3 | line-3-0565-0653-s009201 | forward | revenue | 5 | pending |
| line-3 | line-3-0565-0653-s009201 | reverse | revenue | 5 | pending |
| line-3 | line-3-0564-0648-s009310 | forward | revenue | 5 | pending |
| line-3 | line-3-0564-0648-s009310 | reverse | revenue | 5 | pending |
| line-3 | line-3-0525-0520-s012228 | forward | revenue | 4 | pending |
| line-3 | line-3-0525-0520-s012228 | reverse | revenue | 4 | pending |
| line-3 | line-3-0480-0367-s015672 | reverse | revenue | 4 | pending |
| line-3 | line-3-0525-0520-s012228 | forward | spare | 1 | pending |
| line-3 | line-3-0525-0520-s012228 | reverse | spare | 1 | pending |
| line-3 | line-3-0480-0367-s015672 | reverse | spare | 1 | pending |
| line-3 | line-3-0591-1029-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0594-0750-s007009 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**83 trainsets exceed the reference platform envelope**, requiring **4,938.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0529-0080-s000000 | 4 | 2 | 2 | 119.0 |
| line-1-0532-0339-s005453 | 8 | 2 | 6 | 357.0 |
| line-1-0548-0492-s008657 | 8 | 4 | 4 | 238.0 |
| line-1-0554-0550-s009867 | 8 | 2 | 6 | 357.0 |
| line-1-0564-0648-s011921 | 8 | 4 | 4 | 238.0 |
| line-1-0565-0653-s012029 | 6 | 4 | 2 | 119.0 |
| line-1-0571-0716-s013339 | 3 | 2 | 1 | 59.5 |
| line-2-0294-0806-s011917 | 4 | 2 | 2 | 119.0 |
| line-2-0458-0603-s006054 | 9 | 2 | 7 | 416.5 |
| line-2-0525-0520-s003674 | 10 | 4 | 6 | 357.0 |
| line-2-0548-0492-s002854 | 10 | 4 | 6 | 357.0 |
| line-2-0628-0393-s000000 | 5 | 2 | 3 | 178.5 |
| line-3-0480-0367-s015672 | 5 | 2 | 3 | 178.5 |
| line-3-0525-0520-s012228 | 10 | 4 | 6 | 357.0 |
| line-3-0564-0648-s009310 | 10 | 4 | 6 | 357.0 |
| line-3-0565-0653-s009201 | 10 | 4 | 6 | 357.0 |
| line-3-0591-1029-s000000 | 6 | 2 | 4 | 238.0 |
| line-3-0594-0750-s007009 | 11 | 2 | 9 | 535.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Syria/Raqqa/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
