# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **32 trainsets at stations + 110 at depots = 142 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-1038-0979-s025563 | line-1 | declared-depot | 62 | 3,689.0 | 11 |
| line-2-0399-0481-s000000 | line-2 | declared-depot | 15 | 892.5 | 4 |
| line-3-0717-0891-s000000 | line-3 | declared-depot | 33 | 1,963.5 | 6 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0432-0235-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0447-0303-s005638 | station | forward | revenue | 1 |
| line-1 | line-1-0447-0303-s005638 | station | reverse | revenue | 1 |
| line-1 | line-1-0554-0410-s008664 | station | forward | revenue | 1 |
| line-1 | line-1-0554-0410-s008664 | station | reverse | revenue | 1 |
| line-1 | line-1-0604-0471-s010462 | station | forward | revenue | 1 |
| line-1 | line-1-0604-0471-s010462 | station | reverse | revenue | 1 |
| line-1 | line-1-0637-0515-s011674 | station | forward | revenue | 1 |
| line-1 | line-1-0637-0515-s011674 | station | reverse | revenue | 1 |
| line-1 | line-1-0728-0640-s015139 | station | forward | revenue | 1 |
| line-1 | line-1-0728-0640-s015139 | station | reverse | revenue | 1 |
| line-1 | line-1-1038-0979-s025563 | station | reverse | revenue | 2 |
| line-2 | line-2-0399-0481-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0469-0478-s001425 | station | forward | revenue | 1 |
| line-2 | line-2-0469-0478-s001425 | station | reverse | revenue | 1 |
| line-2 | line-2-0604-0471-s004183 | station | forward | revenue | 1 |
| line-2 | line-2-0604-0471-s004183 | station | reverse | revenue | 1 |
| line-2 | line-2-0742-0465-s006993 | station | reverse | revenue | 2 |
| line-3 | line-3-0403-0375-s013674 | station | reverse | revenue | 2 |
| line-3 | line-3-0469-0478-s010938 | station | forward | revenue | 1 |
| line-3 | line-3-0469-0478-s010938 | station | reverse | revenue | 1 |
| line-3 | line-3-0506-0536-s009378 | station | forward | revenue | 1 |
| line-3 | line-3-0506-0536-s009378 | station | reverse | revenue | 1 |
| line-3 | line-3-0578-0649-s006369 | station | forward | revenue | 1 |
| line-3 | line-3-0578-0649-s006369 | station | reverse | revenue | 1 |
| line-3 | line-3-0717-0891-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-1038-0979-s025563 | depot | — | revenue | 55 |
| line-1 | line-1-1038-0979-s025563 | depot | — | spare | 6 |
| line-1 | line-1-1038-0979-s025563 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0399-0481-s000000 | depot | — | revenue | 12 |
| line-2 | line-2-0399-0481-s000000 | depot | — | spare | 2 |
| line-2 | line-2-0399-0481-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0717-0891-s000000 | depot | — | revenue | 29 |
| line-3 | line-3-0717-0891-s000000 | depot | — | spare | 3 |
| line-3 | line-3-0717-0891-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/kut-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **142 trainsets at 16 stations**; largest initial station queue **14**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **128 revenue, 11 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **32 positions**; **110 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **16 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0432-0235-s000000 | forward | revenue | 6 | pending |
| line-1 | line-1-0447-0303-s005638 | forward | revenue | 6 | pending |
| line-1 | line-1-0447-0303-s005638 | reverse | revenue | 6 | pending |
| line-1 | line-1-0554-0410-s008664 | forward | revenue | 6 | pending |
| line-1 | line-1-0554-0410-s008664 | reverse | revenue | 6 | pending |
| line-1 | line-1-0604-0471-s010462 | forward | revenue | 6 | pending |
| line-1 | line-1-0604-0471-s010462 | reverse | revenue | 6 | pending |
| line-1 | line-1-0637-0515-s011674 | forward | revenue | 6 | pending |
| line-1 | line-1-0637-0515-s011674 | reverse | revenue | 6 | pending |
| line-1 | line-1-0728-0640-s015139 | forward | revenue | 5 | pending |
| line-1 | line-1-0728-0640-s015139 | reverse | revenue | 5 | pending |
| line-1 | line-1-1038-0979-s025563 | reverse | revenue | 5 | pending |
| line-1 | line-1-0728-0640-s015139 | forward | spare | 1 | pending |
| line-1 | line-1-0728-0640-s015139 | reverse | spare | 1 | pending |
| line-1 | line-1-1038-0979-s025563 | reverse | spare | 1 | pending |
| line-1 | line-1-0432-0235-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0447-0303-s005638 | forward | spare | 1 | pending |
| line-1 | line-1-0447-0303-s005638 | reverse | spare | 1 | pending |
| line-1 | line-1-0554-0410-s008664 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0399-0481-s000000 | forward | revenue | 4 | pending |
| line-2 | line-2-0469-0478-s001425 | forward | revenue | 4 | pending |
| line-2 | line-2-0469-0478-s001425 | reverse | revenue | 3 | pending |
| line-2 | line-2-0604-0471-s004183 | forward | revenue | 3 | pending |
| line-2 | line-2-0604-0471-s004183 | reverse | revenue | 3 | pending |
| line-2 | line-2-0742-0465-s006993 | reverse | revenue | 3 | pending |
| line-2 | line-2-0469-0478-s001425 | reverse | spare | 1 | pending |
| line-2 | line-2-0604-0471-s004183 | forward | spare | 1 | pending |
| line-2 | line-2-0604-0471-s004183 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0717-0891-s000000 | forward | revenue | 5 | pending |
| line-3 | line-3-0578-0649-s006369 | forward | revenue | 5 | pending |
| line-3 | line-3-0578-0649-s006369 | reverse | revenue | 5 | pending |
| line-3 | line-3-0506-0536-s009378 | forward | revenue | 5 | pending |
| line-3 | line-3-0506-0536-s009378 | reverse | revenue | 5 | pending |
| line-3 | line-3-0469-0478-s010938 | forward | revenue | 5 | pending |
| line-3 | line-3-0469-0478-s010938 | reverse | revenue | 5 | pending |
| line-3 | line-3-0403-0375-s013674 | reverse | revenue | 4 | pending |
| line-3 | line-3-0403-0375-s013674 | reverse | spare | 1 | pending |
| line-3 | line-3-0717-0891-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0578-0649-s006369 | forward | spare | 1 | pending |
| line-3 | line-3-0578-0649-s006369 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**102 trainsets exceed the reference platform envelope**, requiring **6,069.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0432-0235-s000000 | 7 | 2 | 5 | 297.5 |
| line-1-0447-0303-s005638 | 14 | 2 | 12 | 714.0 |
| line-1-0554-0410-s008664 | 13 | 2 | 11 | 654.5 |
| line-1-0604-0471-s010462 | 12 | 4 | 8 | 476.0 |
| line-1-0637-0515-s011674 | 12 | 2 | 10 | 595.0 |
| line-1-0728-0640-s015139 | 12 | 2 | 10 | 595.0 |
| line-1-1038-0979-s025563 | 6 | 2 | 4 | 238.0 |
| line-2-0399-0481-s000000 | 4 | 2 | 2 | 119.0 |
| line-2-0469-0478-s001425 | 8 | 4 | 4 | 238.0 |
| line-2-0604-0471-s004183 | 8 | 4 | 4 | 238.0 |
| line-2-0742-0465-s006993 | 3 | 2 | 1 | 59.5 |
| line-3-0403-0375-s013674 | 5 | 2 | 3 | 178.5 |
| line-3-0469-0478-s010938 | 10 | 4 | 6 | 357.0 |
| line-3-0506-0536-s009378 | 10 | 2 | 8 | 476.0 |
| line-3-0578-0649-s006369 | 12 | 2 | 10 | 595.0 |
| line-3-0717-0891-s000000 | 6 | 2 | 4 | 238.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Iraq/Kut/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
