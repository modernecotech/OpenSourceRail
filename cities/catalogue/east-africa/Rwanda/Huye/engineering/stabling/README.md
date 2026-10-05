# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **24 trainsets at stations + 56 at depots = 80 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0008-0663-s014481 | line-1 | declared-depot | 21 | 1,029.0 | 4 |
| line-2-0666-0617-s000000 | line-2 | declared-depot | 16 | 784.0 | 4 |
| line-3-0005-0503-s000000 | line-3 | declared-depot | 19 | 931.0 | 4 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0008-0663-s014481 | station | reverse | revenue | 2 |
| line-1 | line-1-0308-0440-s006030 | station | forward | revenue | 1 |
| line-1 | line-1-0308-0440-s006030 | station | reverse | revenue | 1 |
| line-1 | line-1-0415-0355-s003010 | station | forward | revenue | 1 |
| line-1 | line-1-0415-0355-s003010 | station | reverse | revenue | 1 |
| line-1 | line-1-0520-0272-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0310-0231-s012457 | station | reverse | revenue | 2 |
| line-2 | line-2-0386-0302-s010127 | station | forward | revenue | 1 |
| line-2 | line-2-0386-0302-s010127 | station | reverse | revenue | 1 |
| line-2 | line-2-0462-0372-s007792 | station | forward | revenue | 1 |
| line-2 | line-2-0462-0372-s007792 | station | reverse | revenue | 1 |
| line-2 | line-2-0518-0424-s006089 | station | forward | revenue | 1 |
| line-2 | line-2-0518-0424-s006089 | station | reverse | revenue | 1 |
| line-2 | line-2-0666-0617-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0005-0503-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0184-0372-s007006 | station | forward | revenue | 1 |
| line-3 | line-3-0184-0372-s007006 | station | reverse | revenue | 1 |
| line-3 | line-3-0362-0236-s011985 | station | reverse | revenue | 2 |
| line-1 | line-1-0008-0663-s014481 | depot | — | revenue | 18 |
| line-1 | line-1-0008-0663-s014481 | depot | — | spare | 2 |
| line-1 | line-1-0008-0663-s014481 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0666-0617-s000000 | depot | — | revenue | 13 |
| line-2 | line-2-0666-0617-s000000 | depot | — | spare | 2 |
| line-2 | line-2-0666-0617-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0005-0503-s000000 | depot | — | revenue | 16 |
| line-3 | line-3-0005-0503-s000000 | depot | — | spare | 2 |
| line-3 | line-3-0005-0503-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/huye-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **80 trainsets at 12 stations**; largest initial station queue **12**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **71 revenue, 6 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **24 positions**; **56 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **12 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0520-0272-s000000 | forward | revenue | 5 | pending |
| line-1 | line-1-0415-0355-s003010 | forward | revenue | 5 | pending |
| line-1 | line-1-0415-0355-s003010 | reverse | revenue | 4 | pending |
| line-1 | line-1-0308-0440-s006030 | forward | revenue | 4 | pending |
| line-1 | line-1-0308-0440-s006030 | reverse | revenue | 4 | pending |
| line-1 | line-1-0008-0663-s014481 | reverse | revenue | 4 | pending |
| line-1 | line-1-0415-0355-s003010 | reverse | spare | 1 | pending |
| line-1 | line-1-0308-0440-s006030 | forward | spare | 1 | pending |
| line-1 | line-1-0308-0440-s006030 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0666-0617-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0518-0424-s006089 | forward | revenue | 3 | pending |
| line-2 | line-2-0518-0424-s006089 | reverse | revenue | 3 | pending |
| line-2 | line-2-0462-0372-s007792 | forward | revenue | 3 | pending |
| line-2 | line-2-0462-0372-s007792 | reverse | revenue | 3 | pending |
| line-2 | line-2-0386-0302-s010127 | forward | revenue | 3 | pending |
| line-2 | line-2-0386-0302-s010127 | reverse | revenue | 3 | pending |
| line-2 | line-2-0310-0231-s012457 | reverse | revenue | 2 | pending |
| line-2 | line-2-0310-0231-s012457 | reverse | spare | 1 | pending |
| line-2 | line-2-0666-0617-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0518-0424-s006089 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0005-0503-s000000 | forward | revenue | 6 | pending |
| line-3 | line-3-0184-0372-s007006 | forward | revenue | 6 | pending |
| line-3 | line-3-0184-0372-s007006 | reverse | revenue | 5 | pending |
| line-3 | line-3-0362-0236-s011985 | reverse | revenue | 5 | pending |
| line-3 | line-3-0184-0372-s007006 | reverse | spare | 1 | pending |
| line-3 | line-3-0362-0236-s011985 | reverse | spare | 1 | pending |
| line-3 | line-3-0005-0503-s000000 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**56 trainsets exceed the reference platform envelope**, requiring **2,744.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0008-0663-s014481 | 4 | 2 | 2 | 98.0 |
| line-1-0308-0440-s006030 | 10 | 2 | 8 | 392.0 |
| line-1-0415-0355-s003010 | 10 | 2 | 8 | 392.0 |
| line-1-0520-0272-s000000 | 5 | 2 | 3 | 147.0 |
| line-2-0310-0231-s012457 | 3 | 2 | 1 | 49.0 |
| line-2-0386-0302-s010127 | 6 | 2 | 4 | 196.0 |
| line-2-0462-0372-s007792 | 6 | 2 | 4 | 196.0 |
| line-2-0518-0424-s006089 | 7 | 2 | 5 | 245.0 |
| line-2-0666-0617-s000000 | 4 | 2 | 2 | 98.0 |
| line-3-0005-0503-s000000 | 7 | 2 | 5 | 245.0 |
| line-3-0184-0372-s007006 | 12 | 2 | 10 | 490.0 |
| line-3-0362-0236-s011985 | 6 | 2 | 4 | 196.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Rwanda/Huye/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
