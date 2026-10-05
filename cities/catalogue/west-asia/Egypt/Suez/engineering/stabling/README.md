# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **32 trainsets at stations + 134 at depots = 166 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0409-0232-s022662 | line-1 | declared-depot | 60 | 3,570.0 | 10 |
| line-2-0676-0236-s000000 | line-2 | declared-depot | 39 | 2,320.5 | 8 |
| line-3-0202-0517-s000000 | line-3 | declared-depot | 35 | 2,082.5 | 6 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0409-0232-s022662 | station | reverse | revenue | 2 |
| line-1 | line-1-0473-0324-s020163 | station | forward | revenue | 1 |
| line-1 | line-1-0473-0324-s020163 | station | reverse | revenue | 1 |
| line-1 | line-1-0537-0416-s017652 | station | forward | revenue | 1 |
| line-1 | line-1-0537-0416-s017652 | station | reverse | revenue | 1 |
| line-1 | line-1-0613-0526-s014635 | station | forward | revenue | 1 |
| line-1 | line-1-0613-0526-s014635 | station | reverse | revenue | 1 |
| line-1 | line-1-0690-0636-s011622 | station | forward | revenue | 1 |
| line-1 | line-1-0690-0636-s011622 | station | reverse | revenue | 1 |
| line-1 | line-1-1054-1032-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0124-0683-s016233 | station | reverse | revenue | 2 |
| line-2 | line-2-0310-0571-s011126 | station | forward | revenue | 1 |
| line-2 | line-2-0310-0571-s011126 | station | reverse | revenue | 1 |
| line-2 | line-2-0394-0494-s008562 | station | forward | revenue | 1 |
| line-2 | line-2-0394-0494-s008562 | station | reverse | revenue | 1 |
| line-2 | line-2-0479-0417-s006014 | station | forward | revenue | 1 |
| line-2 | line-2-0479-0417-s006014 | station | reverse | revenue | 1 |
| line-2 | line-2-0577-0326-s003007 | station | forward | revenue | 1 |
| line-2 | line-2-0577-0326-s003007 | station | reverse | revenue | 1 |
| line-2 | line-2-0676-0236-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0202-0517-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0355-0380-s006022 | station | forward | revenue | 1 |
| line-3 | line-3-0355-0380-s006022 | station | reverse | revenue | 1 |
| line-3 | line-3-0441-0275-s009046 | station | forward | revenue | 1 |
| line-3 | line-3-0441-0275-s009046 | station | reverse | revenue | 1 |
| line-3 | line-3-0608-0185-s014633 | station | reverse | revenue | 2 |
| line-1 | line-1-0409-0232-s022662 | depot | — | revenue | 53 |
| line-1 | line-1-0409-0232-s022662 | depot | — | spare | 6 |
| line-1 | line-1-0409-0232-s022662 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0676-0236-s000000 | depot | — | revenue | 34 |
| line-2 | line-2-0676-0236-s000000 | depot | — | spare | 4 |
| line-2 | line-2-0676-0236-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0202-0517-s000000 | depot | — | revenue | 31 |
| line-3 | line-3-0202-0517-s000000 | depot | — | spare | 3 |
| line-3 | line-3-0202-0517-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/suez-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **166 trainsets at 16 stations**; largest initial station queue **15**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **150 revenue, 13 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **32 positions**; **134 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **16 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-1054-1032-s000000 | forward | revenue | 7 | pending |
| line-1 | line-1-0690-0636-s011622 | forward | revenue | 7 | pending |
| line-1 | line-1-0690-0636-s011622 | reverse | revenue | 7 | pending |
| line-1 | line-1-0613-0526-s014635 | forward | revenue | 7 | pending |
| line-1 | line-1-0613-0526-s014635 | reverse | revenue | 7 | pending |
| line-1 | line-1-0537-0416-s017652 | forward | revenue | 6 | pending |
| line-1 | line-1-0537-0416-s017652 | reverse | revenue | 6 | pending |
| line-1 | line-1-0473-0324-s020163 | forward | revenue | 6 | pending |
| line-1 | line-1-0473-0324-s020163 | reverse | revenue | 6 | pending |
| line-1 | line-1-0409-0232-s022662 | reverse | revenue | 6 | pending |
| line-1 | line-1-0537-0416-s017652 | forward | spare | 1 | pending |
| line-1 | line-1-0537-0416-s017652 | reverse | spare | 1 | pending |
| line-1 | line-1-0473-0324-s020163 | forward | spare | 1 | pending |
| line-1 | line-1-0473-0324-s020163 | reverse | spare | 1 | pending |
| line-1 | line-1-0409-0232-s022662 | reverse | spare | 1 | pending |
| line-1 | line-1-1054-1032-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0690-0636-s011622 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0676-0236-s000000 | forward | revenue | 5 | pending |
| line-2 | line-2-0577-0326-s003007 | forward | revenue | 5 | pending |
| line-2 | line-2-0577-0326-s003007 | reverse | revenue | 5 | pending |
| line-2 | line-2-0479-0417-s006014 | forward | revenue | 5 | pending |
| line-2 | line-2-0479-0417-s006014 | reverse | revenue | 5 | pending |
| line-2 | line-2-0394-0494-s008562 | forward | revenue | 5 | pending |
| line-2 | line-2-0394-0494-s008562 | reverse | revenue | 4 | pending |
| line-2 | line-2-0310-0571-s011126 | forward | revenue | 4 | pending |
| line-2 | line-2-0310-0571-s011126 | reverse | revenue | 4 | pending |
| line-2 | line-2-0124-0683-s016233 | reverse | revenue | 4 | pending |
| line-2 | line-2-0394-0494-s008562 | reverse | spare | 1 | pending |
| line-2 | line-2-0310-0571-s011126 | forward | spare | 1 | pending |
| line-2 | line-2-0310-0571-s011126 | reverse | spare | 1 | pending |
| line-2 | line-2-0124-0683-s016233 | reverse | spare | 1 | pending |
| line-2 | line-2-0676-0236-s000000 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0202-0517-s000000 | forward | revenue | 7 | pending |
| line-3 | line-3-0355-0380-s006022 | forward | revenue | 7 | pending |
| line-3 | line-3-0355-0380-s006022 | reverse | revenue | 7 | pending |
| line-3 | line-3-0441-0275-s009046 | forward | revenue | 6 | pending |
| line-3 | line-3-0441-0275-s009046 | reverse | revenue | 6 | pending |
| line-3 | line-3-0608-0185-s014633 | reverse | revenue | 6 | pending |
| line-3 | line-3-0441-0275-s009046 | forward | spare | 1 | pending |
| line-3 | line-3-0441-0275-s009046 | reverse | spare | 1 | pending |
| line-3 | line-3-0608-0185-s014633 | reverse | spare | 1 | pending |
| line-3 | line-3-0202-0517-s000000 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**134 trainsets exceed the reference platform envelope**, requiring **7,973.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0409-0232-s022662 | 7 | 2 | 5 | 297.5 |
| line-1-0473-0324-s020163 | 14 | 2 | 12 | 714.0 |
| line-1-0537-0416-s017652 | 14 | 2 | 12 | 714.0 |
| line-1-0613-0526-s014635 | 14 | 2 | 12 | 714.0 |
| line-1-0690-0636-s011622 | 15 | 2 | 13 | 773.5 |
| line-1-1054-1032-s000000 | 8 | 2 | 6 | 357.0 |
| line-2-0124-0683-s016233 | 5 | 2 | 3 | 178.5 |
| line-2-0310-0571-s011126 | 10 | 2 | 8 | 476.0 |
| line-2-0394-0494-s008562 | 10 | 2 | 8 | 476.0 |
| line-2-0479-0417-s006014 | 10 | 2 | 8 | 476.0 |
| line-2-0577-0326-s003007 | 10 | 2 | 8 | 476.0 |
| line-2-0676-0236-s000000 | 6 | 2 | 4 | 238.0 |
| line-3-0202-0517-s000000 | 8 | 2 | 6 | 357.0 |
| line-3-0355-0380-s006022 | 14 | 2 | 12 | 714.0 |
| line-3-0441-0275-s009046 | 14 | 2 | 12 | 714.0 |
| line-3-0608-0185-s014633 | 7 | 2 | 5 | 297.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Egypt/Suez/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
