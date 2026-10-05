# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **30 trainsets at stations + 43 at depots = 73 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0555-0342-s013233 | line-1 | declared-depot | 14 | 686.0 | 4 |
| line-2-0648-0466-s000000 | line-2 | declared-depot | 11 | 539.0 | 3 |
| line-3-0732-0095-s000000 | line-3 | declared-depot | 18 | 882.0 | 4 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0143-0732-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0274-0592-s004769 | station | forward | revenue | 1 |
| line-1 | line-1-0274-0592-s004769 | station | reverse | revenue | 1 |
| line-1 | line-1-0374-0503-s007787 | station | forward | revenue | 1 |
| line-1 | line-1-0374-0503-s007787 | station | reverse | revenue | 1 |
| line-1 | line-1-0434-0449-s009599 | station | forward | revenue | 1 |
| line-1 | line-1-0434-0449-s009599 | station | reverse | revenue | 1 |
| line-1 | line-1-0495-0396-s011422 | station | forward | revenue | 1 |
| line-1 | line-1-0495-0396-s011422 | station | reverse | revenue | 1 |
| line-1 | line-1-0555-0342-s013233 | station | reverse | revenue | 2 |
| line-2 | line-2-0277-0213-s009891 | station | reverse | revenue | 2 |
| line-2 | line-2-0362-0273-s007600 | station | forward | revenue | 1 |
| line-2 | line-2-0362-0273-s007600 | station | reverse | revenue | 1 |
| line-2 | line-2-0446-0333-s005318 | station | forward | revenue | 1 |
| line-2 | line-2-0446-0333-s005318 | station | reverse | revenue | 1 |
| line-2 | line-2-0531-0393-s003027 | station | forward | revenue | 1 |
| line-2 | line-2-0531-0393-s003027 | station | reverse | revenue | 1 |
| line-2 | line-2-0648-0466-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0315-0459-s012787 | station | reverse | revenue | 2 |
| line-3 | line-3-0413-0387-s010043 | station | forward | revenue | 1 |
| line-3 | line-3-0413-0387-s010043 | station | reverse | revenue | 1 |
| line-3 | line-3-0524-0305-s007027 | station | forward | revenue | 1 |
| line-3 | line-3-0524-0305-s007027 | station | reverse | revenue | 1 |
| line-3 | line-3-0732-0095-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0555-0342-s013233 | depot | — | revenue | 11 |
| line-1 | line-1-0555-0342-s013233 | depot | — | spare | 2 |
| line-1 | line-1-0555-0342-s013233 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0648-0466-s000000 | depot | — | revenue | 9 |
| line-2 | line-2-0648-0466-s000000 | depot | — | spare | 1 |
| line-2 | line-2-0648-0466-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0732-0095-s000000 | depot | — | revenue | 15 |
| line-3 | line-3-0732-0095-s000000 | depot | — | spare | 2 |
| line-3 | line-3-0732-0095-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/jinja-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **73 trainsets at 15 stations**; largest initial station queue **9**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **65 revenue, 5 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **30 positions**; **43 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **13 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0143-0732-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0274-0592-s004769 | forward | revenue | 3 | pending |
| line-1 | line-1-0274-0592-s004769 | reverse | revenue | 3 | pending |
| line-1 | line-1-0374-0503-s007787 | forward | revenue | 2 | pending |
| line-1 | line-1-0374-0503-s007787 | reverse | revenue | 2 | pending |
| line-1 | line-1-0434-0449-s009599 | forward | revenue | 2 | pending |
| line-1 | line-1-0434-0449-s009599 | reverse | revenue | 2 | pending |
| line-1 | line-1-0495-0396-s011422 | forward | revenue | 2 | pending |
| line-1 | line-1-0495-0396-s011422 | reverse | revenue | 2 | pending |
| line-1 | line-1-0555-0342-s013233 | reverse | revenue | 2 | pending |
| line-1 | line-1-0374-0503-s007787 | forward | spare | 1 | pending |
| line-1 | line-1-0374-0503-s007787 | reverse | spare | 1 | pending |
| line-1 | line-1-0434-0449-s009599 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0648-0466-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0531-0393-s003027 | forward | revenue | 3 | pending |
| line-2 | line-2-0531-0393-s003027 | reverse | revenue | 3 | pending |
| line-2 | line-2-0446-0333-s005318 | forward | revenue | 2 | pending |
| line-2 | line-2-0446-0333-s005318 | reverse | revenue | 2 | pending |
| line-2 | line-2-0362-0273-s007600 | forward | revenue | 2 | pending |
| line-2 | line-2-0362-0273-s007600 | reverse | revenue | 2 | pending |
| line-2 | line-2-0277-0213-s009891 | reverse | revenue | 2 | pending |
| line-2 | line-2-0446-0333-s005318 | forward | spare | 1 | pending |
| line-2 | line-2-0446-0333-s005318 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0732-0095-s000000 | forward | revenue | 4 | pending |
| line-3 | line-3-0524-0305-s007027 | forward | revenue | 4 | pending |
| line-3 | line-3-0524-0305-s007027 | reverse | revenue | 4 | pending |
| line-3 | line-3-0413-0387-s010043 | forward | revenue | 4 | pending |
| line-3 | line-3-0413-0387-s010043 | reverse | revenue | 4 | pending |
| line-3 | line-3-0315-0459-s012787 | reverse | revenue | 3 | pending |
| line-3 | line-3-0315-0459-s012787 | reverse | spare | 1 | pending |
| line-3 | line-3-0732-0095-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0524-0305-s007027 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**43 trainsets exceed the reference platform envelope**, requiring **2,107.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0143-0732-s000000 | 3 | 2 | 1 | 49.0 |
| line-1-0274-0592-s004769 | 6 | 2 | 4 | 196.0 |
| line-1-0374-0503-s007787 | 6 | 2 | 4 | 196.0 |
| line-1-0434-0449-s009599 | 5 | 2 | 3 | 147.0 |
| line-1-0495-0396-s011422 | 4 | 2 | 2 | 98.0 |
| line-1-0555-0342-s013233 | 2 | 2 | 0 | 0.0 |
| line-2-0277-0213-s009891 | 2 | 2 | 0 | 0.0 |
| line-2-0362-0273-s007600 | 4 | 2 | 2 | 98.0 |
| line-2-0446-0333-s005318 | 6 | 2 | 4 | 196.0 |
| line-2-0531-0393-s003027 | 6 | 2 | 4 | 196.0 |
| line-2-0648-0466-s000000 | 3 | 2 | 1 | 49.0 |
| line-3-0315-0459-s012787 | 4 | 2 | 2 | 98.0 |
| line-3-0413-0387-s010043 | 8 | 2 | 6 | 294.0 |
| line-3-0524-0305-s007027 | 9 | 2 | 7 | 343.0 |
| line-3-0732-0095-s000000 | 5 | 2 | 3 | 147.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Uganda/Jinja/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
