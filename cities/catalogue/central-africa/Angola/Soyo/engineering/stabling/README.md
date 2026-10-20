# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **24 trainsets at stations + 40 at depots = 64 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0319-0148-s000000 | line-1 | declared-depot | 12 | 588.0 | 3 |
| line-2-0593-0351-s000000 | line-2 | declared-depot | 6 | 294.0 | 2 |
| line-3-0744-0445-s010159 | line-3 | declared-depot | 15 | 735.0 | 3 |
| line-4-0422-0396-s000000 | line-4 | declared-depot | 7 | 343.0 | 2 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0319-0148-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0325-0276-s003004 | station | forward | revenue | 1 |
| line-1 | line-1-0325-0276-s003004 | station | reverse | revenue | 1 |
| line-1 | line-1-0422-0396-s006658 | station | forward | revenue | 1 |
| line-1 | line-1-0422-0396-s006658 | station | reverse | revenue | 1 |
| line-1 | line-1-0531-0372-s009374 | station | reverse | revenue | 2 |
| line-2 | line-2-0474-0480-s003906 | station | reverse | revenue | 2 |
| line-2 | line-2-0572-0374-s000681 | station | forward | revenue | 1 |
| line-2 | line-2-0572-0374-s000681 | station | reverse | revenue | 1 |
| line-2 | line-2-0593-0351-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0340-0286-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0572-0374-s005439 | station | forward | revenue | 1 |
| line-3 | line-3-0572-0374-s005439 | station | reverse | revenue | 1 |
| line-3 | line-3-0744-0445-s010159 | station | reverse | revenue | 2 |
| line-4 | line-4-0313-0513-s004550 | station | reverse | revenue | 2 |
| line-4 | line-4-0422-0396-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0319-0148-s000000 | depot | — | revenue | 10 |
| line-1 | line-1-0319-0148-s000000 | depot | — | spare | 1 |
| line-1 | line-1-0319-0148-s000000 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0593-0351-s000000 | depot | — | revenue | 4 |
| line-2 | line-2-0593-0351-s000000 | depot | — | spare | 1 |
| line-2 | line-2-0593-0351-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0744-0445-s010159 | depot | — | revenue | 13 |
| line-3 | line-3-0744-0445-s010159 | depot | — | spare | 1 |
| line-3 | line-3-0744-0445-s010159 | depot | — | cold_reserve | 1 |
| line-4 | line-4-0422-0396-s000000 | depot | — | revenue | 5 |
| line-4 | line-4-0422-0396-s000000 | depot | — | spare | 1 |
| line-4 | line-4-0422-0396-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/soyo-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **64 trainsets at 12 stations**; largest initial station queue **10**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **56 revenue, 4 spare, 4 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **24 positions**; **40 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **12 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0319-0148-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0325-0276-s003004 | forward | revenue | 3 | pending |
| line-1 | line-1-0325-0276-s003004 | reverse | revenue | 3 | pending |
| line-1 | line-1-0422-0396-s006658 | forward | revenue | 3 | pending |
| line-1 | line-1-0422-0396-s006658 | reverse | revenue | 3 | pending |
| line-1 | line-1-0531-0372-s009374 | reverse | revenue | 3 | pending |
| line-1 | line-1-0319-0148-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0325-0276-s003004 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0593-0351-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0572-0374-s000681 | forward | revenue | 3 | pending |
| line-2 | line-2-0572-0374-s000681 | reverse | revenue | 2 | pending |
| line-2 | line-2-0474-0480-s003906 | reverse | revenue | 2 | pending |
| line-2 | line-2-0572-0374-s000681 | reverse | spare | 1 | pending |
| line-2 | line-2-0474-0480-s003906 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0340-0286-s000000 | forward | revenue | 5 | pending |
| line-3 | line-3-0572-0374-s005439 | forward | revenue | 5 | pending |
| line-3 | line-3-0572-0374-s005439 | reverse | revenue | 5 | pending |
| line-3 | line-3-0744-0445-s010159 | reverse | revenue | 4 | pending |
| line-3 | line-3-0744-0445-s010159 | reverse | spare | 1 | pending |
| line-3 | line-3-0340-0286-s000000 | forward | cold_reserve | 1 | pending |
| line-4 | line-4-0422-0396-s000000 | forward | revenue | 5 | pending |
| line-4 | line-4-0313-0513-s004550 | reverse | revenue | 4 | pending |
| line-4 | line-4-0313-0513-s004550 | reverse | spare | 1 | pending |
| line-4 | line-4-0422-0396-s000000 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**32 trainsets exceed the reference platform envelope**, requiring **1,568.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0319-0148-s000000 | 4 | 2 | 2 | 98.0 |
| line-1-0325-0276-s003004 | 7 | 4 | 3 | 147.0 |
| line-1-0422-0396-s006658 | 6 | 4 | 2 | 98.0 |
| line-1-0531-0372-s009374 | 3 | 2 | 1 | 49.0 |
| line-2-0474-0480-s003906 | 3 | 2 | 1 | 49.0 |
| line-2-0572-0374-s000681 | 6 | 4 | 2 | 98.0 |
| line-2-0593-0351-s000000 | 3 | 2 | 1 | 49.0 |
| line-3-0340-0286-s000000 | 6 | 2 | 4 | 196.0 |
| line-3-0572-0374-s005439 | 10 | 4 | 6 | 294.0 |
| line-3-0744-0445-s010159 | 5 | 2 | 3 | 147.0 |
| line-4-0313-0513-s004550 | 5 | 2 | 3 | 147.0 |
| line-4-0422-0396-s000000 | 6 | 2 | 4 | 196.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/central-africa/Angola/Soyo/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
