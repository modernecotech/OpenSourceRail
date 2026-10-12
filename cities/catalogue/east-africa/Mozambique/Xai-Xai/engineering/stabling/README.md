# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **26 trainsets at stations + 28 at depots = 54 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0580-0436-s000000 | line-1 | declared-depot | 7 | 343.0 | 2 |
| line-2-0325-0372-s008192 | line-2 | declared-depot | 9 | 441.0 | 3 |
| line-3-0508-0509-s000000 | line-3 | declared-depot | 6 | 294.0 | 2 |
| line-4-0378-0397-s000000 | line-4 | declared-depot | 6 | 294.0 | 2 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0351-0573-s005973 | station | reverse | revenue | 2 |
| line-1 | line-1-0418-0533-s004231 | station | forward | revenue | 1 |
| line-1 | line-1-0418-0533-s004231 | station | reverse | revenue | 1 |
| line-1 | line-1-0580-0436-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0325-0372-s008192 | station | reverse | revenue | 2 |
| line-2 | line-2-0378-0397-s006689 | station | forward | revenue | 1 |
| line-2 | line-2-0378-0397-s006689 | station | reverse | revenue | 1 |
| line-2 | line-2-0418-0533-s002716 | station | forward | revenue | 1 |
| line-2 | line-2-0418-0533-s002716 | station | reverse | revenue | 1 |
| line-2 | line-2-0439-0556-s002084 | station | forward | revenue | 1 |
| line-2 | line-2-0439-0556-s002084 | station | reverse | revenue | 1 |
| line-2 | line-2-0455-0642-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0348-0616-s004332 | station | reverse | revenue | 2 |
| line-3 | line-3-0439-0556-s001892 | station | forward | revenue | 1 |
| line-3 | line-3-0439-0556-s001892 | station | reverse | revenue | 1 |
| line-3 | line-3-0508-0509-s000000 | station | forward | revenue | 2 |
| line-4 | line-4-0378-0397-s000000 | station | forward | revenue | 2 |
| line-4 | line-4-0413-0265-s004018 | station | reverse | revenue | 2 |
| line-1 | line-1-0580-0436-s000000 | depot | — | revenue | 5 |
| line-1 | line-1-0580-0436-s000000 | depot | — | spare | 1 |
| line-1 | line-1-0580-0436-s000000 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0325-0372-s008192 | depot | — | revenue | 7 |
| line-2 | line-2-0325-0372-s008192 | depot | — | spare | 1 |
| line-2 | line-2-0325-0372-s008192 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0508-0509-s000000 | depot | — | revenue | 4 |
| line-3 | line-3-0508-0509-s000000 | depot | — | spare | 1 |
| line-3 | line-3-0508-0509-s000000 | depot | — | cold_reserve | 1 |
| line-4 | line-4-0378-0397-s000000 | depot | — | revenue | 4 |
| line-4 | line-4-0378-0397-s000000 | depot | — | spare | 1 |
| line-4 | line-4-0378-0397-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/xai-xai-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **54 trainsets at 13 stations**; largest initial station queue **6**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **46 revenue, 4 spare, 4 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **26 positions**; **28 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **12 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0580-0436-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0418-0533-s004231 | forward | revenue | 3 | pending |
| line-1 | line-1-0418-0533-s004231 | reverse | revenue | 3 | pending |
| line-1 | line-1-0351-0573-s005973 | reverse | revenue | 2 | pending |
| line-1 | line-1-0351-0573-s005973 | reverse | spare | 1 | pending |
| line-1 | line-1-0580-0436-s000000 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0455-0642-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0439-0556-s002084 | forward | revenue | 2 | pending |
| line-2 | line-2-0439-0556-s002084 | reverse | revenue | 2 | pending |
| line-2 | line-2-0418-0533-s002716 | forward | revenue | 2 | pending |
| line-2 | line-2-0418-0533-s002716 | reverse | revenue | 2 | pending |
| line-2 | line-2-0378-0397-s006689 | forward | revenue | 2 | pending |
| line-2 | line-2-0378-0397-s006689 | reverse | revenue | 2 | pending |
| line-2 | line-2-0325-0372-s008192 | reverse | revenue | 2 | pending |
| line-2 | line-2-0439-0556-s002084 | forward | spare | 1 | pending |
| line-2 | line-2-0439-0556-s002084 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0508-0509-s000000 | forward | revenue | 3 | pending |
| line-3 | line-3-0439-0556-s001892 | forward | revenue | 3 | pending |
| line-3 | line-3-0439-0556-s001892 | reverse | revenue | 2 | pending |
| line-3 | line-3-0348-0616-s004332 | reverse | revenue | 2 | pending |
| line-3 | line-3-0439-0556-s001892 | reverse | spare | 1 | pending |
| line-3 | line-3-0348-0616-s004332 | reverse | cold_reserve | 1 | pending |
| line-4 | line-4-0378-0397-s000000 | forward | revenue | 4 | pending |
| line-4 | line-4-0413-0265-s004018 | reverse | revenue | 4 | pending |
| line-4 | line-4-0378-0397-s000000 | forward | spare | 1 | pending |
| line-4 | line-4-0413-0265-s004018 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**18 trainsets exceed the reference platform envelope**, requiring **882.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0351-0573-s005973 | 3 | 2 | 1 | 49.0 |
| line-1-0418-0533-s004231 | 6 | 4 | 2 | 98.0 |
| line-1-0580-0436-s000000 | 4 | 2 | 2 | 98.0 |
| line-2-0325-0372-s008192 | 2 | 2 | 0 | 0.0 |
| line-2-0378-0397-s006689 | 4 | 4 | 0 | 0.0 |
| line-2-0418-0533-s002716 | 4 | 4 | 0 | 0.0 |
| line-2-0439-0556-s002084 | 6 | 4 | 2 | 98.0 |
| line-2-0455-0642-s000000 | 3 | 2 | 1 | 49.0 |
| line-3-0348-0616-s004332 | 3 | 2 | 1 | 49.0 |
| line-3-0439-0556-s001892 | 6 | 4 | 2 | 98.0 |
| line-3-0508-0509-s000000 | 3 | 2 | 1 | 49.0 |
| line-4-0378-0397-s000000 | 5 | 2 | 3 | 147.0 |
| line-4-0413-0265-s004018 | 5 | 2 | 3 | 147.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Mozambique/Xai-Xai/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
