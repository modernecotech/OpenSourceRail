# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **28 trainsets at stations + 32 at depots = 60 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0538-0267-s000000 | line-1 | declared-depot | 10 | 490.0 | 3 |
| line-2-0217-0397-s011549 | line-2 | declared-depot | 15 | 735.0 | 4 |
| line-3-0271-0514-s000000 | line-3 | declared-depot | 7 | 343.0 | 3 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0406-0668-s009196 | station | reverse | revenue | 2 |
| line-1 | line-1-0443-0550-s006529 | station | forward | revenue | 1 |
| line-1 | line-1-0443-0550-s006529 | station | reverse | revenue | 1 |
| line-1 | line-1-0465-0485-s005035 | station | forward | revenue | 1 |
| line-1 | line-1-0465-0485-s005035 | station | reverse | revenue | 1 |
| line-1 | line-1-0484-0429-s003722 | station | forward | revenue | 1 |
| line-1 | line-1-0484-0429-s003722 | station | reverse | revenue | 1 |
| line-1 | line-1-0538-0267-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0217-0397-s011549 | station | reverse | revenue | 2 |
| line-2 | line-2-0293-0449-s009493 | station | forward | revenue | 1 |
| line-2 | line-2-0293-0449-s009493 | station | reverse | revenue | 1 |
| line-2 | line-2-0369-0500-s007457 | station | forward | revenue | 1 |
| line-2 | line-2-0369-0500-s007457 | station | reverse | revenue | 1 |
| line-2 | line-2-0443-0550-s005446 | station | forward | revenue | 1 |
| line-2 | line-2-0443-0550-s005446 | station | reverse | revenue | 1 |
| line-2 | line-2-0550-0738-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0271-0514-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0369-0500-s002076 | station | forward | revenue | 1 |
| line-3 | line-3-0369-0500-s002076 | station | reverse | revenue | 1 |
| line-3 | line-3-0465-0485-s004120 | station | forward | revenue | 1 |
| line-3 | line-3-0465-0485-s004120 | station | reverse | revenue | 1 |
| line-3 | line-3-0557-0472-s006068 | station | reverse | revenue | 2 |
| line-1 | line-1-0538-0267-s000000 | depot | — | revenue | 8 |
| line-1 | line-1-0538-0267-s000000 | depot | — | spare | 1 |
| line-1 | line-1-0538-0267-s000000 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0217-0397-s011549 | depot | — | revenue | 12 |
| line-2 | line-2-0217-0397-s011549 | depot | — | spare | 2 |
| line-2 | line-2-0217-0397-s011549 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0271-0514-s000000 | depot | — | revenue | 5 |
| line-3 | line-3-0271-0514-s000000 | depot | — | spare | 1 |
| line-3 | line-3-0271-0514-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/kigoma-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **60 trainsets at 14 stations**; largest initial station queue **6**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **53 revenue, 4 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **28 positions**; **32 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **12 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0538-0267-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0484-0429-s003722 | forward | revenue | 3 | pending |
| line-1 | line-1-0484-0429-s003722 | reverse | revenue | 2 | pending |
| line-1 | line-1-0465-0485-s005035 | forward | revenue | 2 | pending |
| line-1 | line-1-0465-0485-s005035 | reverse | revenue | 2 | pending |
| line-1 | line-1-0443-0550-s006529 | forward | revenue | 2 | pending |
| line-1 | line-1-0443-0550-s006529 | reverse | revenue | 2 | pending |
| line-1 | line-1-0406-0668-s009196 | reverse | revenue | 2 | pending |
| line-1 | line-1-0484-0429-s003722 | reverse | spare | 1 | pending |
| line-1 | line-1-0465-0485-s005035 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0550-0738-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0443-0550-s005446 | forward | revenue | 3 | pending |
| line-2 | line-2-0443-0550-s005446 | reverse | revenue | 3 | pending |
| line-2 | line-2-0369-0500-s007457 | forward | revenue | 3 | pending |
| line-2 | line-2-0369-0500-s007457 | reverse | revenue | 3 | pending |
| line-2 | line-2-0293-0449-s009493 | forward | revenue | 3 | pending |
| line-2 | line-2-0293-0449-s009493 | reverse | revenue | 2 | pending |
| line-2 | line-2-0217-0397-s011549 | reverse | revenue | 2 | pending |
| line-2 | line-2-0293-0449-s009493 | reverse | spare | 1 | pending |
| line-2 | line-2-0217-0397-s011549 | reverse | spare | 1 | pending |
| line-2 | line-2-0550-0738-s000000 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0271-0514-s000000 | forward | revenue | 3 | pending |
| line-3 | line-3-0369-0500-s002076 | forward | revenue | 2 | pending |
| line-3 | line-3-0369-0500-s002076 | reverse | revenue | 2 | pending |
| line-3 | line-3-0465-0485-s004120 | forward | revenue | 2 | pending |
| line-3 | line-3-0465-0485-s004120 | reverse | revenue | 2 | pending |
| line-3 | line-3-0557-0472-s006068 | reverse | revenue | 2 | pending |
| line-3 | line-3-0369-0500-s002076 | forward | spare | 1 | pending |
| line-3 | line-3-0369-0500-s002076 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**20 trainsets exceed the reference platform envelope**, requiring **980.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0406-0668-s009196 | 2 | 2 | 0 | 0.0 |
| line-1-0443-0550-s006529 | 4 | 4 | 0 | 0.0 |
| line-1-0465-0485-s005035 | 5 | 4 | 1 | 49.0 |
| line-1-0484-0429-s003722 | 6 | 2 | 4 | 196.0 |
| line-1-0538-0267-s000000 | 3 | 2 | 1 | 49.0 |
| line-2-0217-0397-s011549 | 3 | 2 | 1 | 49.0 |
| line-2-0293-0449-s009493 | 6 | 2 | 4 | 196.0 |
| line-2-0369-0500-s007457 | 6 | 4 | 2 | 98.0 |
| line-2-0443-0550-s005446 | 6 | 4 | 2 | 98.0 |
| line-2-0550-0738-s000000 | 4 | 2 | 2 | 98.0 |
| line-3-0271-0514-s000000 | 3 | 2 | 1 | 49.0 |
| line-3-0369-0500-s002076 | 6 | 4 | 2 | 98.0 |
| line-3-0465-0485-s004120 | 4 | 4 | 0 | 0.0 |
| line-3-0557-0472-s006068 | 2 | 2 | 0 | 0.0 |

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
