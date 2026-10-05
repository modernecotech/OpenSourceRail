# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **46 trainsets at stations + 110 at depots = 156 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0702-0621-s020196 | line-1 | declared-depot | 47 | 2,796.5 | 9 |
| line-2-0325-0696-s000000 | line-2 | declared-depot | 31 | 1,844.5 | 7 |
| line-3-0134-0492-s000000 | line-3 | declared-depot | 32 | 1,904.0 | 7 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0110-0325-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0222-0383-s003010 | station | forward | revenue | 1 |
| line-1 | line-1-0222-0383-s003010 | station | reverse | revenue | 1 |
| line-1 | line-1-0276-0391-s006034 | station | forward | revenue | 1 |
| line-1 | line-1-0276-0391-s006034 | station | reverse | revenue | 1 |
| line-1 | line-1-0297-0528-s010118 | station | forward | revenue | 1 |
| line-1 | line-1-0297-0528-s010118 | station | reverse | revenue | 1 |
| line-1 | line-1-0413-0571-s012794 | station | forward | revenue | 1 |
| line-1 | line-1-0413-0571-s012794 | station | reverse | revenue | 1 |
| line-1 | line-1-0427-0571-s013074 | station | forward | revenue | 1 |
| line-1 | line-1-0427-0571-s013074 | station | reverse | revenue | 1 |
| line-1 | line-1-0495-0563-s014501 | station | forward | revenue | 1 |
| line-1 | line-1-0495-0563-s014501 | station | reverse | revenue | 1 |
| line-1 | line-1-0569-0555-s016896 | station | forward | revenue | 1 |
| line-1 | line-1-0569-0555-s016896 | station | reverse | revenue | 1 |
| line-1 | line-1-0702-0621-s020196 | station | reverse | revenue | 2 |
| line-2 | line-2-0325-0696-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0424-0575-s003498 | station | forward | revenue | 1 |
| line-2 | line-2-0424-0575-s003498 | station | reverse | revenue | 1 |
| line-2 | line-2-0427-0571-s003603 | station | forward | revenue | 1 |
| line-2 | line-2-0427-0571-s003603 | station | reverse | revenue | 1 |
| line-2 | line-2-0495-0563-s005636 | station | forward | revenue | 1 |
| line-2 | line-2-0495-0563-s005636 | station | reverse | revenue | 1 |
| line-2 | line-2-0569-0555-s007414 | station | forward | revenue | 1 |
| line-2 | line-2-0569-0555-s007414 | station | reverse | revenue | 1 |
| line-2 | line-2-0593-0492-s009037 | station | forward | revenue | 1 |
| line-2 | line-2-0593-0492-s009037 | station | reverse | revenue | 1 |
| line-2 | line-2-0649-0299-s013690 | station | reverse | revenue | 2 |
| line-3 | line-3-0134-0492-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0297-0528-s004128 | station | forward | revenue | 1 |
| line-3 | line-3-0297-0528-s004128 | station | reverse | revenue | 1 |
| line-3 | line-3-0413-0571-s006839 | station | forward | revenue | 1 |
| line-3 | line-3-0413-0571-s006839 | station | reverse | revenue | 1 |
| line-3 | line-3-0424-0575-s007104 | station | forward | revenue | 1 |
| line-3 | line-3-0424-0575-s007104 | station | reverse | revenue | 1 |
| line-3 | line-3-0535-0615-s009702 | station | forward | revenue | 1 |
| line-3 | line-3-0535-0615-s009702 | station | reverse | revenue | 1 |
| line-3 | line-3-0623-0648-s011759 | station | forward | revenue | 1 |
| line-3 | line-3-0623-0648-s011759 | station | reverse | revenue | 1 |
| line-3 | line-3-0710-0680-s013799 | station | reverse | revenue | 2 |
| line-1 | line-1-0702-0621-s020196 | depot | — | revenue | 41 |
| line-1 | line-1-0702-0621-s020196 | depot | — | spare | 5 |
| line-1 | line-1-0702-0621-s020196 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0325-0696-s000000 | depot | — | revenue | 26 |
| line-2 | line-2-0325-0696-s000000 | depot | — | spare | 4 |
| line-2 | line-2-0325-0696-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0134-0492-s000000 | depot | — | revenue | 27 |
| line-3 | line-3-0134-0492-s000000 | depot | — | spare | 4 |
| line-3 | line-3-0134-0492-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/aden-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **156 trainsets at 23 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **140 revenue, 13 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **46 positions**; **110 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **23 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0110-0325-s000000 | forward | revenue | 4 | pending |
| line-1 | line-1-0222-0383-s003010 | forward | revenue | 4 | pending |
| line-1 | line-1-0222-0383-s003010 | reverse | revenue | 4 | pending |
| line-1 | line-1-0276-0391-s006034 | forward | revenue | 4 | pending |
| line-1 | line-1-0276-0391-s006034 | reverse | revenue | 4 | pending |
| line-1 | line-1-0297-0528-s010118 | forward | revenue | 4 | pending |
| line-1 | line-1-0297-0528-s010118 | reverse | revenue | 4 | pending |
| line-1 | line-1-0413-0571-s012794 | forward | revenue | 4 | pending |
| line-1 | line-1-0413-0571-s012794 | reverse | revenue | 4 | pending |
| line-1 | line-1-0427-0571-s013074 | forward | revenue | 4 | pending |
| line-1 | line-1-0427-0571-s013074 | reverse | revenue | 4 | pending |
| line-1 | line-1-0495-0563-s014501 | forward | revenue | 3 | pending |
| line-1 | line-1-0495-0563-s014501 | reverse | revenue | 3 | pending |
| line-1 | line-1-0569-0555-s016896 | forward | revenue | 3 | pending |
| line-1 | line-1-0569-0555-s016896 | reverse | revenue | 3 | pending |
| line-1 | line-1-0702-0621-s020196 | reverse | revenue | 3 | pending |
| line-1 | line-1-0495-0563-s014501 | forward | spare | 1 | pending |
| line-1 | line-1-0495-0563-s014501 | reverse | spare | 1 | pending |
| line-1 | line-1-0569-0555-s016896 | forward | spare | 1 | pending |
| line-1 | line-1-0569-0555-s016896 | reverse | spare | 1 | pending |
| line-1 | line-1-0702-0621-s020196 | reverse | spare | 1 | pending |
| line-1 | line-1-0110-0325-s000000 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0325-0696-s000000 | forward | revenue | 4 | pending |
| line-2 | line-2-0424-0575-s003498 | forward | revenue | 4 | pending |
| line-2 | line-2-0424-0575-s003498 | reverse | revenue | 4 | pending |
| line-2 | line-2-0427-0571-s003603 | forward | revenue | 4 | pending |
| line-2 | line-2-0427-0571-s003603 | reverse | revenue | 3 | pending |
| line-2 | line-2-0495-0563-s005636 | forward | revenue | 3 | pending |
| line-2 | line-2-0495-0563-s005636 | reverse | revenue | 3 | pending |
| line-2 | line-2-0569-0555-s007414 | forward | revenue | 3 | pending |
| line-2 | line-2-0569-0555-s007414 | reverse | revenue | 3 | pending |
| line-2 | line-2-0593-0492-s009037 | forward | revenue | 3 | pending |
| line-2 | line-2-0593-0492-s009037 | reverse | revenue | 3 | pending |
| line-2 | line-2-0649-0299-s013690 | reverse | revenue | 3 | pending |
| line-2 | line-2-0427-0571-s003603 | reverse | spare | 1 | pending |
| line-2 | line-2-0495-0563-s005636 | forward | spare | 1 | pending |
| line-2 | line-2-0495-0563-s005636 | reverse | spare | 1 | pending |
| line-2 | line-2-0569-0555-s007414 | forward | spare | 1 | pending |
| line-2 | line-2-0569-0555-s007414 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0134-0492-s000000 | forward | revenue | 4 | pending |
| line-3 | line-3-0297-0528-s004128 | forward | revenue | 4 | pending |
| line-3 | line-3-0297-0528-s004128 | reverse | revenue | 4 | pending |
| line-3 | line-3-0413-0571-s006839 | forward | revenue | 4 | pending |
| line-3 | line-3-0413-0571-s006839 | reverse | revenue | 4 | pending |
| line-3 | line-3-0424-0575-s007104 | forward | revenue | 3 | pending |
| line-3 | line-3-0424-0575-s007104 | reverse | revenue | 3 | pending |
| line-3 | line-3-0535-0615-s009702 | forward | revenue | 3 | pending |
| line-3 | line-3-0535-0615-s009702 | reverse | revenue | 3 | pending |
| line-3 | line-3-0623-0648-s011759 | forward | revenue | 3 | pending |
| line-3 | line-3-0623-0648-s011759 | reverse | revenue | 3 | pending |
| line-3 | line-3-0710-0680-s013799 | reverse | revenue | 3 | pending |
| line-3 | line-3-0424-0575-s007104 | forward | spare | 1 | pending |
| line-3 | line-3-0424-0575-s007104 | reverse | spare | 1 | pending |
| line-3 | line-3-0535-0615-s009702 | forward | spare | 1 | pending |
| line-3 | line-3-0535-0615-s009702 | reverse | spare | 1 | pending |
| line-3 | line-3-0623-0648-s011759 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**86 trainsets exceed the reference platform envelope**, requiring **5,117.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0110-0325-s000000 | 5 | 2 | 3 | 178.5 |
| line-1-0222-0383-s003010 | 8 | 2 | 6 | 357.0 |
| line-1-0276-0391-s006034 | 8 | 2 | 6 | 357.0 |
| line-1-0297-0528-s010118 | 8 | 4 | 4 | 238.0 |
| line-1-0413-0571-s012794 | 8 | 4 | 4 | 238.0 |
| line-1-0427-0571-s013074 | 8 | 4 | 4 | 238.0 |
| line-1-0495-0563-s014501 | 8 | 4 | 4 | 238.0 |
| line-1-0569-0555-s016896 | 8 | 4 | 4 | 238.0 |
| line-1-0702-0621-s020196 | 4 | 2 | 2 | 119.0 |
| line-2-0325-0696-s000000 | 4 | 2 | 2 | 119.0 |
| line-2-0424-0575-s003498 | 8 | 4 | 4 | 238.0 |
| line-2-0427-0571-s003603 | 8 | 4 | 4 | 238.0 |
| line-2-0495-0563-s005636 | 8 | 4 | 4 | 238.0 |
| line-2-0569-0555-s007414 | 8 | 4 | 4 | 238.0 |
| line-2-0593-0492-s009037 | 6 | 2 | 4 | 238.0 |
| line-2-0649-0299-s013690 | 3 | 2 | 1 | 59.5 |
| line-3-0134-0492-s000000 | 4 | 2 | 2 | 119.0 |
| line-3-0297-0528-s004128 | 8 | 4 | 4 | 238.0 |
| line-3-0413-0571-s006839 | 8 | 4 | 4 | 238.0 |
| line-3-0424-0575-s007104 | 8 | 4 | 4 | 238.0 |
| line-3-0535-0615-s009702 | 8 | 2 | 6 | 357.0 |
| line-3-0623-0648-s011759 | 7 | 2 | 5 | 297.5 |
| line-3-0710-0680-s013799 | 3 | 2 | 1 | 59.5 |

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
