# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **50 trainsets at stations + 101 at depots = 151 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0057-0560-s020382 | line-1 | declared-depot | 47 | 2,796.5 | 10 |
| line-2-0528-0461-s000000 | line-2 | declared-depot | 14 | 833.0 | 4 |
| line-3-0953-1061-s000000 | line-3 | declared-depot | 40 | 2,380.0 | 8 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0057-0560-s020382 | station | reverse | revenue | 2 |
| line-1 | line-1-0152-0525-s017529 | station | forward | revenue | 1 |
| line-1 | line-1-0152-0525-s017529 | station | reverse | revenue | 1 |
| line-1 | line-1-0313-0556-s013440 | station | forward | revenue | 1 |
| line-1 | line-1-0313-0556-s013440 | station | reverse | revenue | 1 |
| line-1 | line-1-0395-0597-s011402 | station | forward | revenue | 1 |
| line-1 | line-1-0395-0597-s011402 | station | reverse | revenue | 1 |
| line-1 | line-1-0478-0637-s009363 | station | forward | revenue | 1 |
| line-1 | line-1-0478-0637-s009363 | station | reverse | revenue | 1 |
| line-1 | line-1-0496-0646-s008917 | station | forward | revenue | 1 |
| line-1 | line-1-0496-0646-s008917 | station | reverse | revenue | 1 |
| line-1 | line-1-0500-0648-s008809 | station | forward | revenue | 1 |
| line-1 | line-1-0500-0648-s008809 | station | reverse | revenue | 1 |
| line-1 | line-1-0503-0650-s008732 | station | forward | revenue | 1 |
| line-1 | line-1-0503-0650-s008732 | station | reverse | revenue | 1 |
| line-1 | line-1-0554-0675-s007482 | station | forward | revenue | 1 |
| line-1 | line-1-0554-0675-s007482 | station | reverse | revenue | 1 |
| line-1 | line-1-0674-0734-s004499 | station | forward | revenue | 1 |
| line-1 | line-1-0674-0734-s004499 | station | reverse | revenue | 1 |
| line-1 | line-1-0857-0824-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0435-0789-s007366 | station | reverse | revenue | 2 |
| line-2 | line-2-0478-0637-s003958 | station | forward | revenue | 1 |
| line-2 | line-2-0478-0637-s003958 | station | reverse | revenue | 1 |
| line-2 | line-2-0479-0633-s003869 | station | forward | revenue | 1 |
| line-2 | line-2-0479-0633-s003869 | station | reverse | revenue | 1 |
| line-2 | line-2-0508-0533-s001606 | station | forward | revenue | 1 |
| line-2 | line-2-0508-0533-s001606 | station | reverse | revenue | 1 |
| line-2 | line-2-0528-0461-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0383-0566-s017538 | station | reverse | revenue | 2 |
| line-3 | line-3-0479-0633-s014899 | station | forward | revenue | 1 |
| line-3 | line-3-0479-0633-s014899 | station | reverse | revenue | 1 |
| line-3 | line-3-0496-0646-s014428 | station | forward | revenue | 1 |
| line-3 | line-3-0496-0646-s014428 | station | reverse | revenue | 1 |
| line-3 | line-3-0500-0648-s014331 | station | forward | revenue | 1 |
| line-3 | line-3-0500-0648-s014331 | station | reverse | revenue | 1 |
| line-3 | line-3-0503-0650-s014255 | station | forward | revenue | 1 |
| line-3 | line-3-0503-0650-s014255 | station | reverse | revenue | 1 |
| line-3 | line-3-0578-0703-s012199 | station | forward | revenue | 1 |
| line-3 | line-3-0578-0703-s012199 | station | reverse | revenue | 1 |
| line-3 | line-3-0652-0756-s010151 | station | forward | revenue | 1 |
| line-3 | line-3-0652-0756-s010151 | station | reverse | revenue | 1 |
| line-3 | line-3-0784-0848-s006573 | station | forward | revenue | 1 |
| line-3 | line-3-0784-0848-s006573 | station | reverse | revenue | 1 |
| line-3 | line-3-0953-1061-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0057-0560-s020382 | depot | — | revenue | 40 |
| line-1 | line-1-0057-0560-s020382 | depot | — | spare | 6 |
| line-1 | line-1-0057-0560-s020382 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0528-0461-s000000 | depot | — | revenue | 11 |
| line-2 | line-2-0528-0461-s000000 | depot | — | spare | 2 |
| line-2 | line-2-0528-0461-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0953-1061-s000000 | depot | — | revenue | 34 |
| line-3 | line-3-0953-1061-s000000 | depot | — | spare | 5 |
| line-3 | line-3-0953-1061-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/jizan-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **151 trainsets at 25 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **135 revenue, 13 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **50 positions**; **101 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **25 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0857-0824-s000000 | forward | revenue | 4 | pending |
| line-1 | line-1-0674-0734-s004499 | forward | revenue | 4 | pending |
| line-1 | line-1-0674-0734-s004499 | reverse | revenue | 3 | pending |
| line-1 | line-1-0554-0675-s007482 | forward | revenue | 3 | pending |
| line-1 | line-1-0554-0675-s007482 | reverse | revenue | 3 | pending |
| line-1 | line-1-0503-0650-s008732 | forward | revenue | 3 | pending |
| line-1 | line-1-0503-0650-s008732 | reverse | revenue | 3 | pending |
| line-1 | line-1-0500-0648-s008809 | forward | revenue | 3 | pending |
| line-1 | line-1-0500-0648-s008809 | reverse | revenue | 3 | pending |
| line-1 | line-1-0496-0646-s008917 | forward | revenue | 3 | pending |
| line-1 | line-1-0496-0646-s008917 | reverse | revenue | 3 | pending |
| line-1 | line-1-0478-0637-s009363 | forward | revenue | 3 | pending |
| line-1 | line-1-0478-0637-s009363 | reverse | revenue | 3 | pending |
| line-1 | line-1-0395-0597-s011402 | forward | revenue | 3 | pending |
| line-1 | line-1-0395-0597-s011402 | reverse | revenue | 3 | pending |
| line-1 | line-1-0313-0556-s013440 | forward | revenue | 3 | pending |
| line-1 | line-1-0313-0556-s013440 | reverse | revenue | 3 | pending |
| line-1 | line-1-0152-0525-s017529 | forward | revenue | 3 | pending |
| line-1 | line-1-0152-0525-s017529 | reverse | revenue | 3 | pending |
| line-1 | line-1-0057-0560-s020382 | reverse | revenue | 3 | pending |
| line-1 | line-1-0674-0734-s004499 | reverse | spare | 1 | pending |
| line-1 | line-1-0554-0675-s007482 | forward | spare | 1 | pending |
| line-1 | line-1-0554-0675-s007482 | reverse | spare | 1 | pending |
| line-1 | line-1-0503-0650-s008732 | forward | spare | 1 | pending |
| line-1 | line-1-0503-0650-s008732 | reverse | spare | 1 | pending |
| line-1 | line-1-0500-0648-s008809 | forward | spare | 1 | pending |
| line-1 | line-1-0500-0648-s008809 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0528-0461-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0508-0533-s001606 | forward | revenue | 3 | pending |
| line-2 | line-2-0508-0533-s001606 | reverse | revenue | 3 | pending |
| line-2 | line-2-0479-0633-s003869 | forward | revenue | 3 | pending |
| line-2 | line-2-0479-0633-s003869 | reverse | revenue | 3 | pending |
| line-2 | line-2-0478-0637-s003958 | forward | revenue | 2 | pending |
| line-2 | line-2-0478-0637-s003958 | reverse | revenue | 2 | pending |
| line-2 | line-2-0435-0789-s007366 | reverse | revenue | 2 | pending |
| line-2 | line-2-0478-0637-s003958 | forward | spare | 1 | pending |
| line-2 | line-2-0478-0637-s003958 | reverse | spare | 1 | pending |
| line-2 | line-2-0435-0789-s007366 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0953-1061-s000000 | forward | revenue | 4 | pending |
| line-3 | line-3-0784-0848-s006573 | forward | revenue | 4 | pending |
| line-3 | line-3-0784-0848-s006573 | reverse | revenue | 4 | pending |
| line-3 | line-3-0652-0756-s010151 | forward | revenue | 4 | pending |
| line-3 | line-3-0652-0756-s010151 | reverse | revenue | 3 | pending |
| line-3 | line-3-0578-0703-s012199 | forward | revenue | 3 | pending |
| line-3 | line-3-0578-0703-s012199 | reverse | revenue | 3 | pending |
| line-3 | line-3-0503-0650-s014255 | forward | revenue | 3 | pending |
| line-3 | line-3-0503-0650-s014255 | reverse | revenue | 3 | pending |
| line-3 | line-3-0500-0648-s014331 | forward | revenue | 3 | pending |
| line-3 | line-3-0500-0648-s014331 | reverse | revenue | 3 | pending |
| line-3 | line-3-0496-0646-s014428 | forward | revenue | 3 | pending |
| line-3 | line-3-0496-0646-s014428 | reverse | revenue | 3 | pending |
| line-3 | line-3-0479-0633-s014899 | forward | revenue | 3 | pending |
| line-3 | line-3-0479-0633-s014899 | reverse | revenue | 3 | pending |
| line-3 | line-3-0383-0566-s017538 | reverse | revenue | 3 | pending |
| line-3 | line-3-0652-0756-s010151 | reverse | spare | 1 | pending |
| line-3 | line-3-0578-0703-s012199 | forward | spare | 1 | pending |
| line-3 | line-3-0578-0703-s012199 | reverse | spare | 1 | pending |
| line-3 | line-3-0503-0650-s014255 | forward | spare | 1 | pending |
| line-3 | line-3-0503-0650-s014255 | reverse | spare | 1 | pending |
| line-3 | line-3-0500-0648-s014331 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**75 trainsets exceed the reference platform envelope**, requiring **4,462.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0057-0560-s020382 | 3 | 2 | 1 | 59.5 |
| line-1-0152-0525-s017529 | 6 | 2 | 4 | 238.0 |
| line-1-0313-0556-s013440 | 6 | 2 | 4 | 238.0 |
| line-1-0395-0597-s011402 | 6 | 4 | 2 | 119.0 |
| line-1-0478-0637-s009363 | 6 | 4 | 2 | 119.0 |
| line-1-0496-0646-s008917 | 6 | 4 | 2 | 119.0 |
| line-1-0500-0648-s008809 | 8 | 4 | 4 | 238.0 |
| line-1-0503-0650-s008732 | 8 | 4 | 4 | 238.0 |
| line-1-0554-0675-s007482 | 8 | 2 | 6 | 357.0 |
| line-1-0674-0734-s004499 | 8 | 4 | 4 | 238.0 |
| line-1-0857-0824-s000000 | 4 | 2 | 2 | 119.0 |
| line-2-0435-0789-s007366 | 3 | 2 | 1 | 59.5 |
| line-2-0478-0637-s003958 | 6 | 4 | 2 | 119.0 |
| line-2-0479-0633-s003869 | 6 | 4 | 2 | 119.0 |
| line-2-0508-0533-s001606 | 6 | 2 | 4 | 238.0 |
| line-2-0528-0461-s000000 | 3 | 2 | 1 | 59.5 |
| line-3-0383-0566-s017538 | 3 | 2 | 1 | 59.5 |
| line-3-0479-0633-s014899 | 6 | 4 | 2 | 119.0 |
| line-3-0496-0646-s014428 | 6 | 4 | 2 | 119.0 |
| line-3-0500-0648-s014331 | 7 | 4 | 3 | 178.5 |
| line-3-0503-0650-s014255 | 8 | 4 | 4 | 238.0 |
| line-3-0578-0703-s012199 | 8 | 2 | 6 | 357.0 |
| line-3-0652-0756-s010151 | 8 | 4 | 4 | 238.0 |
| line-3-0784-0848-s006573 | 8 | 2 | 6 | 357.0 |
| line-3-0953-1061-s000000 | 4 | 2 | 2 | 119.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Saudi Arabia/Jizan/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
