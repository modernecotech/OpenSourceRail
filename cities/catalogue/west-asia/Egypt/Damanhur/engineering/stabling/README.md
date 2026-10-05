# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **30 trainsets at stations + 102 at depots = 132 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0370-0539-s000000 | line-1 | declared-depot | 18 | 1,071.0 | 4 |
| line-2-0647-1100-s000000 | line-2 | declared-depot | 40 | 2,380.0 | 8 |
| line-3-0354-0950-s018310 | line-3 | declared-depot | 44 | 2,618.0 | 8 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0370-0539-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0470-0547-s002066 | station | forward | revenue | 1 |
| line-1 | line-1-0470-0547-s002066 | station | reverse | revenue | 1 |
| line-1 | line-1-0571-0554-s004144 | station | forward | revenue | 1 |
| line-1 | line-1-0571-0554-s004144 | station | reverse | revenue | 1 |
| line-1 | line-1-0731-0566-s007444 | station | reverse | revenue | 2 |
| line-2 | line-2-0526-0378-s016176 | station | reverse | revenue | 2 |
| line-2 | line-2-0549-0466-s014225 | station | forward | revenue | 1 |
| line-2 | line-2-0549-0466-s014225 | station | reverse | revenue | 1 |
| line-2 | line-2-0571-0554-s012283 | station | forward | revenue | 1 |
| line-2 | line-2-0571-0554-s012283 | station | reverse | revenue | 1 |
| line-2 | line-2-0598-0656-s010019 | station | forward | revenue | 1 |
| line-2 | line-2-0598-0656-s010019 | station | reverse | revenue | 1 |
| line-2 | line-2-0633-0792-s007009 | station | forward | revenue | 1 |
| line-2 | line-2-0633-0792-s007009 | station | reverse | revenue | 1 |
| line-2 | line-2-0647-1100-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0354-0950-s018310 | station | reverse | revenue | 2 |
| line-3 | line-3-0468-0758-s013233 | station | forward | revenue | 1 |
| line-3 | line-3-0468-0758-s013233 | station | reverse | revenue | 1 |
| line-3 | line-3-0572-0554-s008163 | station | forward | revenue | 1 |
| line-3 | line-3-0572-0554-s008163 | station | reverse | revenue | 1 |
| line-3 | line-3-0624-0453-s005665 | station | forward | revenue | 1 |
| line-3 | line-3-0624-0453-s005665 | station | reverse | revenue | 1 |
| line-3 | line-3-0740-0226-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0370-0539-s000000 | depot | — | revenue | 15 |
| line-1 | line-1-0370-0539-s000000 | depot | — | spare | 2 |
| line-1 | line-1-0370-0539-s000000 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0647-1100-s000000 | depot | — | revenue | 35 |
| line-2 | line-2-0647-1100-s000000 | depot | — | spare | 4 |
| line-2 | line-2-0647-1100-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0354-0950-s018310 | depot | — | revenue | 39 |
| line-3 | line-3-0354-0950-s018310 | depot | — | spare | 4 |
| line-3 | line-3-0354-0950-s018310 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/damanhur-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **132 trainsets at 15 stations**; largest initial station queue **14**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **119 revenue, 10 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **30 positions**; **102 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **15 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0370-0539-s000000 | forward | revenue | 4 | pending |
| line-1 | line-1-0470-0547-s002066 | forward | revenue | 4 | pending |
| line-1 | line-1-0470-0547-s002066 | reverse | revenue | 4 | pending |
| line-1 | line-1-0571-0554-s004144 | forward | revenue | 4 | pending |
| line-1 | line-1-0571-0554-s004144 | reverse | revenue | 4 | pending |
| line-1 | line-1-0731-0566-s007444 | reverse | revenue | 3 | pending |
| line-1 | line-1-0731-0566-s007444 | reverse | spare | 1 | pending |
| line-1 | line-1-0370-0539-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0470-0547-s002066 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0647-1100-s000000 | forward | revenue | 5 | pending |
| line-2 | line-2-0633-0792-s007009 | forward | revenue | 5 | pending |
| line-2 | line-2-0633-0792-s007009 | reverse | revenue | 5 | pending |
| line-2 | line-2-0598-0656-s010019 | forward | revenue | 5 | pending |
| line-2 | line-2-0598-0656-s010019 | reverse | revenue | 5 | pending |
| line-2 | line-2-0571-0554-s012283 | forward | revenue | 5 | pending |
| line-2 | line-2-0571-0554-s012283 | reverse | revenue | 5 | pending |
| line-2 | line-2-0549-0466-s014225 | forward | revenue | 4 | pending |
| line-2 | line-2-0549-0466-s014225 | reverse | revenue | 4 | pending |
| line-2 | line-2-0526-0378-s016176 | reverse | revenue | 4 | pending |
| line-2 | line-2-0549-0466-s014225 | forward | spare | 1 | pending |
| line-2 | line-2-0549-0466-s014225 | reverse | spare | 1 | pending |
| line-2 | line-2-0526-0378-s016176 | reverse | spare | 1 | pending |
| line-2 | line-2-0647-1100-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0633-0792-s007009 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0740-0226-s000000 | forward | revenue | 7 | pending |
| line-3 | line-3-0624-0453-s005665 | forward | revenue | 6 | pending |
| line-3 | line-3-0624-0453-s005665 | reverse | revenue | 6 | pending |
| line-3 | line-3-0572-0554-s008163 | forward | revenue | 6 | pending |
| line-3 | line-3-0572-0554-s008163 | reverse | revenue | 6 | pending |
| line-3 | line-3-0468-0758-s013233 | forward | revenue | 6 | pending |
| line-3 | line-3-0468-0758-s013233 | reverse | revenue | 6 | pending |
| line-3 | line-3-0354-0950-s018310 | reverse | revenue | 6 | pending |
| line-3 | line-3-0624-0453-s005665 | forward | spare | 1 | pending |
| line-3 | line-3-0624-0453-s005665 | reverse | spare | 1 | pending |
| line-3 | line-3-0572-0554-s008163 | forward | spare | 1 | pending |
| line-3 | line-3-0572-0554-s008163 | reverse | spare | 1 | pending |
| line-3 | line-3-0468-0758-s013233 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**96 trainsets exceed the reference platform envelope**, requiring **5,712.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0370-0539-s000000 | 5 | 2 | 3 | 178.5 |
| line-1-0470-0547-s002066 | 9 | 2 | 7 | 416.5 |
| line-1-0571-0554-s004144 | 8 | 4 | 4 | 238.0 |
| line-1-0731-0566-s007444 | 4 | 2 | 2 | 119.0 |
| line-2-0526-0378-s016176 | 5 | 2 | 3 | 178.5 |
| line-2-0549-0466-s014225 | 10 | 2 | 8 | 476.0 |
| line-2-0571-0554-s012283 | 10 | 4 | 6 | 357.0 |
| line-2-0598-0656-s010019 | 10 | 2 | 8 | 476.0 |
| line-2-0633-0792-s007009 | 11 | 2 | 9 | 535.5 |
| line-2-0647-1100-s000000 | 6 | 2 | 4 | 238.0 |
| line-3-0354-0950-s018310 | 6 | 2 | 4 | 238.0 |
| line-3-0468-0758-s013233 | 13 | 2 | 11 | 654.5 |
| line-3-0572-0554-s008163 | 14 | 4 | 10 | 595.0 |
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
