# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **32 trainsets at stations + 40 at depots = 72 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0040-0699-s000000 | line-1 | declared-depot | 14 | 686.0 | 4 |
| line-2-0437-0275-s000000 | line-2 | declared-depot | 6 | 294.0 | 2 |
| line-3-0000-0751-s016402 | line-3 | declared-depot | 20 | 980.0 | 5 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0040-0699-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0127-0596-s003172 | station | forward | revenue | 1 |
| line-1 | line-1-0127-0596-s003172 | station | reverse | revenue | 1 |
| line-1 | line-1-0171-0513-s005244 | station | forward | revenue | 1 |
| line-1 | line-1-0171-0513-s005244 | station | reverse | revenue | 1 |
| line-1 | line-1-0207-0443-s007012 | station | forward | revenue | 1 |
| line-1 | line-1-0207-0443-s007012 | station | reverse | revenue | 1 |
| line-1 | line-1-0247-0365-s008927 | station | forward | revenue | 1 |
| line-1 | line-1-0247-0365-s008927 | station | reverse | revenue | 1 |
| line-1 | line-1-0286-0290-s010832 | station | forward | revenue | 1 |
| line-1 | line-1-0286-0290-s010832 | station | reverse | revenue | 1 |
| line-1 | line-1-0323-0219-s012594 | station | reverse | revenue | 2 |
| line-2 | line-2-0222-0297-s004506 | station | reverse | revenue | 2 |
| line-2 | line-2-0286-0290-s003156 | station | forward | revenue | 1 |
| line-2 | line-2-0286-0290-s003156 | station | reverse | revenue | 1 |
| line-2 | line-2-0437-0275-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0000-0751-s016402 | station | reverse | revenue | 2 |
| line-3 | line-3-0127-0596-s010889 | station | forward | revenue | 1 |
| line-3 | line-3-0127-0596-s010889 | station | reverse | revenue | 1 |
| line-3 | line-3-0171-0513-s007979 | station | forward | revenue | 1 |
| line-3 | line-3-0171-0513-s007979 | station | reverse | revenue | 1 |
| line-3 | line-3-0207-0443-s005579 | station | forward | revenue | 1 |
| line-3 | line-3-0207-0443-s005579 | station | reverse | revenue | 1 |
| line-3 | line-3-0322-0461-s003014 | station | forward | revenue | 1 |
| line-3 | line-3-0322-0461-s003014 | station | reverse | revenue | 1 |
| line-3 | line-3-0433-0385-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0040-0699-s000000 | depot | — | revenue | 11 |
| line-1 | line-1-0040-0699-s000000 | depot | — | spare | 2 |
| line-1 | line-1-0040-0699-s000000 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0437-0275-s000000 | depot | — | revenue | 4 |
| line-2 | line-2-0437-0275-s000000 | depot | — | spare | 1 |
| line-2 | line-2-0437-0275-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0000-0751-s016402 | depot | — | revenue | 17 |
| line-3 | line-3-0000-0751-s016402 | depot | — | spare | 2 |
| line-3 | line-3-0000-0751-s016402 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/entebbe-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **72 trainsets at 16 stations**; largest initial station queue **7**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **64 revenue, 5 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **32 positions**; **40 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **15 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0040-0699-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0127-0596-s003172 | forward | revenue | 2 | pending |
| line-1 | line-1-0127-0596-s003172 | reverse | revenue | 2 | pending |
| line-1 | line-1-0171-0513-s005244 | forward | revenue | 2 | pending |
| line-1 | line-1-0171-0513-s005244 | reverse | revenue | 2 | pending |
| line-1 | line-1-0207-0443-s007012 | forward | revenue | 2 | pending |
| line-1 | line-1-0207-0443-s007012 | reverse | revenue | 2 | pending |
| line-1 | line-1-0247-0365-s008927 | forward | revenue | 2 | pending |
| line-1 | line-1-0247-0365-s008927 | reverse | revenue | 2 | pending |
| line-1 | line-1-0286-0290-s010832 | forward | revenue | 2 | pending |
| line-1 | line-1-0286-0290-s010832 | reverse | revenue | 2 | pending |
| line-1 | line-1-0323-0219-s012594 | reverse | revenue | 2 | pending |
| line-1 | line-1-0127-0596-s003172 | forward | spare | 1 | pending |
| line-1 | line-1-0127-0596-s003172 | reverse | spare | 1 | pending |
| line-1 | line-1-0171-0513-s005244 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0437-0275-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0286-0290-s003156 | forward | revenue | 3 | pending |
| line-2 | line-2-0286-0290-s003156 | reverse | revenue | 2 | pending |
| line-2 | line-2-0222-0297-s004506 | reverse | revenue | 2 | pending |
| line-2 | line-2-0286-0290-s003156 | reverse | spare | 1 | pending |
| line-2 | line-2-0222-0297-s004506 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0433-0385-s000000 | forward | revenue | 3 | pending |
| line-3 | line-3-0322-0461-s003014 | forward | revenue | 3 | pending |
| line-3 | line-3-0322-0461-s003014 | reverse | revenue | 3 | pending |
| line-3 | line-3-0207-0443-s005579 | forward | revenue | 3 | pending |
| line-3 | line-3-0207-0443-s005579 | reverse | revenue | 3 | pending |
| line-3 | line-3-0171-0513-s007979 | forward | revenue | 3 | pending |
| line-3 | line-3-0171-0513-s007979 | reverse | revenue | 3 | pending |
| line-3 | line-3-0127-0596-s010889 | forward | revenue | 3 | pending |
| line-3 | line-3-0127-0596-s010889 | reverse | revenue | 3 | pending |
| line-3 | line-3-0000-0751-s016402 | reverse | revenue | 2 | pending |
| line-3 | line-3-0000-0751-s016402 | reverse | spare | 1 | pending |
| line-3 | line-3-0433-0385-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0322-0461-s003014 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**24 trainsets exceed the reference platform envelope**, requiring **1,176.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0040-0699-s000000 | 3 | 2 | 1 | 49.0 |
| line-1-0127-0596-s003172 | 6 | 4 | 2 | 98.0 |
| line-1-0171-0513-s005244 | 5 | 4 | 1 | 49.0 |
| line-1-0207-0443-s007012 | 4 | 4 | 0 | 0.0 |
| line-1-0247-0365-s008927 | 4 | 2 | 2 | 98.0 |
| line-1-0286-0290-s010832 | 4 | 4 | 0 | 0.0 |
| line-1-0323-0219-s012594 | 2 | 2 | 0 | 0.0 |
| line-2-0222-0297-s004506 | 3 | 2 | 1 | 49.0 |
| line-2-0286-0290-s003156 | 6 | 4 | 2 | 98.0 |
| line-2-0437-0275-s000000 | 3 | 2 | 1 | 49.0 |
| line-3-0000-0751-s016402 | 3 | 2 | 1 | 49.0 |
| line-3-0127-0596-s010889 | 6 | 4 | 2 | 98.0 |
| line-3-0171-0513-s007979 | 6 | 4 | 2 | 98.0 |
| line-3-0207-0443-s005579 | 6 | 4 | 2 | 98.0 |
| line-3-0322-0461-s003014 | 7 | 2 | 5 | 245.0 |
| line-3-0433-0385-s000000 | 4 | 2 | 2 | 98.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Uganda/Entebbe/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
