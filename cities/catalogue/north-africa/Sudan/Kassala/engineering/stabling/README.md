# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **22 trainsets at stations + 47 at depots = 69 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0752-0316-s008853 | line-1 | declared-depot | 21 | 1,249.5 | 4 |
| line-2-0561-0629-s000000 | line-2 | declared-depot | 11 | 654.5 | 3 |
| line-3-0533-0566-s000000 | line-3 | declared-depot | 15 | 892.5 | 4 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0422-0537-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0543-0456-s003267 | station | forward | revenue | 1 |
| line-1 | line-1-0543-0456-s003267 | station | reverse | revenue | 1 |
| line-1 | line-1-0752-0316-s008853 | station | reverse | revenue | 2 |
| line-2 | line-2-0533-0358-s005652 | station | reverse | revenue | 2 |
| line-2 | line-2-0543-0456-s003609 | station | forward | revenue | 1 |
| line-2 | line-2-0543-0456-s003609 | station | reverse | revenue | 1 |
| line-2 | line-2-0552-0547-s001715 | station | forward | revenue | 1 |
| line-2 | line-2-0552-0547-s001715 | station | reverse | revenue | 1 |
| line-2 | line-2-0561-0629-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0533-0566-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0551-0546-s000608 | station | forward | revenue | 1 |
| line-3 | line-3-0551-0546-s000608 | station | reverse | revenue | 1 |
| line-3 | line-3-0621-0464-s003003 | station | forward | revenue | 1 |
| line-3 | line-3-0621-0464-s003003 | station | reverse | revenue | 1 |
| line-3 | line-3-0718-0353-s006308 | station | reverse | revenue | 2 |
| line-1 | line-1-0752-0316-s008853 | depot | — | revenue | 18 |
| line-1 | line-1-0752-0316-s008853 | depot | — | spare | 2 |
| line-1 | line-1-0752-0316-s008853 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0561-0629-s000000 | depot | — | revenue | 9 |
| line-2 | line-2-0561-0629-s000000 | depot | — | spare | 1 |
| line-2 | line-2-0561-0629-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0533-0566-s000000 | depot | — | revenue | 12 |
| line-3 | line-3-0533-0566-s000000 | depot | — | spare | 2 |
| line-3 | line-3-0533-0566-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/kassala-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **69 trainsets at 11 stations**; largest initial station queue **14**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **61 revenue, 5 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **22 positions**; **47 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **11 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0422-0537-s000000 | forward | revenue | 6 | pending |
| line-1 | line-1-0543-0456-s003267 | forward | revenue | 6 | pending |
| line-1 | line-1-0543-0456-s003267 | reverse | revenue | 6 | pending |
| line-1 | line-1-0752-0316-s008853 | reverse | revenue | 6 | pending |
| line-1 | line-1-0422-0537-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0543-0456-s003267 | forward | spare | 1 | pending |
| line-1 | line-1-0543-0456-s003267 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0561-0629-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0552-0547-s001715 | forward | revenue | 3 | pending |
| line-2 | line-2-0552-0547-s001715 | reverse | revenue | 3 | pending |
| line-2 | line-2-0543-0456-s003609 | forward | revenue | 3 | pending |
| line-2 | line-2-0543-0456-s003609 | reverse | revenue | 3 | pending |
| line-2 | line-2-0533-0358-s005652 | reverse | revenue | 2 | pending |
| line-2 | line-2-0533-0358-s005652 | reverse | spare | 1 | pending |
| line-2 | line-2-0561-0629-s000000 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0533-0566-s000000 | forward | revenue | 4 | pending |
| line-3 | line-3-0551-0546-s000608 | forward | revenue | 4 | pending |
| line-3 | line-3-0551-0546-s000608 | reverse | revenue | 3 | pending |
| line-3 | line-3-0621-0464-s003003 | forward | revenue | 3 | pending |
| line-3 | line-3-0621-0464-s003003 | reverse | revenue | 3 | pending |
| line-3 | line-3-0718-0353-s006308 | reverse | revenue | 3 | pending |
| line-3 | line-3-0551-0546-s000608 | reverse | spare | 1 | pending |
| line-3 | line-3-0621-0464-s003003 | forward | spare | 1 | pending |
| line-3 | line-3-0621-0464-s003003 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**39 trainsets exceed the reference platform envelope**, requiring **2,320.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0422-0537-s000000 | 7 | 2 | 5 | 297.5 |
| line-1-0543-0456-s003267 | 14 | 4 | 10 | 595.0 |
| line-1-0752-0316-s008853 | 6 | 2 | 4 | 238.0 |
| line-2-0533-0358-s005652 | 3 | 2 | 1 | 59.5 |
| line-2-0543-0456-s003609 | 6 | 4 | 2 | 119.0 |
| line-2-0552-0547-s001715 | 6 | 4 | 2 | 119.0 |
| line-2-0561-0629-s000000 | 4 | 2 | 2 | 119.0 |
| line-3-0533-0566-s000000 | 4 | 2 | 2 | 119.0 |
| line-3-0551-0546-s000608 | 8 | 4 | 4 | 238.0 |
| line-3-0621-0464-s003003 | 8 | 2 | 6 | 357.0 |
| line-3-0718-0353-s006308 | 3 | 2 | 1 | 59.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/north-africa/Sudan/Kassala/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
