# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **28 trainsets at stations + 73 at depots = 101 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0540-0014-s016255 | line-1 | declared-depot | 38 | 2,261.0 | 8 |
| line-2-0616-0676-s000000 | line-2 | declared-depot | 12 | 714.0 | 3 |
| line-3-0185-0604-s000000 | line-3 | declared-depot | 23 | 1,368.5 | 5 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0514-0251-s011148 | station | forward | revenue | 1 |
| line-1 | line-1-0514-0251-s011148 | station | reverse | revenue | 1 |
| line-1 | line-1-0530-0373-s008576 | station | forward | revenue | 1 |
| line-1 | line-1-0530-0373-s008576 | station | reverse | revenue | 1 |
| line-1 | line-1-0540-0014-s016255 | station | reverse | revenue | 2 |
| line-1 | line-1-0546-0494-s006023 | station | forward | revenue | 1 |
| line-1 | line-1-0546-0494-s006023 | station | reverse | revenue | 1 |
| line-1 | line-1-0554-0552-s004797 | station | forward | revenue | 1 |
| line-1 | line-1-0554-0552-s004797 | station | reverse | revenue | 1 |
| line-1 | line-1-0566-0636-s003017 | station | forward | revenue | 1 |
| line-1 | line-1-0566-0636-s003017 | station | reverse | revenue | 1 |
| line-1 | line-1-0585-0779-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0372-0609-s005435 | station | reverse | revenue | 2 |
| line-2 | line-2-0494-0642-s002722 | station | forward | revenue | 1 |
| line-2 | line-2-0494-0642-s002722 | station | reverse | revenue | 1 |
| line-2 | line-2-0616-0676-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0185-0604-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0313-0518-s003507 | station | forward | revenue | 1 |
| line-3 | line-3-0313-0518-s003507 | station | reverse | revenue | 1 |
| line-3 | line-3-0454-0450-s007019 | station | forward | revenue | 1 |
| line-3 | line-3-0454-0450-s007019 | station | reverse | revenue | 1 |
| line-3 | line-3-0577-0391-s010073 | station | reverse | revenue | 2 |
| line-1 | line-1-0540-0014-s016255 | depot | — | revenue | 33 |
| line-1 | line-1-0540-0014-s016255 | depot | — | spare | 4 |
| line-1 | line-1-0540-0014-s016255 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0616-0676-s000000 | depot | — | revenue | 10 |
| line-2 | line-2-0616-0676-s000000 | depot | — | spare | 1 |
| line-2 | line-2-0616-0676-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0185-0604-s000000 | depot | — | revenue | 20 |
| line-3 | line-3-0185-0604-s000000 | depot | — | spare | 2 |
| line-3 | line-3-0185-0604-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/rajshahi-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **101 trainsets at 14 stations**; largest initial station queue **10**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **91 revenue, 7 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **28 positions**; **73 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **14 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0585-0779-s000000 | forward | revenue | 4 | pending |
| line-1 | line-1-0566-0636-s003017 | forward | revenue | 4 | pending |
| line-1 | line-1-0566-0636-s003017 | reverse | revenue | 4 | pending |
| line-1 | line-1-0554-0552-s004797 | forward | revenue | 4 | pending |
| line-1 | line-1-0554-0552-s004797 | reverse | revenue | 4 | pending |
| line-1 | line-1-0546-0494-s006023 | forward | revenue | 4 | pending |
| line-1 | line-1-0546-0494-s006023 | reverse | revenue | 4 | pending |
| line-1 | line-1-0530-0373-s008576 | forward | revenue | 4 | pending |
| line-1 | line-1-0530-0373-s008576 | reverse | revenue | 4 | pending |
| line-1 | line-1-0514-0251-s011148 | forward | revenue | 4 | pending |
| line-1 | line-1-0514-0251-s011148 | reverse | revenue | 4 | pending |
| line-1 | line-1-0540-0014-s016255 | reverse | revenue | 3 | pending |
| line-1 | line-1-0540-0014-s016255 | reverse | spare | 1 | pending |
| line-1 | line-1-0585-0779-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0566-0636-s003017 | forward | spare | 1 | pending |
| line-1 | line-1-0566-0636-s003017 | reverse | spare | 1 | pending |
| line-1 | line-1-0554-0552-s004797 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0616-0676-s000000 | forward | revenue | 4 | pending |
| line-2 | line-2-0494-0642-s002722 | forward | revenue | 4 | pending |
| line-2 | line-2-0494-0642-s002722 | reverse | revenue | 4 | pending |
| line-2 | line-2-0372-0609-s005435 | reverse | revenue | 4 | pending |
| line-2 | line-2-0616-0676-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0494-0642-s002722 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0185-0604-s000000 | forward | revenue | 5 | pending |
| line-3 | line-3-0313-0518-s003507 | forward | revenue | 5 | pending |
| line-3 | line-3-0313-0518-s003507 | reverse | revenue | 5 | pending |
| line-3 | line-3-0454-0450-s007019 | forward | revenue | 5 | pending |
| line-3 | line-3-0454-0450-s007019 | reverse | revenue | 4 | pending |
| line-3 | line-3-0577-0391-s010073 | reverse | revenue | 4 | pending |
| line-3 | line-3-0454-0450-s007019 | reverse | spare | 1 | pending |
| line-3 | line-3-0577-0391-s010073 | reverse | spare | 1 | pending |
| line-3 | line-3-0185-0604-s000000 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**73 trainsets exceed the reference platform envelope**, requiring **4,343.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0514-0251-s011148 | 8 | 2 | 6 | 357.0 |
| line-1-0530-0373-s008576 | 8 | 2 | 6 | 357.0 |
| line-1-0540-0014-s016255 | 4 | 2 | 2 | 119.0 |
| line-1-0546-0494-s006023 | 8 | 2 | 6 | 357.0 |
| line-1-0554-0552-s004797 | 9 | 2 | 7 | 416.5 |
| line-1-0566-0636-s003017 | 10 | 2 | 8 | 476.0 |
| line-1-0585-0779-s000000 | 5 | 2 | 3 | 178.5 |
| line-2-0372-0609-s005435 | 4 | 2 | 2 | 119.0 |
| line-2-0494-0642-s002722 | 9 | 2 | 7 | 416.5 |
| line-2-0616-0676-s000000 | 5 | 2 | 3 | 178.5 |
| line-3-0185-0604-s000000 | 6 | 2 | 4 | 238.0 |
| line-3-0313-0518-s003507 | 10 | 2 | 8 | 476.0 |
| line-3-0454-0450-s007019 | 10 | 2 | 8 | 476.0 |
| line-3-0577-0391-s010073 | 5 | 2 | 3 | 178.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/south-asia/Bangladesh/Rajshahi/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
