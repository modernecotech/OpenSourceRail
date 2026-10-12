# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **38 trainsets at stations + 49 at depots = 87 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0461-0291-s011748 | line-1 | declared-depot | 16 | 784.0 | 4 |
| line-2-0321-0322-s000000 | line-2 | declared-depot | 9 | 441.0 | 3 |
| line-3-0232-0739-s000000 | line-3 | declared-depot | 12 | 588.0 | 4 |
| line-4-0536-0377-s000000 | line-4 | declared-depot | 12 | 588.0 | 3 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0116-0683-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0318-0450-s007009 | station | forward | revenue | 1 |
| line-1 | line-1-0318-0450-s007009 | station | reverse | revenue | 1 |
| line-1 | line-1-0378-0383-s008998 | station | forward | revenue | 1 |
| line-1 | line-1-0378-0383-s008998 | station | reverse | revenue | 1 |
| line-1 | line-1-0382-0378-s009143 | station | forward | revenue | 1 |
| line-1 | line-1-0382-0378-s009143 | station | reverse | revenue | 1 |
| line-1 | line-1-0461-0291-s011748 | station | reverse | revenue | 2 |
| line-2 | line-2-0321-0322-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0360-0380-s001845 | station | forward | revenue | 1 |
| line-2 | line-2-0360-0380-s001845 | station | reverse | revenue | 1 |
| line-2 | line-2-0373-0378-s002122 | station | forward | revenue | 1 |
| line-2 | line-2-0373-0378-s002122 | station | reverse | revenue | 1 |
| line-2 | line-2-0382-0378-s002302 | station | forward | revenue | 1 |
| line-2 | line-2-0382-0378-s002302 | station | reverse | revenue | 1 |
| line-2 | line-2-0536-0377-s005572 | station | forward | revenue | 1 |
| line-2 | line-2-0536-0377-s005572 | station | reverse | revenue | 1 |
| line-2 | line-2-0690-0365-s008858 | station | reverse | revenue | 2 |
| line-3 | line-3-0232-0739-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0325-0361-s010777 | station | reverse | revenue | 2 |
| line-3 | line-3-0360-0380-s009548 | station | forward | revenue | 1 |
| line-3 | line-3-0360-0380-s009548 | station | reverse | revenue | 1 |
| line-3 | line-3-0373-0378-s009243 | station | forward | revenue | 1 |
| line-3 | line-3-0373-0378-s009243 | station | reverse | revenue | 1 |
| line-3 | line-3-0378-0383-s009090 | station | forward | revenue | 1 |
| line-3 | line-3-0378-0383-s009090 | station | reverse | revenue | 1 |
| line-3 | line-3-0383-0485-s006712 | station | forward | revenue | 1 |
| line-3 | line-3-0383-0485-s006712 | station | reverse | revenue | 1 |
| line-4 | line-4-0383-0485-s007245 | station | reverse | revenue | 2 |
| line-4 | line-4-0536-0377-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0461-0291-s011748 | depot | — | revenue | 13 |
| line-1 | line-1-0461-0291-s011748 | depot | — | spare | 2 |
| line-1 | line-1-0461-0291-s011748 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0321-0322-s000000 | depot | — | revenue | 7 |
| line-2 | line-2-0321-0322-s000000 | depot | — | spare | 1 |
| line-2 | line-2-0321-0322-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0232-0739-s000000 | depot | — | revenue | 9 |
| line-3 | line-3-0232-0739-s000000 | depot | — | spare | 2 |
| line-3 | line-3-0232-0739-s000000 | depot | — | cold_reserve | 1 |
| line-4 | line-4-0536-0377-s000000 | depot | — | revenue | 10 |
| line-4 | line-4-0536-0377-s000000 | depot | — | spare | 1 |
| line-4 | line-4-0536-0377-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/idlib-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **87 trainsets at 19 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **77 revenue, 6 spare, 4 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **38 positions**; **49 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **17 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0116-0683-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0318-0450-s007009 | forward | revenue | 3 | pending |
| line-1 | line-1-0318-0450-s007009 | reverse | revenue | 3 | pending |
| line-1 | line-1-0378-0383-s008998 | forward | revenue | 3 | pending |
| line-1 | line-1-0378-0383-s008998 | reverse | revenue | 3 | pending |
| line-1 | line-1-0382-0378-s009143 | forward | revenue | 3 | pending |
| line-1 | line-1-0382-0378-s009143 | reverse | revenue | 3 | pending |
| line-1 | line-1-0461-0291-s011748 | reverse | revenue | 2 | pending |
| line-1 | line-1-0461-0291-s011748 | reverse | spare | 1 | pending |
| line-1 | line-1-0116-0683-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0318-0450-s007009 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0321-0322-s000000 | forward | revenue | 2 | pending |
| line-2 | line-2-0360-0380-s001845 | forward | revenue | 2 | pending |
| line-2 | line-2-0360-0380-s001845 | reverse | revenue | 2 | pending |
| line-2 | line-2-0373-0378-s002122 | forward | revenue | 2 | pending |
| line-2 | line-2-0373-0378-s002122 | reverse | revenue | 2 | pending |
| line-2 | line-2-0382-0378-s002302 | forward | revenue | 2 | pending |
| line-2 | line-2-0382-0378-s002302 | reverse | revenue | 2 | pending |
| line-2 | line-2-0536-0377-s005572 | forward | revenue | 2 | pending |
| line-2 | line-2-0536-0377-s005572 | reverse | revenue | 2 | pending |
| line-2 | line-2-0690-0365-s008858 | reverse | revenue | 1 | pending |
| line-2 | line-2-0690-0365-s008858 | reverse | spare | 1 | pending |
| line-2 | line-2-0321-0322-s000000 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0232-0739-s000000 | forward | revenue | 3 | pending |
| line-3 | line-3-0383-0485-s006712 | forward | revenue | 2 | pending |
| line-3 | line-3-0383-0485-s006712 | reverse | revenue | 2 | pending |
| line-3 | line-3-0378-0383-s009090 | forward | revenue | 2 | pending |
| line-3 | line-3-0378-0383-s009090 | reverse | revenue | 2 | pending |
| line-3 | line-3-0373-0378-s009243 | forward | revenue | 2 | pending |
| line-3 | line-3-0373-0378-s009243 | reverse | revenue | 2 | pending |
| line-3 | line-3-0360-0380-s009548 | forward | revenue | 2 | pending |
| line-3 | line-3-0360-0380-s009548 | reverse | revenue | 2 | pending |
| line-3 | line-3-0325-0361-s010777 | reverse | revenue | 2 | pending |
| line-3 | line-3-0383-0485-s006712 | forward | spare | 1 | pending |
| line-3 | line-3-0383-0485-s006712 | reverse | spare | 1 | pending |
| line-3 | line-3-0378-0383-s009090 | forward | cold_reserve | 1 | pending |
| line-4 | line-4-0536-0377-s000000 | forward | revenue | 7 | pending |
| line-4 | line-4-0383-0485-s007245 | reverse | revenue | 7 | pending |
| line-4 | line-4-0536-0377-s000000 | forward | spare | 1 | pending |
| line-4 | line-4-0383-0485-s007245 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**29 trainsets exceed the reference platform envelope**, requiring **1,421.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0116-0683-s000000 | 4 | 2 | 2 | 98.0 |
| line-1-0318-0450-s007009 | 7 | 2 | 5 | 245.0 |
| line-1-0378-0383-s008998 | 6 | 4 | 2 | 98.0 |
| line-1-0382-0378-s009143 | 6 | 4 | 2 | 98.0 |
| line-1-0461-0291-s011748 | 3 | 2 | 1 | 49.0 |
| line-2-0321-0322-s000000 | 3 | 2 | 1 | 49.0 |
| line-2-0360-0380-s001845 | 4 | 4 | 0 | 0.0 |
| line-2-0373-0378-s002122 | 4 | 4 | 0 | 0.0 |
| line-2-0382-0378-s002302 | 4 | 4 | 0 | 0.0 |
| line-2-0536-0377-s005572 | 4 | 4 | 0 | 0.0 |
| line-2-0690-0365-s008858 | 2 | 2 | 0 | 0.0 |
| line-3-0232-0739-s000000 | 3 | 2 | 1 | 49.0 |
| line-3-0325-0361-s010777 | 2 | 2 | 0 | 0.0 |
| line-3-0360-0380-s009548 | 4 | 4 | 0 | 0.0 |
| line-3-0373-0378-s009243 | 4 | 4 | 0 | 0.0 |
| line-3-0378-0383-s009090 | 5 | 4 | 1 | 49.0 |
| line-3-0383-0485-s006712 | 6 | 4 | 2 | 98.0 |
| line-4-0383-0485-s007245 | 8 | 2 | 6 | 294.0 |
| line-4-0536-0377-s000000 | 8 | 2 | 6 | 294.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Syria/Idlib/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
