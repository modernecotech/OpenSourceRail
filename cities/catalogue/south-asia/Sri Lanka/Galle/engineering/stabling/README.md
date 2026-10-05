# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **34 trainsets at stations + 137 at depots = 171 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0437-0220-s020538 | line-1 | declared-depot | 49 | 2,915.5 | 9 |
| line-2-0346-0285-s000000 | line-2 | declared-depot | 48 | 2,856.0 | 8 |
| line-3-0306-1057-s000000 | line-3 | declared-depot | 40 | 2,380.0 | 7 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0437-0220-s020538 | station | reverse | revenue | 2 |
| line-1 | line-1-0496-0315-s018044 | station | forward | revenue | 1 |
| line-1 | line-1-0496-0315-s018044 | station | reverse | revenue | 1 |
| line-1 | line-1-0556-0411-s015521 | station | forward | revenue | 1 |
| line-1 | line-1-0556-0411-s015521 | station | reverse | revenue | 1 |
| line-1 | line-1-0615-0506-s013015 | station | forward | revenue | 1 |
| line-1 | line-1-0615-0506-s013015 | station | reverse | revenue | 1 |
| line-1 | line-1-0686-0621-s010010 | station | forward | revenue | 1 |
| line-1 | line-1-0686-0621-s010010 | station | reverse | revenue | 1 |
| line-1 | line-1-0757-0734-s007009 | station | forward | revenue | 1 |
| line-1 | line-1-0757-0734-s007009 | station | reverse | revenue | 1 |
| line-1 | line-1-0880-1029-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0346-0285-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0449-0483-s004954 | station | forward | revenue | 1 |
| line-2 | line-2-0449-0483-s004954 | station | reverse | revenue | 1 |
| line-2 | line-2-0512-0603-s007970 | station | forward | revenue | 1 |
| line-2 | line-2-0512-0603-s007970 | station | reverse | revenue | 1 |
| line-2 | line-2-0625-0820-s013421 | station | forward | revenue | 1 |
| line-2 | line-2-0625-0820-s013421 | station | reverse | revenue | 1 |
| line-2 | line-2-0784-1025-s018855 | station | reverse | revenue | 2 |
| line-3 | line-3-0306-1057-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0445-0807-s007004 | station | forward | revenue | 1 |
| line-3 | line-3-0445-0807-s007004 | station | reverse | revenue | 1 |
| line-3 | line-3-0508-0671-s010317 | station | forward | revenue | 1 |
| line-3 | line-3-0508-0671-s010317 | station | reverse | revenue | 1 |
| line-3 | line-3-0561-0556-s013103 | station | forward | revenue | 1 |
| line-3 | line-3-0561-0556-s013103 | station | reverse | revenue | 1 |
| line-3 | line-3-0621-0427-s016238 | station | reverse | revenue | 2 |
| line-1 | line-1-0437-0220-s020538 | depot | — | revenue | 43 |
| line-1 | line-1-0437-0220-s020538 | depot | — | spare | 5 |
| line-1 | line-1-0437-0220-s020538 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0346-0285-s000000 | depot | — | revenue | 42 |
| line-2 | line-2-0346-0285-s000000 | depot | — | spare | 5 |
| line-2 | line-2-0346-0285-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0306-1057-s000000 | depot | — | revenue | 35 |
| line-3 | line-3-0306-1057-s000000 | depot | — | spare | 4 |
| line-3 | line-3-0306-1057-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/galle-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **171 trainsets at 17 stations**; largest initial station queue **15**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **154 revenue, 14 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **34 positions**; **137 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **17 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0880-1029-s000000 | forward | revenue | 5 | pending |
| line-1 | line-1-0757-0734-s007009 | forward | revenue | 5 | pending |
| line-1 | line-1-0757-0734-s007009 | reverse | revenue | 5 | pending |
| line-1 | line-1-0686-0621-s010010 | forward | revenue | 5 | pending |
| line-1 | line-1-0686-0621-s010010 | reverse | revenue | 5 | pending |
| line-1 | line-1-0615-0506-s013015 | forward | revenue | 5 | pending |
| line-1 | line-1-0615-0506-s013015 | reverse | revenue | 5 | pending |
| line-1 | line-1-0556-0411-s015521 | forward | revenue | 5 | pending |
| line-1 | line-1-0556-0411-s015521 | reverse | revenue | 5 | pending |
| line-1 | line-1-0496-0315-s018044 | forward | revenue | 4 | pending |
| line-1 | line-1-0496-0315-s018044 | reverse | revenue | 4 | pending |
| line-1 | line-1-0437-0220-s020538 | reverse | revenue | 4 | pending |
| line-1 | line-1-0496-0315-s018044 | forward | spare | 1 | pending |
| line-1 | line-1-0496-0315-s018044 | reverse | spare | 1 | pending |
| line-1 | line-1-0437-0220-s020538 | reverse | spare | 1 | pending |
| line-1 | line-1-0880-1029-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0757-0734-s007009 | forward | spare | 1 | pending |
| line-1 | line-1-0757-0734-s007009 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0346-0285-s000000 | forward | revenue | 7 | pending |
| line-2 | line-2-0449-0483-s004954 | forward | revenue | 7 | pending |
| line-2 | line-2-0449-0483-s004954 | reverse | revenue | 7 | pending |
| line-2 | line-2-0512-0603-s007970 | forward | revenue | 7 | pending |
| line-2 | line-2-0512-0603-s007970 | reverse | revenue | 6 | pending |
| line-2 | line-2-0625-0820-s013421 | forward | revenue | 6 | pending |
| line-2 | line-2-0625-0820-s013421 | reverse | revenue | 6 | pending |
| line-2 | line-2-0784-1025-s018855 | reverse | revenue | 6 | pending |
| line-2 | line-2-0512-0603-s007970 | reverse | spare | 1 | pending |
| line-2 | line-2-0625-0820-s013421 | forward | spare | 1 | pending |
| line-2 | line-2-0625-0820-s013421 | reverse | spare | 1 | pending |
| line-2 | line-2-0784-1025-s018855 | reverse | spare | 1 | pending |
| line-2 | line-2-0346-0285-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0449-0483-s004954 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0306-1057-s000000 | forward | revenue | 6 | pending |
| line-3 | line-3-0445-0807-s007004 | forward | revenue | 6 | pending |
| line-3 | line-3-0445-0807-s007004 | reverse | revenue | 6 | pending |
| line-3 | line-3-0508-0671-s010317 | forward | revenue | 6 | pending |
| line-3 | line-3-0508-0671-s010317 | reverse | revenue | 6 | pending |
| line-3 | line-3-0561-0556-s013103 | forward | revenue | 5 | pending |
| line-3 | line-3-0561-0556-s013103 | reverse | revenue | 5 | pending |
| line-3 | line-3-0621-0427-s016238 | reverse | revenue | 5 | pending |
| line-3 | line-3-0561-0556-s013103 | forward | spare | 1 | pending |
| line-3 | line-3-0561-0556-s013103 | reverse | spare | 1 | pending |
| line-3 | line-3-0621-0427-s016238 | reverse | spare | 1 | pending |
| line-3 | line-3-0306-1057-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0445-0807-s007004 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**137 trainsets exceed the reference platform envelope**, requiring **8,151.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0437-0220-s020538 | 5 | 2 | 3 | 178.5 |
| line-1-0496-0315-s018044 | 10 | 2 | 8 | 476.0 |
| line-1-0556-0411-s015521 | 10 | 2 | 8 | 476.0 |
| line-1-0615-0506-s013015 | 10 | 2 | 8 | 476.0 |
| line-1-0686-0621-s010010 | 10 | 2 | 8 | 476.0 |
| line-1-0757-0734-s007009 | 12 | 2 | 10 | 595.0 |
| line-1-0880-1029-s000000 | 6 | 2 | 4 | 238.0 |
| line-2-0346-0285-s000000 | 8 | 2 | 6 | 357.0 |
| line-2-0449-0483-s004954 | 15 | 2 | 13 | 773.5 |
| line-2-0512-0603-s007970 | 14 | 2 | 12 | 714.0 |
| line-2-0625-0820-s013421 | 14 | 2 | 12 | 714.0 |
| line-2-0784-1025-s018855 | 7 | 2 | 5 | 297.5 |
| line-3-0306-1057-s000000 | 7 | 2 | 5 | 297.5 |
| line-3-0445-0807-s007004 | 13 | 2 | 11 | 654.5 |
| line-3-0508-0671-s010317 | 12 | 2 | 10 | 595.0 |
| line-3-0561-0556-s013103 | 12 | 2 | 10 | 595.0 |
| line-3-0621-0427-s016238 | 6 | 2 | 4 | 238.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/south-asia/Sri Lanka/Galle/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
