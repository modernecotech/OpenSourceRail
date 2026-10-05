# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **28 trainsets at stations + 102 at depots = 130 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0370-0539-s000000 | line-1 | declared-depot | 18 | 1,071.0 | 4 |
| line-2-0647-1100-s000000 | line-2 | declared-depot | 40 | 2,380.0 | 7 |
| line-3-0354-0950-s018035 | line-3 | declared-depot | 44 | 2,618.0 | 8 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0370-0539-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0549-0552-s003688 | station | forward | revenue | 1 |
| line-1 | line-1-0549-0552-s003688 | station | reverse | revenue | 1 |
| line-1 | line-1-0640-0559-s005566 | station | forward | revenue | 1 |
| line-1 | line-1-0640-0559-s005566 | station | reverse | revenue | 1 |
| line-1 | line-1-0731-0566-s007444 | station | reverse | revenue | 2 |
| line-2 | line-2-0526-0378-s015824 | station | reverse | revenue | 2 |
| line-2 | line-2-0569-0546-s012108 | station | forward | revenue | 1 |
| line-2 | line-2-0569-0546-s012108 | station | reverse | revenue | 1 |
| line-2 | line-2-0594-0640-s010021 | station | forward | revenue | 1 |
| line-2 | line-2-0594-0640-s010021 | station | reverse | revenue | 1 |
| line-2 | line-2-0629-0776-s007011 | station | forward | revenue | 1 |
| line-2 | line-2-0629-0776-s007011 | station | reverse | revenue | 1 |
| line-2 | line-2-0647-1100-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0354-0950-s018035 | station | reverse | revenue | 2 |
| line-3 | line-3-0469-0756-s013185 | station | forward | revenue | 1 |
| line-3 | line-3-0469-0756-s013185 | station | reverse | revenue | 1 |
| line-3 | line-3-0568-0561-s008336 | station | forward | revenue | 1 |
| line-3 | line-3-0568-0561-s008336 | station | reverse | revenue | 1 |
| line-3 | line-3-0624-0453-s005665 | station | forward | revenue | 1 |
| line-3 | line-3-0624-0453-s005665 | station | reverse | revenue | 1 |
| line-3 | line-3-0740-0226-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0370-0539-s000000 | depot | — | revenue | 15 |
| line-1 | line-1-0370-0539-s000000 | depot | — | spare | 2 |
| line-1 | line-1-0370-0539-s000000 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0647-1100-s000000 | depot | — | revenue | 35 |
| line-2 | line-2-0647-1100-s000000 | depot | — | spare | 4 |
| line-2 | line-2-0647-1100-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0354-0950-s018035 | depot | — | revenue | 39 |
| line-3 | line-3-0354-0950-s018035 | depot | — | spare | 4 |
| line-3 | line-3-0354-0950-s018035 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/damanhur-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **130 trainsets at 14 stations**; largest initial station queue **14**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **117 revenue, 10 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **28 positions**; **102 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **14 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0370-0539-s000000 | forward | revenue | 4 | pending |
| line-1 | line-1-0549-0552-s003688 | forward | revenue | 4 | pending |
| line-1 | line-1-0549-0552-s003688 | reverse | revenue | 4 | pending |
| line-1 | line-1-0640-0559-s005566 | forward | revenue | 4 | pending |
| line-1 | line-1-0640-0559-s005566 | reverse | revenue | 4 | pending |
| line-1 | line-1-0731-0566-s007444 | reverse | revenue | 3 | pending |
| line-1 | line-1-0731-0566-s007444 | reverse | spare | 1 | pending |
| line-1 | line-1-0370-0539-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0549-0552-s003688 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0647-1100-s000000 | forward | revenue | 6 | pending |
| line-2 | line-2-0629-0776-s007011 | forward | revenue | 6 | pending |
| line-2 | line-2-0629-0776-s007011 | reverse | revenue | 6 | pending |
| line-2 | line-2-0594-0640-s010021 | forward | revenue | 6 | pending |
| line-2 | line-2-0594-0640-s010021 | reverse | revenue | 6 | pending |
| line-2 | line-2-0569-0546-s012108 | forward | revenue | 5 | pending |
| line-2 | line-2-0569-0546-s012108 | reverse | revenue | 5 | pending |
| line-2 | line-2-0526-0378-s015824 | reverse | revenue | 5 | pending |
| line-2 | line-2-0569-0546-s012108 | forward | spare | 1 | pending |
| line-2 | line-2-0569-0546-s012108 | reverse | spare | 1 | pending |
| line-2 | line-2-0526-0378-s015824 | reverse | spare | 1 | pending |
| line-2 | line-2-0647-1100-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0629-0776-s007011 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0740-0226-s000000 | forward | revenue | 7 | pending |
| line-3 | line-3-0624-0453-s005665 | forward | revenue | 6 | pending |
| line-3 | line-3-0624-0453-s005665 | reverse | revenue | 6 | pending |
| line-3 | line-3-0568-0561-s008336 | forward | revenue | 6 | pending |
| line-3 | line-3-0568-0561-s008336 | reverse | revenue | 6 | pending |
| line-3 | line-3-0469-0756-s013185 | forward | revenue | 6 | pending |
| line-3 | line-3-0469-0756-s013185 | reverse | revenue | 6 | pending |
| line-3 | line-3-0354-0950-s018035 | reverse | revenue | 6 | pending |
| line-3 | line-3-0624-0453-s005665 | forward | spare | 1 | pending |
| line-3 | line-3-0624-0453-s005665 | reverse | spare | 1 | pending |
| line-3 | line-3-0568-0561-s008336 | forward | spare | 1 | pending |
| line-3 | line-3-0568-0561-s008336 | reverse | spare | 1 | pending |
| line-3 | line-3-0469-0756-s013185 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**96 trainsets exceed the reference platform envelope**, requiring **5,712.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0370-0539-s000000 | 5 | 2 | 3 | 178.5 |
| line-1-0549-0552-s003688 | 9 | 4 | 5 | 297.5 |
| line-1-0640-0559-s005566 | 8 | 2 | 6 | 357.0 |
| line-1-0731-0566-s007444 | 4 | 2 | 2 | 119.0 |
| line-2-0526-0378-s015824 | 6 | 2 | 4 | 238.0 |
| line-2-0569-0546-s012108 | 12 | 4 | 8 | 476.0 |
| line-2-0594-0640-s010021 | 12 | 2 | 10 | 595.0 |
| line-2-0629-0776-s007011 | 13 | 2 | 11 | 654.5 |
| line-2-0647-1100-s000000 | 7 | 2 | 5 | 297.5 |
| line-3-0354-0950-s018035 | 6 | 2 | 4 | 238.0 |
| line-3-0469-0756-s013185 | 13 | 2 | 11 | 654.5 |
| line-3-0568-0561-s008336 | 14 | 4 | 10 | 595.0 |
| line-3-0624-0453-s005665 | 14 | 2 | 12 | 714.0 |
| line-3-0740-0226-s000000 | 7 | 2 | 5 | 297.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Egypt/Damanhur/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
