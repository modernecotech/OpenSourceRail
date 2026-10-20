# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **42 trainsets at stations + 152 at depots = 194 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0361-1048-s025416 | line-1 | declared-depot | 62 | 3,689.0 | 11 |
| line-2-0486-0817-s000000 | line-2 | declared-depot | 31 | 1,844.5 | 6 |
| line-3-0267-0585-s000000 | line-3 | declared-depot | 33 | 1,963.5 | 6 |
| line-4-0690-0686-s000000 | line-4 | declared-depot | 14 | 833.0 | 3 |
| line-5-0503-0417-s000000 | line-5 | declared-depot | 12 | 714.0 | 3 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0361-1048-s025416 | station | reverse | revenue | 2 |
| line-1 | line-1-0406-0778-s018224 | station | forward | revenue | 1 |
| line-1 | line-1-0406-0778-s018224 | station | reverse | revenue | 1 |
| line-1 | line-1-0461-0632-s014321 | station | forward | revenue | 1 |
| line-1 | line-1-0461-0632-s014321 | station | reverse | revenue | 1 |
| line-1 | line-1-0503-0417-s006255 | station | forward | revenue | 1 |
| line-1 | line-1-0503-0417-s006255 | station | reverse | revenue | 1 |
| line-1 | line-1-0511-0215-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0538-0610-s012205 | station | forward | revenue | 1 |
| line-1 | line-1-0538-0610-s012205 | station | reverse | revenue | 1 |
| line-1 | line-1-0544-0556-s010589 | station | forward | revenue | 1 |
| line-1 | line-1-0544-0556-s010589 | station | reverse | revenue | 1 |
| line-2 | line-2-0486-0817-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0554-0654-s005199 | station | forward | revenue | 1 |
| line-2 | line-2-0554-0654-s005199 | station | reverse | revenue | 1 |
| line-2 | line-2-0577-0533-s008226 | station | forward | revenue | 1 |
| line-2 | line-2-0577-0533-s008226 | station | reverse | revenue | 1 |
| line-2 | line-2-0698-0421-s012183 | station | reverse | revenue | 2 |
| line-3 | line-3-0267-0585-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0461-0632-s004279 | station | forward | revenue | 1 |
| line-3 | line-3-0461-0632-s004279 | station | reverse | revenue | 1 |
| line-3 | line-3-0554-0654-s006321 | station | forward | revenue | 1 |
| line-3 | line-3-0554-0654-s006321 | station | reverse | revenue | 1 |
| line-3 | line-3-0690-0686-s009320 | station | forward | revenue | 1 |
| line-3 | line-3-0690-0686-s009320 | station | reverse | revenue | 1 |
| line-3 | line-3-0883-0735-s013610 | station | reverse | revenue | 2 |
| line-4 | line-4-0538-0512-s006388 | station | reverse | revenue | 2 |
| line-4 | line-4-0577-0533-s005434 | station | forward | revenue | 1 |
| line-4 | line-4-0577-0533-s005434 | station | reverse | revenue | 1 |
| line-4 | line-4-0690-0686-s000000 | station | forward | revenue | 2 |
| line-5 | line-5-0313-0338-s004737 | station | reverse | revenue | 2 |
| line-5 | line-5-0503-0417-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0361-1048-s025416 | depot | — | revenue | 55 |
| line-1 | line-1-0361-1048-s025416 | depot | — | spare | 6 |
| line-1 | line-1-0361-1048-s025416 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0486-0817-s000000 | depot | — | revenue | 27 |
| line-2 | line-2-0486-0817-s000000 | depot | — | spare | 3 |
| line-2 | line-2-0486-0817-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0267-0585-s000000 | depot | — | revenue | 29 |
| line-3 | line-3-0267-0585-s000000 | depot | — | spare | 3 |
| line-3 | line-3-0267-0585-s000000 | depot | — | cold_reserve | 1 |
| line-4 | line-4-0690-0686-s000000 | depot | — | revenue | 12 |
| line-4 | line-4-0690-0686-s000000 | depot | — | spare | 1 |
| line-4 | line-4-0690-0686-s000000 | depot | — | cold_reserve | 1 |
| line-5 | line-5-0503-0417-s000000 | depot | — | revenue | 10 |
| line-5 | line-5-0503-0417-s000000 | depot | — | spare | 1 |
| line-5 | line-5-0503-0417-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/huambo-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **194 trainsets at 21 stations**; largest initial station queue **14**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **175 revenue, 14 spare, 5 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **42 positions**; **152 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **21 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0511-0215-s000000 | forward | revenue | 6 | pending |
| line-1 | line-1-0503-0417-s006255 | forward | revenue | 6 | pending |
| line-1 | line-1-0503-0417-s006255 | reverse | revenue | 6 | pending |
| line-1 | line-1-0544-0556-s010589 | forward | revenue | 6 | pending |
| line-1 | line-1-0544-0556-s010589 | reverse | revenue | 6 | pending |
| line-1 | line-1-0538-0610-s012205 | forward | revenue | 6 | pending |
| line-1 | line-1-0538-0610-s012205 | reverse | revenue | 6 | pending |
| line-1 | line-1-0461-0632-s014321 | forward | revenue | 6 | pending |
| line-1 | line-1-0461-0632-s014321 | reverse | revenue | 6 | pending |
| line-1 | line-1-0406-0778-s018224 | forward | revenue | 5 | pending |
| line-1 | line-1-0406-0778-s018224 | reverse | revenue | 5 | pending |
| line-1 | line-1-0361-1048-s025416 | reverse | revenue | 5 | pending |
| line-1 | line-1-0406-0778-s018224 | forward | spare | 1 | pending |
| line-1 | line-1-0406-0778-s018224 | reverse | spare | 1 | pending |
| line-1 | line-1-0361-1048-s025416 | reverse | spare | 1 | pending |
| line-1 | line-1-0511-0215-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0503-0417-s006255 | forward | spare | 1 | pending |
| line-1 | line-1-0503-0417-s006255 | reverse | spare | 1 | pending |
| line-1 | line-1-0544-0556-s010589 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0486-0817-s000000 | forward | revenue | 6 | pending |
| line-2 | line-2-0554-0654-s005199 | forward | revenue | 6 | pending |
| line-2 | line-2-0554-0654-s005199 | reverse | revenue | 6 | pending |
| line-2 | line-2-0577-0533-s008226 | forward | revenue | 6 | pending |
| line-2 | line-2-0577-0533-s008226 | reverse | revenue | 6 | pending |
| line-2 | line-2-0698-0421-s012183 | reverse | revenue | 5 | pending |
| line-2 | line-2-0698-0421-s012183 | reverse | spare | 1 | pending |
| line-2 | line-2-0486-0817-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0554-0654-s005199 | forward | spare | 1 | pending |
| line-2 | line-2-0554-0654-s005199 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0267-0585-s000000 | forward | revenue | 5 | pending |
| line-3 | line-3-0461-0632-s004279 | forward | revenue | 5 | pending |
| line-3 | line-3-0461-0632-s004279 | reverse | revenue | 5 | pending |
| line-3 | line-3-0554-0654-s006321 | forward | revenue | 5 | pending |
| line-3 | line-3-0554-0654-s006321 | reverse | revenue | 5 | pending |
| line-3 | line-3-0690-0686-s009320 | forward | revenue | 5 | pending |
| line-3 | line-3-0690-0686-s009320 | reverse | revenue | 5 | pending |
| line-3 | line-3-0883-0735-s013610 | reverse | revenue | 4 | pending |
| line-3 | line-3-0883-0735-s013610 | reverse | spare | 1 | pending |
| line-3 | line-3-0267-0585-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0461-0632-s004279 | forward | spare | 1 | pending |
| line-3 | line-3-0461-0632-s004279 | reverse | cold_reserve | 1 | pending |
| line-4 | line-4-0690-0686-s000000 | forward | revenue | 5 | pending |
| line-4 | line-4-0577-0533-s005434 | forward | revenue | 5 | pending |
| line-4 | line-4-0577-0533-s005434 | reverse | revenue | 4 | pending |
| line-4 | line-4-0538-0512-s006388 | reverse | revenue | 4 | pending |
| line-4 | line-4-0577-0533-s005434 | reverse | spare | 1 | pending |
| line-4 | line-4-0538-0512-s006388 | reverse | cold_reserve | 1 | pending |
| line-5 | line-5-0503-0417-s000000 | forward | revenue | 7 | pending |
| line-5 | line-5-0313-0338-s004737 | reverse | revenue | 7 | pending |
| line-5 | line-5-0503-0417-s000000 | forward | spare | 1 | pending |
| line-5 | line-5-0313-0338-s004737 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**136 trainsets exceed the reference platform envelope**, requiring **8,092.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0361-1048-s025416 | 6 | 2 | 4 | 238.0 |
| line-1-0406-0778-s018224 | 12 | 2 | 10 | 595.0 |
| line-1-0461-0632-s014321 | 12 | 4 | 8 | 476.0 |
| line-1-0503-0417-s006255 | 14 | 4 | 10 | 595.0 |
| line-1-0511-0215-s000000 | 7 | 2 | 5 | 297.5 |
| line-1-0538-0610-s012205 | 12 | 2 | 10 | 595.0 |
| line-1-0544-0556-s010589 | 13 | 2 | 11 | 654.5 |
| line-2-0486-0817-s000000 | 7 | 2 | 5 | 297.5 |
| line-2-0554-0654-s005199 | 14 | 4 | 10 | 595.0 |
| line-2-0577-0533-s008226 | 12 | 4 | 8 | 476.0 |
| line-2-0698-0421-s012183 | 6 | 2 | 4 | 238.0 |
| line-3-0267-0585-s000000 | 6 | 2 | 4 | 238.0 |
| line-3-0461-0632-s004279 | 12 | 4 | 8 | 476.0 |
| line-3-0554-0654-s006321 | 10 | 4 | 6 | 357.0 |
| line-3-0690-0686-s009320 | 10 | 4 | 6 | 357.0 |
| line-3-0883-0735-s013610 | 5 | 2 | 3 | 178.5 |
| line-4-0538-0512-s006388 | 5 | 2 | 3 | 178.5 |
| line-4-0577-0533-s005434 | 10 | 4 | 6 | 357.0 |
| line-4-0690-0686-s000000 | 5 | 2 | 3 | 178.5 |
| line-5-0313-0338-s004737 | 8 | 2 | 6 | 357.0 |
| line-5-0503-0417-s000000 | 8 | 2 | 6 | 357.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/central-africa/Angola/Huambo/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
