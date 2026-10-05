# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **30 trainsets at stations + 95 at depots = 125 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0702-0621-s014957 | line-1 | declared-depot | 34 | 2,023.0 | 7 |
| line-2-0325-0696-s000000 | line-2 | declared-depot | 28 | 1,666.0 | 5 |
| line-3-0134-0492-s000000 | line-3 | declared-depot | 33 | 1,963.5 | 6 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0110-0325-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0222-0383-s003010 | station | forward | revenue | 1 |
| line-1 | line-1-0222-0383-s003010 | station | reverse | revenue | 1 |
| line-1 | line-1-0362-0452-s006499 | station | forward | revenue | 1 |
| line-1 | line-1-0362-0452-s006499 | station | reverse | revenue | 1 |
| line-1 | line-1-0503-0523-s010013 | station | forward | revenue | 1 |
| line-1 | line-1-0503-0523-s010013 | station | reverse | revenue | 1 |
| line-1 | line-1-0603-0572-s012489 | station | forward | revenue | 1 |
| line-1 | line-1-0603-0572-s012489 | station | reverse | revenue | 1 |
| line-1 | line-1-0702-0621-s014957 | station | reverse | revenue | 2 |
| line-2 | line-2-0325-0696-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0410-0592-s003007 | station | forward | revenue | 1 |
| line-2 | line-2-0410-0592-s003007 | station | reverse | revenue | 1 |
| line-2 | line-2-0530-0445-s007245 | station | forward | revenue | 1 |
| line-2 | line-2-0530-0445-s007245 | station | reverse | revenue | 1 |
| line-2 | line-2-0649-0299-s011468 | station | reverse | revenue | 2 |
| line-3 | line-3-0134-0492-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0416-0572-s006919 | station | forward | revenue | 1 |
| line-3 | line-3-0416-0572-s006919 | station | reverse | revenue | 1 |
| line-3 | line-3-0535-0615-s009702 | station | forward | revenue | 1 |
| line-3 | line-3-0535-0615-s009702 | station | reverse | revenue | 1 |
| line-3 | line-3-0623-0648-s011759 | station | forward | revenue | 1 |
| line-3 | line-3-0623-0648-s011759 | station | reverse | revenue | 1 |
| line-3 | line-3-0710-0680-s013799 | station | reverse | revenue | 2 |
| line-1 | line-1-0702-0621-s014957 | depot | — | revenue | 29 |
| line-1 | line-1-0702-0621-s014957 | depot | — | spare | 4 |
| line-1 | line-1-0702-0621-s014957 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0325-0696-s000000 | depot | — | revenue | 24 |
| line-2 | line-2-0325-0696-s000000 | depot | — | spare | 3 |
| line-2 | line-2-0325-0696-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0134-0492-s000000 | depot | — | revenue | 29 |
| line-3 | line-3-0134-0492-s000000 | depot | — | spare | 3 |
| line-3 | line-3-0134-0492-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/aden-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **125 trainsets at 15 stations**; largest initial station queue **12**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **112 revenue, 10 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **30 positions**; **95 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **15 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0110-0325-s000000 | forward | revenue | 5 | pending |
| line-1 | line-1-0222-0383-s003010 | forward | revenue | 4 | pending |
| line-1 | line-1-0222-0383-s003010 | reverse | revenue | 4 | pending |
| line-1 | line-1-0362-0452-s006499 | forward | revenue | 4 | pending |
| line-1 | line-1-0362-0452-s006499 | reverse | revenue | 4 | pending |
| line-1 | line-1-0503-0523-s010013 | forward | revenue | 4 | pending |
| line-1 | line-1-0503-0523-s010013 | reverse | revenue | 4 | pending |
| line-1 | line-1-0603-0572-s012489 | forward | revenue | 4 | pending |
| line-1 | line-1-0603-0572-s012489 | reverse | revenue | 4 | pending |
| line-1 | line-1-0702-0621-s014957 | reverse | revenue | 4 | pending |
| line-1 | line-1-0222-0383-s003010 | forward | spare | 1 | pending |
| line-1 | line-1-0222-0383-s003010 | reverse | spare | 1 | pending |
| line-1 | line-1-0362-0452-s006499 | forward | spare | 1 | pending |
| line-1 | line-1-0362-0452-s006499 | reverse | spare | 1 | pending |
| line-1 | line-1-0503-0523-s010013 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0325-0696-s000000 | forward | revenue | 6 | pending |
| line-2 | line-2-0410-0592-s003007 | forward | revenue | 6 | pending |
| line-2 | line-2-0410-0592-s003007 | reverse | revenue | 5 | pending |
| line-2 | line-2-0530-0445-s007245 | forward | revenue | 5 | pending |
| line-2 | line-2-0530-0445-s007245 | reverse | revenue | 5 | pending |
| line-2 | line-2-0649-0299-s011468 | reverse | revenue | 5 | pending |
| line-2 | line-2-0410-0592-s003007 | reverse | spare | 1 | pending |
| line-2 | line-2-0530-0445-s007245 | forward | spare | 1 | pending |
| line-2 | line-2-0530-0445-s007245 | reverse | spare | 1 | pending |
| line-2 | line-2-0649-0299-s011468 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0134-0492-s000000 | forward | revenue | 5 | pending |
| line-3 | line-3-0416-0572-s006919 | forward | revenue | 5 | pending |
| line-3 | line-3-0416-0572-s006919 | reverse | revenue | 5 | pending |
| line-3 | line-3-0535-0615-s009702 | forward | revenue | 5 | pending |
| line-3 | line-3-0535-0615-s009702 | reverse | revenue | 5 | pending |
| line-3 | line-3-0623-0648-s011759 | forward | revenue | 5 | pending |
| line-3 | line-3-0623-0648-s011759 | reverse | revenue | 5 | pending |
| line-3 | line-3-0710-0680-s013799 | reverse | revenue | 4 | pending |
| line-3 | line-3-0710-0680-s013799 | reverse | spare | 1 | pending |
| line-3 | line-3-0134-0492-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0416-0572-s006919 | forward | spare | 1 | pending |
| line-3 | line-3-0416-0572-s006919 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**91 trainsets exceed the reference platform envelope**, requiring **5,414.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0110-0325-s000000 | 5 | 2 | 3 | 178.5 |
| line-1-0222-0383-s003010 | 10 | 2 | 8 | 476.0 |
| line-1-0362-0452-s006499 | 10 | 2 | 8 | 476.0 |
| line-1-0503-0523-s010013 | 9 | 2 | 7 | 416.5 |
| line-1-0603-0572-s012489 | 8 | 2 | 6 | 357.0 |
| line-1-0702-0621-s014957 | 4 | 2 | 2 | 119.0 |
| line-2-0325-0696-s000000 | 6 | 2 | 4 | 238.0 |
| line-2-0410-0592-s003007 | 12 | 4 | 8 | 476.0 |
| line-2-0530-0445-s007245 | 12 | 2 | 10 | 595.0 |
| line-2-0649-0299-s011468 | 6 | 2 | 4 | 238.0 |
| line-3-0134-0492-s000000 | 6 | 2 | 4 | 238.0 |
| line-3-0416-0572-s006919 | 12 | 4 | 8 | 476.0 |
| line-3-0535-0615-s009702 | 10 | 2 | 8 | 476.0 |
| line-3-0623-0648-s011759 | 10 | 2 | 8 | 476.0 |
| line-3-0710-0680-s013799 | 5 | 2 | 3 | 178.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Yemen/Aden/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
