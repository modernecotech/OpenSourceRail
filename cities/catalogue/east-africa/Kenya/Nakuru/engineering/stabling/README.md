# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **30 trainsets at stations + 122 at depots = 152 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0383-0392-s000000 | line-1 | declared-depot | 28 | 1,666.0 | 5 |
| line-2-1065-0208-s020413 | line-2 | declared-depot | 55 | 3,272.5 | 9 |
| line-3-0651-0932-s000000 | line-3 | declared-depot | 39 | 2,320.5 | 8 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0383-0392-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0424-0519-s002915 | station | forward | revenue | 1 |
| line-1 | line-1-0424-0519-s002915 | station | reverse | revenue | 1 |
| line-1 | line-1-0470-0659-s006131 | station | forward | revenue | 1 |
| line-1 | line-1-0470-0659-s006131 | station | reverse | revenue | 1 |
| line-1 | line-1-0531-0881-s011456 | station | reverse | revenue | 2 |
| line-2 | line-2-0381-0736-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0470-0659-s002652 | station | forward | revenue | 1 |
| line-2 | line-2-0470-0659-s002652 | station | reverse | revenue | 1 |
| line-2 | line-2-0577-0567-s005824 | station | forward | revenue | 1 |
| line-2 | line-2-0577-0567-s005824 | station | reverse | revenue | 1 |
| line-2 | line-2-0700-0462-s009458 | station | forward | revenue | 1 |
| line-2 | line-2-0700-0462-s009458 | station | reverse | revenue | 1 |
| line-2 | line-2-1065-0208-s020413 | station | reverse | revenue | 2 |
| line-3 | line-3-0562-0648-s007008 | station | forward | revenue | 1 |
| line-3 | line-3-0562-0648-s007008 | station | reverse | revenue | 1 |
| line-3 | line-3-0564-0202-s016235 | station | reverse | revenue | 2 |
| line-3 | line-3-0576-0506-s010020 | station | forward | revenue | 1 |
| line-3 | line-3-0576-0506-s010020 | station | reverse | revenue | 1 |
| line-3 | line-3-0577-0567-s008780 | station | forward | revenue | 1 |
| line-3 | line-3-0577-0567-s008780 | station | reverse | revenue | 1 |
| line-3 | line-3-0582-0812-s003511 | station | forward | revenue | 1 |
| line-3 | line-3-0582-0812-s003511 | station | reverse | revenue | 1 |
| line-3 | line-3-0651-0932-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0383-0392-s000000 | depot | — | revenue | 24 |
| line-1 | line-1-0383-0392-s000000 | depot | — | spare | 3 |
| line-1 | line-1-0383-0392-s000000 | depot | — | cold_reserve | 1 |
| line-2 | line-2-1065-0208-s020413 | depot | — | revenue | 49 |
| line-2 | line-2-1065-0208-s020413 | depot | — | spare | 5 |
| line-2 | line-2-1065-0208-s020413 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0651-0932-s000000 | depot | — | revenue | 34 |
| line-3 | line-3-0651-0932-s000000 | depot | — | spare | 4 |
| line-3 | line-3-0651-0932-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/nakuru-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **152 trainsets at 15 stations**; largest initial station queue **16**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **137 revenue, 12 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **30 positions**; **122 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **15 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0383-0392-s000000 | forward | revenue | 6 | pending |
| line-1 | line-1-0424-0519-s002915 | forward | revenue | 6 | pending |
| line-1 | line-1-0424-0519-s002915 | reverse | revenue | 5 | pending |
| line-1 | line-1-0470-0659-s006131 | forward | revenue | 5 | pending |
| line-1 | line-1-0470-0659-s006131 | reverse | revenue | 5 | pending |
| line-1 | line-1-0531-0881-s011456 | reverse | revenue | 5 | pending |
| line-1 | line-1-0424-0519-s002915 | reverse | spare | 1 | pending |
| line-1 | line-1-0470-0659-s006131 | forward | spare | 1 | pending |
| line-1 | line-1-0470-0659-s006131 | reverse | spare | 1 | pending |
| line-1 | line-1-0531-0881-s011456 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0381-0736-s000000 | forward | revenue | 8 | pending |
| line-2 | line-2-0470-0659-s002652 | forward | revenue | 8 | pending |
| line-2 | line-2-0470-0659-s002652 | reverse | revenue | 8 | pending |
| line-2 | line-2-0577-0567-s005824 | forward | revenue | 7 | pending |
| line-2 | line-2-0577-0567-s005824 | reverse | revenue | 7 | pending |
| line-2 | line-2-0700-0462-s009458 | forward | revenue | 7 | pending |
| line-2 | line-2-0700-0462-s009458 | reverse | revenue | 7 | pending |
| line-2 | line-2-1065-0208-s020413 | reverse | revenue | 7 | pending |
| line-2 | line-2-0577-0567-s005824 | forward | spare | 1 | pending |
| line-2 | line-2-0577-0567-s005824 | reverse | spare | 1 | pending |
| line-2 | line-2-0700-0462-s009458 | forward | spare | 1 | pending |
| line-2 | line-2-0700-0462-s009458 | reverse | spare | 1 | pending |
| line-2 | line-2-1065-0208-s020413 | reverse | spare | 1 | pending |
| line-2 | line-2-0381-0736-s000000 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0651-0932-s000000 | forward | revenue | 5 | pending |
| line-3 | line-3-0582-0812-s003511 | forward | revenue | 5 | pending |
| line-3 | line-3-0582-0812-s003511 | reverse | revenue | 5 | pending |
| line-3 | line-3-0562-0648-s007008 | forward | revenue | 5 | pending |
| line-3 | line-3-0562-0648-s007008 | reverse | revenue | 5 | pending |
| line-3 | line-3-0577-0567-s008780 | forward | revenue | 5 | pending |
| line-3 | line-3-0577-0567-s008780 | reverse | revenue | 4 | pending |
| line-3 | line-3-0576-0506-s010020 | forward | revenue | 4 | pending |
| line-3 | line-3-0576-0506-s010020 | reverse | revenue | 4 | pending |
| line-3 | line-3-0564-0202-s016235 | reverse | revenue | 4 | pending |
| line-3 | line-3-0577-0567-s008780 | reverse | spare | 1 | pending |
| line-3 | line-3-0576-0506-s010020 | forward | spare | 1 | pending |
| line-3 | line-3-0576-0506-s010020 | reverse | spare | 1 | pending |
| line-3 | line-3-0564-0202-s016235 | reverse | spare | 1 | pending |
| line-3 | line-3-0651-0932-s000000 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**114 trainsets exceed the reference platform envelope**, requiring **6,783.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0383-0392-s000000 | 6 | 2 | 4 | 238.0 |
| line-1-0424-0519-s002915 | 12 | 2 | 10 | 595.0 |
| line-1-0470-0659-s006131 | 12 | 4 | 8 | 476.0 |
| line-1-0531-0881-s011456 | 6 | 2 | 4 | 238.0 |
| line-2-0381-0736-s000000 | 9 | 2 | 7 | 416.5 |
| line-2-0470-0659-s002652 | 16 | 4 | 12 | 714.0 |
| line-2-0577-0567-s005824 | 16 | 4 | 12 | 714.0 |
| line-2-0700-0462-s009458 | 16 | 2 | 14 | 833.0 |
| line-2-1065-0208-s020413 | 8 | 2 | 6 | 357.0 |
| line-3-0562-0648-s007008 | 10 | 2 | 8 | 476.0 |
| line-3-0564-0202-s016235 | 5 | 2 | 3 | 178.5 |
| line-3-0576-0506-s010020 | 10 | 2 | 8 | 476.0 |
| line-3-0577-0567-s008780 | 10 | 4 | 6 | 357.0 |
| line-3-0582-0812-s003511 | 10 | 2 | 8 | 476.0 |
| line-3-0651-0932-s000000 | 6 | 2 | 4 | 238.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Kenya/Nakuru/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
