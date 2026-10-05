# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **30 trainsets at stations + 59 at depots = 89 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0583-0785-s010425 | line-1 | declared-depot | 22 | 1,309.0 | 5 |
| line-2-0321-0576-s000000 | line-2 | declared-depot | 18 | 1,071.0 | 4 |
| line-3-0345-0481-s000000 | line-3 | declared-depot | 19 | 1,130.5 | 4 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0481-0306-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0506-0425-s002587 | station | forward | revenue | 1 |
| line-1 | line-1-0506-0425-s002587 | station | reverse | revenue | 1 |
| line-1 | line-1-0525-0511-s004465 | station | forward | revenue | 1 |
| line-1 | line-1-0525-0511-s004465 | station | reverse | revenue | 1 |
| line-1 | line-1-0543-0598-s006354 | station | forward | revenue | 1 |
| line-1 | line-1-0543-0598-s006354 | station | reverse | revenue | 1 |
| line-1 | line-1-0563-0691-s008379 | station | forward | revenue | 1 |
| line-1 | line-1-0563-0691-s008379 | station | reverse | revenue | 1 |
| line-1 | line-1-0583-0785-s010425 | station | reverse | revenue | 2 |
| line-2 | line-2-0321-0576-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0466-0590-s003016 | station | forward | revenue | 1 |
| line-2 | line-2-0466-0590-s003016 | station | reverse | revenue | 1 |
| line-2 | line-2-0543-0598-s004622 | station | forward | revenue | 1 |
| line-2 | line-2-0543-0598-s004622 | station | reverse | revenue | 1 |
| line-2 | line-2-0637-0607-s006577 | station | forward | revenue | 1 |
| line-2 | line-2-0637-0607-s006577 | station | reverse | revenue | 1 |
| line-2 | line-2-0732-0616-s008551 | station | reverse | revenue | 2 |
| line-3 | line-3-0345-0481-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0506-0425-s003684 | station | forward | revenue | 1 |
| line-3 | line-3-0506-0425-s003684 | station | reverse | revenue | 1 |
| line-3 | line-3-0599-0393-s005821 | station | forward | revenue | 1 |
| line-3 | line-3-0599-0393-s005821 | station | reverse | revenue | 1 |
| line-3 | line-3-0692-0360-s007954 | station | reverse | revenue | 2 |
| line-1 | line-1-0583-0785-s010425 | depot | — | revenue | 18 |
| line-1 | line-1-0583-0785-s010425 | depot | — | spare | 3 |
| line-1 | line-1-0583-0785-s010425 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0321-0576-s000000 | depot | — | revenue | 15 |
| line-2 | line-2-0321-0576-s000000 | depot | — | spare | 2 |
| line-2 | line-2-0321-0576-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0345-0481-s000000 | depot | — | revenue | 16 |
| line-3 | line-3-0345-0481-s000000 | depot | — | spare | 2 |
| line-3 | line-3-0345-0481-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/oujda-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **89 trainsets at 15 stations**; largest initial station queue **10**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **79 revenue, 7 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **30 positions**; **59 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **15 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0481-0306-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0506-0425-s002587 | forward | revenue | 3 | pending |
| line-1 | line-1-0506-0425-s002587 | reverse | revenue | 3 | pending |
| line-1 | line-1-0525-0511-s004465 | forward | revenue | 3 | pending |
| line-1 | line-1-0525-0511-s004465 | reverse | revenue | 3 | pending |
| line-1 | line-1-0543-0598-s006354 | forward | revenue | 3 | pending |
| line-1 | line-1-0543-0598-s006354 | reverse | revenue | 3 | pending |
| line-1 | line-1-0563-0691-s008379 | forward | revenue | 3 | pending |
| line-1 | line-1-0563-0691-s008379 | reverse | revenue | 3 | pending |
| line-1 | line-1-0583-0785-s010425 | reverse | revenue | 3 | pending |
| line-1 | line-1-0481-0306-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0506-0425-s002587 | forward | spare | 1 | pending |
| line-1 | line-1-0506-0425-s002587 | reverse | spare | 1 | pending |
| line-1 | line-1-0525-0511-s004465 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0321-0576-s000000 | forward | revenue | 4 | pending |
| line-2 | line-2-0466-0590-s003016 | forward | revenue | 3 | pending |
| line-2 | line-2-0466-0590-s003016 | reverse | revenue | 3 | pending |
| line-2 | line-2-0543-0598-s004622 | forward | revenue | 3 | pending |
| line-2 | line-2-0543-0598-s004622 | reverse | revenue | 3 | pending |
| line-2 | line-2-0637-0607-s006577 | forward | revenue | 3 | pending |
| line-2 | line-2-0637-0607-s006577 | reverse | revenue | 3 | pending |
| line-2 | line-2-0732-0616-s008551 | reverse | revenue | 3 | pending |
| line-2 | line-2-0466-0590-s003016 | forward | spare | 1 | pending |
| line-2 | line-2-0466-0590-s003016 | reverse | spare | 1 | pending |
| line-2 | line-2-0543-0598-s004622 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0345-0481-s000000 | forward | revenue | 4 | pending |
| line-3 | line-3-0506-0425-s003684 | forward | revenue | 4 | pending |
| line-3 | line-3-0506-0425-s003684 | reverse | revenue | 4 | pending |
| line-3 | line-3-0599-0393-s005821 | forward | revenue | 4 | pending |
| line-3 | line-3-0599-0393-s005821 | reverse | revenue | 4 | pending |
| line-3 | line-3-0692-0360-s007954 | reverse | revenue | 4 | pending |
| line-3 | line-3-0345-0481-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0506-0425-s003684 | forward | spare | 1 | pending |
| line-3 | line-3-0506-0425-s003684 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**51 trainsets exceed the reference platform envelope**, requiring **3,034.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0481-0306-s000000 | 4 | 2 | 2 | 119.0 |
| line-1-0506-0425-s002587 | 8 | 4 | 4 | 238.0 |
| line-1-0525-0511-s004465 | 7 | 2 | 5 | 297.5 |
| line-1-0543-0598-s006354 | 6 | 4 | 2 | 119.0 |
| line-1-0563-0691-s008379 | 6 | 2 | 4 | 238.0 |
| line-1-0583-0785-s010425 | 3 | 2 | 1 | 59.5 |
| line-2-0321-0576-s000000 | 4 | 2 | 2 | 119.0 |
| line-2-0466-0590-s003016 | 8 | 2 | 6 | 357.0 |
| line-2-0543-0598-s004622 | 7 | 4 | 3 | 178.5 |
| line-2-0637-0607-s006577 | 6 | 2 | 4 | 238.0 |
| line-2-0732-0616-s008551 | 3 | 2 | 1 | 59.5 |
| line-3-0345-0481-s000000 | 5 | 2 | 3 | 178.5 |
| line-3-0506-0425-s003684 | 10 | 4 | 6 | 357.0 |
| line-3-0599-0393-s005821 | 8 | 2 | 6 | 357.0 |
| line-3-0692-0360-s007954 | 4 | 2 | 2 | 119.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/north-africa/Morocco/Oujda/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
