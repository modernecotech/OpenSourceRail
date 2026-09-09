# Station and depot overnight allocation

Plan: **20 trainsets at stations + 20 at depots = 40 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0215-0324-s006643 | line-1 | declared-depot | 8 | 392.0 | 6 |
| line-2-0270-0428-s005747 | line-2 | storage-at-existing-powered-service-point | 7 | 343.0 | 0 |
| line-3-0375-0363-s003276 | line-3 | storage-at-existing-powered-service-point | 5 | 245.0 | 0 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0215-0324-s006643 | station | reverse | revenue | 2 |
| line-1 | line-1-0300-0320-s004564 | station | forward | revenue | 1 |
| line-1 | line-1-0300-0320-s004564 | station | reverse | revenue | 1 |
| line-1 | line-1-0318-0457-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0369-0375-s002479 | station | forward | revenue | 1 |
| line-1 | line-1-0369-0375-s002479 | station | reverse | revenue | 1 |
| line-2 | line-2-0270-0428-s005747 | station | reverse | revenue | 2 |
| line-2 | line-2-0369-0375-s002392 | station | forward | revenue | 1 |
| line-2 | line-2-0369-0375-s002392 | station | reverse | revenue | 1 |
| line-2 | line-2-0462-0393-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0277-0363-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0345-0348-s001640 | station | forward | revenue | 1 |
| line-3 | line-3-0345-0348-s001640 | station | reverse | revenue | 1 |
| line-3 | line-3-0375-0363-s003276 | station | reverse | revenue | 2 |
| line-1 | line-1-0215-0324-s006643 | depot | — | revenue | 6 |
| line-1 | line-1-0215-0324-s006643 | depot | — | spare | 1 |
| line-1 | line-1-0215-0324-s006643 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0270-0428-s005747 | depot | — | revenue | 5 |
| line-2 | line-2-0270-0428-s005747 | depot | — | spare | 1 |
| line-2 | line-2-0270-0428-s005747 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0375-0363-s003276 | depot | — | revenue | 3 |
| line-3 | line-3-0375-0363-s003276 | depot | — | spare | 1 |
| line-3 | line-3-0375-0363-s003276 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/sumbawanga-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **40 trainsets at 10 stations**; largest initial station queue **6**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **34 revenue, 3 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **20 positions**; **20 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **8 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0318-0457-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0369-0375-s002479 | forward | revenue | 3 | pending |
| line-1 | line-1-0369-0375-s002479 | reverse | revenue | 2 | pending |
| line-1 | line-1-0300-0320-s004564 | forward | revenue | 2 | pending |
| line-1 | line-1-0300-0320-s004564 | reverse | revenue | 2 | pending |
| line-1 | line-1-0215-0324-s006643 | reverse | revenue | 2 | pending |
| line-1 | line-1-0369-0375-s002479 | reverse | spare | 1 | pending |
| line-1 | line-1-0300-0320-s004564 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0462-0393-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0369-0375-s002392 | forward | revenue | 3 | pending |
| line-2 | line-2-0369-0375-s002392 | reverse | revenue | 3 | pending |
| line-2 | line-2-0270-0428-s005747 | reverse | revenue | 2 | pending |
| line-2 | line-2-0270-0428-s005747 | reverse | spare | 1 | pending |
| line-2 | line-2-0462-0393-s000000 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0277-0363-s000000 | forward | revenue | 3 | pending |
| line-3 | line-3-0345-0348-s001640 | forward | revenue | 2 | pending |
| line-3 | line-3-0345-0348-s001640 | reverse | revenue | 2 | pending |
| line-3 | line-3-0375-0363-s003276 | reverse | revenue | 2 | pending |
| line-3 | line-3-0345-0348-s001640 | forward | spare | 1 | pending |
| line-3 | line-3-0345-0348-s001640 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**16 trainsets exceed the reference platform envelope**, requiring **784.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0215-0324-s006643 | 2 | 2 | 0 | 0.0 |
| line-1-0300-0320-s004564 | 5 | 2 | 3 | 147.0 |
| line-1-0318-0457-s000000 | 3 | 2 | 1 | 49.0 |
| line-1-0369-0375-s002479 | 6 | 4 | 2 | 98.0 |
| line-2-0270-0428-s005747 | 3 | 2 | 1 | 49.0 |
| line-2-0369-0375-s002392 | 6 | 4 | 2 | 98.0 |
| line-2-0462-0393-s000000 | 4 | 2 | 2 | 98.0 |
| line-3-0277-0363-s000000 | 3 | 2 | 1 | 49.0 |
| line-3-0345-0348-s001640 | 6 | 2 | 4 | 196.0 |
| line-3-0375-0363-s003276 | 2 | 2 | 0 | 0.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Tanzania/Sumbawanga/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
