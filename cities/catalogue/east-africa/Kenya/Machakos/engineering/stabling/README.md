# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **26 trainsets at stations + 42 at depots = 68 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0528-0329-s011989 | line-1 | declared-depot | 17 | 833.0 | 4 |
| line-2-0431-0420-s000000 | line-2 | declared-depot | 8 | 392.0 | 3 |
| line-3-0208-0369-s000000 | line-3 | declared-depot | 9 | 441.0 | 2 |
| line-4-0292-0381-s000000 | line-4 | declared-depot | 8 | 392.0 | 2 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0020-0297-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0292-0381-s006318 | station | forward | revenue | 1 |
| line-1 | line-1-0292-0381-s006318 | station | reverse | revenue | 1 |
| line-1 | line-1-0426-0382-s009481 | station | forward | revenue | 1 |
| line-1 | line-1-0426-0382-s009481 | station | reverse | revenue | 1 |
| line-1 | line-1-0528-0329-s011989 | station | reverse | revenue | 2 |
| line-2 | line-2-0401-0191-s004829 | station | forward | revenue | 1 |
| line-2 | line-2-0401-0191-s004829 | station | reverse | revenue | 1 |
| line-2 | line-2-0413-0102-s006831 | station | reverse | revenue | 2 |
| line-2 | line-2-0413-0287-s002809 | station | forward | revenue | 1 |
| line-2 | line-2-0413-0287-s002809 | station | reverse | revenue | 1 |
| line-2 | line-2-0426-0382-s000801 | station | forward | revenue | 1 |
| line-2 | line-2-0426-0382-s000801 | station | reverse | revenue | 1 |
| line-2 | line-2-0431-0420-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0208-0369-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0390-0161-s006207 | station | reverse | revenue | 2 |
| line-4 | line-4-0263-0563-s005306 | station | reverse | revenue | 2 |
| line-4 | line-4-0292-0381-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0528-0329-s011989 | depot | — | revenue | 14 |
| line-1 | line-1-0528-0329-s011989 | depot | — | spare | 2 |
| line-1 | line-1-0528-0329-s011989 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0431-0420-s000000 | depot | — | revenue | 6 |
| line-2 | line-2-0431-0420-s000000 | depot | — | spare | 1 |
| line-2 | line-2-0431-0420-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0208-0369-s000000 | depot | — | revenue | 7 |
| line-3 | line-3-0208-0369-s000000 | depot | — | spare | 1 |
| line-3 | line-3-0208-0369-s000000 | depot | — | cold_reserve | 1 |
| line-4 | line-4-0292-0381-s000000 | depot | — | revenue | 6 |
| line-4 | line-4-0292-0381-s000000 | depot | — | spare | 1 |
| line-4 | line-4-0292-0381-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/machakos-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **68 trainsets at 13 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **59 revenue, 5 spare, 4 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **26 positions**; **42 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **12 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0020-0297-s000000 | forward | revenue | 4 | pending |
| line-1 | line-1-0292-0381-s006318 | forward | revenue | 4 | pending |
| line-1 | line-1-0292-0381-s006318 | reverse | revenue | 4 | pending |
| line-1 | line-1-0426-0382-s009481 | forward | revenue | 4 | pending |
| line-1 | line-1-0426-0382-s009481 | reverse | revenue | 3 | pending |
| line-1 | line-1-0528-0329-s011989 | reverse | revenue | 3 | pending |
| line-1 | line-1-0426-0382-s009481 | reverse | spare | 1 | pending |
| line-1 | line-1-0528-0329-s011989 | reverse | spare | 1 | pending |
| line-1 | line-1-0020-0297-s000000 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0431-0420-s000000 | forward | revenue | 2 | pending |
| line-2 | line-2-0426-0382-s000801 | forward | revenue | 2 | pending |
| line-2 | line-2-0426-0382-s000801 | reverse | revenue | 2 | pending |
| line-2 | line-2-0413-0287-s002809 | forward | revenue | 2 | pending |
| line-2 | line-2-0413-0287-s002809 | reverse | revenue | 2 | pending |
| line-2 | line-2-0401-0191-s004829 | forward | revenue | 2 | pending |
| line-2 | line-2-0401-0191-s004829 | reverse | revenue | 2 | pending |
| line-2 | line-2-0413-0102-s006831 | reverse | revenue | 2 | pending |
| line-2 | line-2-0431-0420-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0426-0382-s000801 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0208-0369-s000000 | forward | revenue | 6 | pending |
| line-3 | line-3-0390-0161-s006207 | reverse | revenue | 5 | pending |
| line-3 | line-3-0390-0161-s006207 | reverse | spare | 1 | pending |
| line-3 | line-3-0208-0369-s000000 | forward | cold_reserve | 1 | pending |
| line-4 | line-4-0292-0381-s000000 | forward | revenue | 5 | pending |
| line-4 | line-4-0263-0563-s005306 | reverse | revenue | 5 | pending |
| line-4 | line-4-0292-0381-s000000 | forward | spare | 1 | pending |
| line-4 | line-4-0263-0563-s005306 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**36 trainsets exceed the reference platform envelope**, requiring **1,764.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0020-0297-s000000 | 5 | 2 | 3 | 147.0 |
| line-1-0292-0381-s006318 | 8 | 4 | 4 | 196.0 |
| line-1-0426-0382-s009481 | 8 | 4 | 4 | 196.0 |
| line-1-0528-0329-s011989 | 4 | 2 | 2 | 98.0 |
| line-2-0401-0191-s004829 | 4 | 2 | 2 | 98.0 |
| line-2-0413-0102-s006831 | 2 | 2 | 0 | 0.0 |
| line-2-0413-0287-s002809 | 4 | 2 | 2 | 98.0 |
| line-2-0426-0382-s000801 | 5 | 4 | 1 | 49.0 |
| line-2-0431-0420-s000000 | 3 | 2 | 1 | 49.0 |
| line-3-0208-0369-s000000 | 7 | 2 | 5 | 245.0 |
| line-3-0390-0161-s006207 | 6 | 2 | 4 | 196.0 |
| line-4-0263-0563-s005306 | 6 | 2 | 4 | 196.0 |
| line-4-0292-0381-s000000 | 6 | 2 | 4 | 196.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Kenya/Machakos/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
