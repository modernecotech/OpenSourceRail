# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **36 trainsets at stations + 133 at depots = 169 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0216-0447-s000000 | line-1 | declared-depot | 34 | 2,023.0 | 7 |
| line-2-0674-0383-s000000 | line-2 | declared-depot | 40 | 2,380.0 | 8 |
| line-3-0085-0118-s022663 | line-3 | declared-depot | 59 | 3,510.5 | 10 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0216-0447-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0370-0519-s003805 | station | forward | revenue | 1 |
| line-1 | line-1-0370-0519-s003805 | station | reverse | revenue | 1 |
| line-1 | line-1-0436-0550-s005417 | station | forward | revenue | 1 |
| line-1 | line-1-0436-0550-s005417 | station | reverse | revenue | 1 |
| line-1 | line-1-0561-0609-s008430 | station | forward | revenue | 1 |
| line-1 | line-1-0561-0609-s008430 | station | reverse | revenue | 1 |
| line-1 | line-1-0684-0667-s011440 | station | forward | revenue | 1 |
| line-1 | line-1-0684-0667-s011440 | station | reverse | revenue | 1 |
| line-1 | line-1-0799-0721-s014281 | station | reverse | revenue | 2 |
| line-2 | line-2-0418-1069-s016754 | station | reverse | revenue | 2 |
| line-2 | line-2-0454-0841-s011381 | station | forward | revenue | 1 |
| line-2 | line-2-0454-0841-s011381 | station | reverse | revenue | 1 |
| line-2 | line-2-0506-0733-s008696 | station | forward | revenue | 1 |
| line-2 | line-2-0506-0733-s008696 | station | reverse | revenue | 1 |
| line-2 | line-2-0557-0625-s006020 | station | forward | revenue | 1 |
| line-2 | line-2-0557-0625-s006020 | station | reverse | revenue | 1 |
| line-2 | line-2-0616-0504-s003006 | station | forward | revenue | 1 |
| line-2 | line-2-0616-0504-s003006 | station | reverse | revenue | 1 |
| line-2 | line-2-0674-0383-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0085-0118-s022663 | station | reverse | revenue | 2 |
| line-3 | line-3-0416-0384-s013546 | station | forward | revenue | 1 |
| line-3 | line-3-0416-0384-s013546 | station | reverse | revenue | 1 |
| line-3 | line-3-0547-0471-s010029 | station | forward | revenue | 1 |
| line-3 | line-3-0547-0471-s010029 | station | reverse | revenue | 1 |
| line-3 | line-3-0659-0546-s007004 | station | forward | revenue | 1 |
| line-3 | line-3-0659-0546-s007004 | station | reverse | revenue | 1 |
| line-3 | line-3-0790-0633-s003511 | station | forward | revenue | 1 |
| line-3 | line-3-0790-0633-s003511 | station | reverse | revenue | 1 |
| line-3 | line-3-0919-0713-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0216-0447-s000000 | depot | — | revenue | 29 |
| line-1 | line-1-0216-0447-s000000 | depot | — | spare | 4 |
| line-1 | line-1-0216-0447-s000000 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0674-0383-s000000 | depot | — | revenue | 35 |
| line-2 | line-2-0674-0383-s000000 | depot | — | spare | 4 |
| line-2 | line-2-0674-0383-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0085-0118-s022663 | depot | — | revenue | 52 |
| line-3 | line-3-0085-0118-s022663 | depot | — | spare | 6 |
| line-3 | line-3-0085-0118-s022663 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/arusha-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **169 trainsets at 18 stations**; largest initial station queue **14**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **152 revenue, 14 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **36 positions**; **133 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **18 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0216-0447-s000000 | forward | revenue | 5 | pending |
| line-1 | line-1-0370-0519-s003805 | forward | revenue | 4 | pending |
| line-1 | line-1-0370-0519-s003805 | reverse | revenue | 4 | pending |
| line-1 | line-1-0436-0550-s005417 | forward | revenue | 4 | pending |
| line-1 | line-1-0436-0550-s005417 | reverse | revenue | 4 | pending |
| line-1 | line-1-0561-0609-s008430 | forward | revenue | 4 | pending |
| line-1 | line-1-0561-0609-s008430 | reverse | revenue | 4 | pending |
| line-1 | line-1-0684-0667-s011440 | forward | revenue | 4 | pending |
| line-1 | line-1-0684-0667-s011440 | reverse | revenue | 4 | pending |
| line-1 | line-1-0799-0721-s014281 | reverse | revenue | 4 | pending |
| line-1 | line-1-0370-0519-s003805 | forward | spare | 1 | pending |
| line-1 | line-1-0370-0519-s003805 | reverse | spare | 1 | pending |
| line-1 | line-1-0436-0550-s005417 | forward | spare | 1 | pending |
| line-1 | line-1-0436-0550-s005417 | reverse | spare | 1 | pending |
| line-1 | line-1-0561-0609-s008430 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0674-0383-s000000 | forward | revenue | 5 | pending |
| line-2 | line-2-0616-0504-s003006 | forward | revenue | 5 | pending |
| line-2 | line-2-0616-0504-s003006 | reverse | revenue | 5 | pending |
| line-2 | line-2-0557-0625-s006020 | forward | revenue | 5 | pending |
| line-2 | line-2-0557-0625-s006020 | reverse | revenue | 5 | pending |
| line-2 | line-2-0506-0733-s008696 | forward | revenue | 5 | pending |
| line-2 | line-2-0506-0733-s008696 | reverse | revenue | 5 | pending |
| line-2 | line-2-0454-0841-s011381 | forward | revenue | 4 | pending |
| line-2 | line-2-0454-0841-s011381 | reverse | revenue | 4 | pending |
| line-2 | line-2-0418-1069-s016754 | reverse | revenue | 4 | pending |
| line-2 | line-2-0454-0841-s011381 | forward | spare | 1 | pending |
| line-2 | line-2-0454-0841-s011381 | reverse | spare | 1 | pending |
| line-2 | line-2-0418-1069-s016754 | reverse | spare | 1 | pending |
| line-2 | line-2-0674-0383-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0616-0504-s003006 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0919-0713-s000000 | forward | revenue | 7 | pending |
| line-3 | line-3-0790-0633-s003511 | forward | revenue | 7 | pending |
| line-3 | line-3-0790-0633-s003511 | reverse | revenue | 7 | pending |
| line-3 | line-3-0659-0546-s007004 | forward | revenue | 7 | pending |
| line-3 | line-3-0659-0546-s007004 | reverse | revenue | 6 | pending |
| line-3 | line-3-0547-0471-s010029 | forward | revenue | 6 | pending |
| line-3 | line-3-0547-0471-s010029 | reverse | revenue | 6 | pending |
| line-3 | line-3-0416-0384-s013546 | forward | revenue | 6 | pending |
| line-3 | line-3-0416-0384-s013546 | reverse | revenue | 6 | pending |
| line-3 | line-3-0085-0118-s022663 | reverse | revenue | 6 | pending |
| line-3 | line-3-0659-0546-s007004 | reverse | spare | 1 | pending |
| line-3 | line-3-0547-0471-s010029 | forward | spare | 1 | pending |
| line-3 | line-3-0547-0471-s010029 | reverse | spare | 1 | pending |
| line-3 | line-3-0416-0384-s013546 | forward | spare | 1 | pending |
| line-3 | line-3-0416-0384-s013546 | reverse | spare | 1 | pending |
| line-3 | line-3-0085-0118-s022663 | reverse | spare | 1 | pending |
| line-3 | line-3-0919-0713-s000000 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**129 trainsets exceed the reference platform envelope**, requiring **7,675.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0216-0447-s000000 | 5 | 2 | 3 | 178.5 |
| line-1-0370-0519-s003805 | 10 | 2 | 8 | 476.0 |
| line-1-0436-0550-s005417 | 10 | 2 | 8 | 476.0 |
| line-1-0561-0609-s008430 | 9 | 4 | 5 | 297.5 |
| line-1-0684-0667-s011440 | 8 | 2 | 6 | 357.0 |
| line-1-0799-0721-s014281 | 4 | 2 | 2 | 119.0 |
| line-2-0418-1069-s016754 | 5 | 2 | 3 | 178.5 |
| line-2-0454-0841-s011381 | 10 | 2 | 8 | 476.0 |
| line-2-0506-0733-s008696 | 10 | 2 | 8 | 476.0 |
| line-2-0557-0625-s006020 | 10 | 4 | 6 | 357.0 |
| line-2-0616-0504-s003006 | 11 | 2 | 9 | 535.5 |
| line-2-0674-0383-s000000 | 6 | 2 | 4 | 238.0 |
| line-3-0085-0118-s022663 | 7 | 2 | 5 | 297.5 |
| line-3-0416-0384-s013546 | 14 | 2 | 12 | 714.0 |
| line-3-0547-0471-s010029 | 14 | 2 | 12 | 714.0 |
| line-3-0659-0546-s007004 | 14 | 2 | 12 | 714.0 |
| line-3-0790-0633-s003511 | 14 | 2 | 12 | 714.0 |
| line-3-0919-0713-s000000 | 8 | 2 | 6 | 357.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Tanzania/Arusha/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
