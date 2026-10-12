# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **34 trainsets at stations + 41 at depots = 75 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0406-0668-s011599 | line-1 | declared-depot | 13 | 637.0 | 4 |
| line-2-0550-0738-s000000 | line-2 | declared-depot | 15 | 735.0 | 4 |
| line-3-0271-0514-s000000 | line-3 | declared-depot | 7 | 343.0 | 3 |
| line-4-0548-0708-s000000 | line-4 | declared-depot | 6 | 294.0 | 2 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0396-0390-s005039 | station | forward | revenue | 1 |
| line-1 | line-1-0396-0390-s005039 | station | reverse | revenue | 1 |
| line-1 | line-1-0406-0668-s011599 | station | reverse | revenue | 2 |
| line-1 | line-1-0440-0489-s007581 | station | forward | revenue | 1 |
| line-1 | line-1-0440-0489-s007581 | station | reverse | revenue | 1 |
| line-1 | line-1-0441-0549-s008856 | station | forward | revenue | 1 |
| line-1 | line-1-0441-0549-s008856 | station | reverse | revenue | 1 |
| line-1 | line-1-0456-0328-s003020 | station | forward | revenue | 1 |
| line-1 | line-1-0456-0328-s003020 | station | reverse | revenue | 1 |
| line-1 | line-1-0538-0267-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0217-0397-s011549 | station | reverse | revenue | 2 |
| line-2 | line-2-0369-0500-s007457 | station | forward | revenue | 1 |
| line-2 | line-2-0369-0500-s007457 | station | reverse | revenue | 1 |
| line-2 | line-2-0441-0549-s005494 | station | forward | revenue | 1 |
| line-2 | line-2-0441-0549-s005494 | station | reverse | revenue | 1 |
| line-2 | line-2-0548-0708-s000617 | station | forward | revenue | 1 |
| line-2 | line-2-0548-0708-s000617 | station | reverse | revenue | 1 |
| line-2 | line-2-0550-0738-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0271-0514-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0369-0500-s002076 | station | forward | revenue | 1 |
| line-3 | line-3-0369-0500-s002076 | station | reverse | revenue | 1 |
| line-3 | line-3-0440-0489-s003587 | station | forward | revenue | 1 |
| line-3 | line-3-0440-0489-s003587 | station | reverse | revenue | 1 |
| line-3 | line-3-0557-0472-s006068 | station | reverse | revenue | 2 |
| line-4 | line-4-0548-0708-s000000 | station | forward | revenue | 2 |
| line-4 | line-4-0681-0718-s004002 | station | reverse | revenue | 2 |
| line-1 | line-1-0406-0668-s011599 | depot | — | revenue | 10 |
| line-1 | line-1-0406-0668-s011599 | depot | — | spare | 2 |
| line-1 | line-1-0406-0668-s011599 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0550-0738-s000000 | depot | — | revenue | 12 |
| line-2 | line-2-0550-0738-s000000 | depot | — | spare | 2 |
| line-2 | line-2-0550-0738-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0271-0514-s000000 | depot | — | revenue | 5 |
| line-3 | line-3-0271-0514-s000000 | depot | — | spare | 1 |
| line-3 | line-3-0271-0514-s000000 | depot | — | cold_reserve | 1 |
| line-4 | line-4-0548-0708-s000000 | depot | — | revenue | 4 |
| line-4 | line-4-0548-0708-s000000 | depot | — | spare | 1 |
| line-4 | line-4-0548-0708-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/kigoma-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **75 trainsets at 17 stations**; largest initial station queue **6**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **65 revenue, 6 spare, 4 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **34 positions**; **41 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **15 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0538-0267-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0456-0328-s003020 | forward | revenue | 3 | pending |
| line-1 | line-1-0456-0328-s003020 | reverse | revenue | 2 | pending |
| line-1 | line-1-0396-0390-s005039 | forward | revenue | 2 | pending |
| line-1 | line-1-0396-0390-s005039 | reverse | revenue | 2 | pending |
| line-1 | line-1-0440-0489-s007581 | forward | revenue | 2 | pending |
| line-1 | line-1-0440-0489-s007581 | reverse | revenue | 2 | pending |
| line-1 | line-1-0441-0549-s008856 | forward | revenue | 2 | pending |
| line-1 | line-1-0441-0549-s008856 | reverse | revenue | 2 | pending |
| line-1 | line-1-0406-0668-s011599 | reverse | revenue | 2 | pending |
| line-1 | line-1-0456-0328-s003020 | reverse | spare | 1 | pending |
| line-1 | line-1-0396-0390-s005039 | forward | spare | 1 | pending |
| line-1 | line-1-0396-0390-s005039 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0550-0738-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0548-0708-s000617 | forward | revenue | 3 | pending |
| line-2 | line-2-0548-0708-s000617 | reverse | revenue | 3 | pending |
| line-2 | line-2-0441-0549-s005494 | forward | revenue | 3 | pending |
| line-2 | line-2-0441-0549-s005494 | reverse | revenue | 3 | pending |
| line-2 | line-2-0369-0500-s007457 | forward | revenue | 3 | pending |
| line-2 | line-2-0369-0500-s007457 | reverse | revenue | 2 | pending |
| line-2 | line-2-0217-0397-s011549 | reverse | revenue | 2 | pending |
| line-2 | line-2-0369-0500-s007457 | reverse | spare | 1 | pending |
| line-2 | line-2-0217-0397-s011549 | reverse | spare | 1 | pending |
| line-2 | line-2-0550-0738-s000000 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0271-0514-s000000 | forward | revenue | 3 | pending |
| line-3 | line-3-0369-0500-s002076 | forward | revenue | 2 | pending |
| line-3 | line-3-0369-0500-s002076 | reverse | revenue | 2 | pending |
| line-3 | line-3-0440-0489-s003587 | forward | revenue | 2 | pending |
| line-3 | line-3-0440-0489-s003587 | reverse | revenue | 2 | pending |
| line-3 | line-3-0557-0472-s006068 | reverse | revenue | 2 | pending |
| line-3 | line-3-0369-0500-s002076 | forward | spare | 1 | pending |
| line-3 | line-3-0369-0500-s002076 | reverse | cold_reserve | 1 | pending |
| line-4 | line-4-0548-0708-s000000 | forward | revenue | 4 | pending |
| line-4 | line-4-0681-0718-s004002 | reverse | revenue | 4 | pending |
| line-4 | line-4-0548-0708-s000000 | forward | spare | 1 | pending |
| line-4 | line-4-0681-0718-s004002 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**27 trainsets exceed the reference platform envelope**, requiring **1,323.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0396-0390-s005039 | 6 | 2 | 4 | 196.0 |
| line-1-0406-0668-s011599 | 2 | 2 | 0 | 0.0 |
| line-1-0440-0489-s007581 | 4 | 4 | 0 | 0.0 |
| line-1-0441-0549-s008856 | 4 | 4 | 0 | 0.0 |
| line-1-0456-0328-s003020 | 6 | 2 | 4 | 196.0 |
| line-1-0538-0267-s000000 | 3 | 2 | 1 | 49.0 |
| line-2-0217-0397-s011549 | 3 | 2 | 1 | 49.0 |
| line-2-0369-0500-s007457 | 6 | 4 | 2 | 98.0 |
| line-2-0441-0549-s005494 | 6 | 4 | 2 | 98.0 |
| line-2-0548-0708-s000617 | 6 | 4 | 2 | 98.0 |
| line-2-0550-0738-s000000 | 4 | 2 | 2 | 98.0 |
| line-3-0271-0514-s000000 | 3 | 2 | 1 | 49.0 |
| line-3-0369-0500-s002076 | 6 | 4 | 2 | 98.0 |
| line-3-0440-0489-s003587 | 4 | 4 | 0 | 0.0 |
| line-3-0557-0472-s006068 | 2 | 2 | 0 | 0.0 |
| line-4-0548-0708-s000000 | 5 | 2 | 3 | 147.0 |
| line-4-0681-0718-s004002 | 5 | 2 | 3 | 147.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Tanzania/Kigoma/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
