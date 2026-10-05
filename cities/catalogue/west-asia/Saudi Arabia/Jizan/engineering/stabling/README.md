# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **34 trainsets at stations + 103 at depots = 137 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0057-0560-s019954 | line-1 | declared-depot | 47 | 2,796.5 | 9 |
| line-2-0528-0461-s000000 | line-2 | declared-depot | 16 | 952.0 | 4 |
| line-3-0953-1061-s000000 | line-3 | declared-depot | 40 | 2,380.0 | 8 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0057-0560-s019954 | station | reverse | revenue | 2 |
| line-1 | line-1-0151-0528-s017533 | station | forward | revenue | 1 |
| line-1 | line-1-0151-0528-s017533 | station | reverse | revenue | 1 |
| line-1 | line-1-0289-0544-s014031 | station | forward | revenue | 1 |
| line-1 | line-1-0289-0544-s014031 | station | reverse | revenue | 1 |
| line-1 | line-1-0430-0614-s010526 | station | forward | revenue | 1 |
| line-1 | line-1-0430-0614-s010526 | station | reverse | revenue | 1 |
| line-1 | line-1-0553-0674-s007510 | station | forward | revenue | 1 |
| line-1 | line-1-0553-0674-s007510 | station | reverse | revenue | 1 |
| line-1 | line-1-0674-0734-s004499 | station | forward | revenue | 1 |
| line-1 | line-1-0674-0734-s004499 | station | reverse | revenue | 1 |
| line-1 | line-1-0857-0824-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0435-0789-s007366 | station | reverse | revenue | 2 |
| line-2 | line-2-0472-0660-s004479 | station | forward | revenue | 1 |
| line-2 | line-2-0472-0660-s004479 | station | reverse | revenue | 1 |
| line-2 | line-2-0508-0533-s001606 | station | forward | revenue | 1 |
| line-2 | line-2-0508-0533-s001606 | station | reverse | revenue | 1 |
| line-2 | line-2-0528-0461-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0382-0565-s017566 | station | reverse | revenue | 2 |
| line-3 | line-3-0462-0621-s015362 | station | forward | revenue | 1 |
| line-3 | line-3-0462-0621-s015362 | station | reverse | revenue | 1 |
| line-3 | line-3-0543-0678-s013164 | station | forward | revenue | 1 |
| line-3 | line-3-0543-0678-s013164 | station | reverse | revenue | 1 |
| line-3 | line-3-0652-0756-s010151 | station | forward | revenue | 1 |
| line-3 | line-3-0652-0756-s010151 | station | reverse | revenue | 1 |
| line-3 | line-3-0784-0848-s006573 | station | forward | revenue | 1 |
| line-3 | line-3-0784-0848-s006573 | station | reverse | revenue | 1 |
| line-3 | line-3-0953-1061-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0057-0560-s019954 | depot | — | revenue | 41 |
| line-1 | line-1-0057-0560-s019954 | depot | — | spare | 5 |
| line-1 | line-1-0057-0560-s019954 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0528-0461-s000000 | depot | — | revenue | 13 |
| line-2 | line-2-0528-0461-s000000 | depot | — | spare | 2 |
| line-2 | line-2-0528-0461-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0953-1061-s000000 | depot | — | revenue | 35 |
| line-3 | line-3-0953-1061-s000000 | depot | — | spare | 4 |
| line-3 | line-3-0953-1061-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/jizan-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **137 trainsets at 17 stations**; largest initial station queue **11**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **123 revenue, 11 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **34 positions**; **103 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **17 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0857-0824-s000000 | forward | revenue | 5 | pending |
| line-1 | line-1-0674-0734-s004499 | forward | revenue | 5 | pending |
| line-1 | line-1-0674-0734-s004499 | reverse | revenue | 5 | pending |
| line-1 | line-1-0553-0674-s007510 | forward | revenue | 5 | pending |
| line-1 | line-1-0553-0674-s007510 | reverse | revenue | 5 | pending |
| line-1 | line-1-0430-0614-s010526 | forward | revenue | 5 | pending |
| line-1 | line-1-0430-0614-s010526 | reverse | revenue | 5 | pending |
| line-1 | line-1-0289-0544-s014031 | forward | revenue | 4 | pending |
| line-1 | line-1-0289-0544-s014031 | reverse | revenue | 4 | pending |
| line-1 | line-1-0151-0528-s017533 | forward | revenue | 4 | pending |
| line-1 | line-1-0151-0528-s017533 | reverse | revenue | 4 | pending |
| line-1 | line-1-0057-0560-s019954 | reverse | revenue | 4 | pending |
| line-1 | line-1-0289-0544-s014031 | forward | spare | 1 | pending |
| line-1 | line-1-0289-0544-s014031 | reverse | spare | 1 | pending |
| line-1 | line-1-0151-0528-s017533 | forward | spare | 1 | pending |
| line-1 | line-1-0151-0528-s017533 | reverse | spare | 1 | pending |
| line-1 | line-1-0057-0560-s019954 | reverse | spare | 1 | pending |
| line-1 | line-1-0857-0824-s000000 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0528-0461-s000000 | forward | revenue | 4 | pending |
| line-2 | line-2-0508-0533-s001606 | forward | revenue | 4 | pending |
| line-2 | line-2-0508-0533-s001606 | reverse | revenue | 4 | pending |
| line-2 | line-2-0472-0660-s004479 | forward | revenue | 3 | pending |
| line-2 | line-2-0472-0660-s004479 | reverse | revenue | 3 | pending |
| line-2 | line-2-0435-0789-s007366 | reverse | revenue | 3 | pending |
| line-2 | line-2-0472-0660-s004479 | forward | spare | 1 | pending |
| line-2 | line-2-0472-0660-s004479 | reverse | spare | 1 | pending |
| line-2 | line-2-0435-0789-s007366 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0953-1061-s000000 | forward | revenue | 5 | pending |
| line-3 | line-3-0784-0848-s006573 | forward | revenue | 5 | pending |
| line-3 | line-3-0784-0848-s006573 | reverse | revenue | 5 | pending |
| line-3 | line-3-0652-0756-s010151 | forward | revenue | 5 | pending |
| line-3 | line-3-0652-0756-s010151 | reverse | revenue | 5 | pending |
| line-3 | line-3-0543-0678-s013164 | forward | revenue | 5 | pending |
| line-3 | line-3-0543-0678-s013164 | reverse | revenue | 5 | pending |
| line-3 | line-3-0462-0621-s015362 | forward | revenue | 4 | pending |
| line-3 | line-3-0462-0621-s015362 | reverse | revenue | 4 | pending |
| line-3 | line-3-0382-0565-s017566 | reverse | revenue | 4 | pending |
| line-3 | line-3-0462-0621-s015362 | forward | spare | 1 | pending |
| line-3 | line-3-0462-0621-s015362 | reverse | spare | 1 | pending |
| line-3 | line-3-0382-0565-s017566 | reverse | spare | 1 | pending |
| line-3 | line-3-0953-1061-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0784-0848-s006573 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**91 trainsets exceed the reference platform envelope**, requiring **5,414.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0057-0560-s019954 | 5 | 2 | 3 | 178.5 |
| line-1-0151-0528-s017533 | 10 | 2 | 8 | 476.0 |
| line-1-0289-0544-s014031 | 10 | 2 | 8 | 476.0 |
| line-1-0430-0614-s010526 | 10 | 4 | 6 | 357.0 |
| line-1-0553-0674-s007510 | 10 | 4 | 6 | 357.0 |
| line-1-0674-0734-s004499 | 10 | 4 | 6 | 357.0 |
| line-1-0857-0824-s000000 | 6 | 2 | 4 | 238.0 |
| line-2-0435-0789-s007366 | 4 | 2 | 2 | 119.0 |
| line-2-0472-0660-s004479 | 8 | 2 | 6 | 357.0 |
| line-2-0508-0533-s001606 | 8 | 2 | 6 | 357.0 |
| line-2-0528-0461-s000000 | 4 | 2 | 2 | 119.0 |
| line-3-0382-0565-s017566 | 5 | 2 | 3 | 178.5 |
| line-3-0462-0621-s015362 | 10 | 4 | 6 | 357.0 |
| line-3-0543-0678-s013164 | 10 | 4 | 6 | 357.0 |
| line-3-0652-0756-s010151 | 10 | 4 | 6 | 357.0 |
| line-3-0784-0848-s006573 | 11 | 2 | 9 | 535.5 |
| line-3-0953-1061-s000000 | 6 | 2 | 4 | 238.0 |

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
