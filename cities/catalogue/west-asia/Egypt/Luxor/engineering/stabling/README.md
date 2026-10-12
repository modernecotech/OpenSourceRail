# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **36 trainsets at stations + 141 at depots = 177 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0268-0383-s000000 | line-1 | declared-depot | 23 | 1,368.5 | 5 |
| line-2-0324-0669-s023097 | line-2 | declared-depot | 61 | 3,629.5 | 11 |
| line-3-0621-0862-s000000 | line-3 | declared-depot | 31 | 1,844.5 | 6 |
| line-4-0547-0754-s000000 | line-4 | declared-depot | 14 | 833.0 | 3 |
| line-5-0399-0681-s000000 | line-5 | declared-depot | 12 | 714.0 | 3 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0268-0383-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0490-0454-s005052 | station | forward | revenue | 1 |
| line-1 | line-1-0490-0454-s005052 | station | reverse | revenue | 1 |
| line-1 | line-1-0601-0490-s007593 | station | forward | revenue | 1 |
| line-1 | line-1-0601-0490-s007593 | station | reverse | revenue | 1 |
| line-1 | line-1-0712-0526-s010123 | station | reverse | revenue | 2 |
| line-2 | line-2-0324-0669-s023097 | station | reverse | revenue | 2 |
| line-2 | line-2-0399-0681-s020748 | station | forward | revenue | 1 |
| line-2 | line-2-0399-0681-s020748 | station | reverse | revenue | 1 |
| line-2 | line-2-0451-0616-s018865 | station | forward | revenue | 1 |
| line-2 | line-2-0451-0616-s018865 | station | reverse | revenue | 1 |
| line-2 | line-2-0544-0571-s016183 | station | forward | revenue | 1 |
| line-2 | line-2-0544-0571-s016183 | station | reverse | revenue | 1 |
| line-2 | line-2-0588-0433-s012647 | station | forward | revenue | 1 |
| line-2 | line-2-0588-0433-s012647 | station | reverse | revenue | 1 |
| line-2 | line-2-0953-0093-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0300-0398-s012607 | station | reverse | revenue | 2 |
| line-3 | line-3-0451-0616-s006680 | station | forward | revenue | 1 |
| line-3 | line-3-0451-0616-s006680 | station | reverse | revenue | 1 |
| line-3 | line-3-0547-0754-s002949 | station | forward | revenue | 1 |
| line-3 | line-3-0547-0754-s002949 | station | reverse | revenue | 1 |
| line-3 | line-3-0621-0862-s000000 | station | forward | revenue | 2 |
| line-4 | line-4-0544-0571-s005384 | station | reverse | revenue | 2 |
| line-4 | line-4-0547-0754-s000000 | station | forward | revenue | 2 |
| line-5 | line-5-0399-0681-s000000 | station | forward | revenue | 2 |
| line-5 | line-5-0485-0861-s004656 | station | reverse | revenue | 2 |
| line-1 | line-1-0268-0383-s000000 | depot | — | revenue | 20 |
| line-1 | line-1-0268-0383-s000000 | depot | — | spare | 2 |
| line-1 | line-1-0268-0383-s000000 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0324-0669-s023097 | depot | — | revenue | 54 |
| line-2 | line-2-0324-0669-s023097 | depot | — | spare | 6 |
| line-2 | line-2-0324-0669-s023097 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0621-0862-s000000 | depot | — | revenue | 27 |
| line-3 | line-3-0621-0862-s000000 | depot | — | spare | 3 |
| line-3 | line-3-0621-0862-s000000 | depot | — | cold_reserve | 1 |
| line-4 | line-4-0547-0754-s000000 | depot | — | revenue | 12 |
| line-4 | line-4-0547-0754-s000000 | depot | — | spare | 1 |
| line-4 | line-4-0547-0754-s000000 | depot | — | cold_reserve | 1 |
| line-5 | line-5-0399-0681-s000000 | depot | — | revenue | 10 |
| line-5 | line-5-0399-0681-s000000 | depot | — | spare | 1 |
| line-5 | line-5-0399-0681-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/luxor-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **177 trainsets at 18 stations**; largest initial station queue **16**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **159 revenue, 13 spare, 5 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **36 positions**; **141 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **18 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0268-0383-s000000 | forward | revenue | 5 | pending |
| line-1 | line-1-0490-0454-s005052 | forward | revenue | 5 | pending |
| line-1 | line-1-0490-0454-s005052 | reverse | revenue | 5 | pending |
| line-1 | line-1-0601-0490-s007593 | forward | revenue | 5 | pending |
| line-1 | line-1-0601-0490-s007593 | reverse | revenue | 4 | pending |
| line-1 | line-1-0712-0526-s010123 | reverse | revenue | 4 | pending |
| line-1 | line-1-0601-0490-s007593 | reverse | spare | 1 | pending |
| line-1 | line-1-0712-0526-s010123 | reverse | spare | 1 | pending |
| line-1 | line-1-0268-0383-s000000 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0953-0093-s000000 | forward | revenue | 7 | pending |
| line-2 | line-2-0588-0433-s012647 | forward | revenue | 7 | pending |
| line-2 | line-2-0588-0433-s012647 | reverse | revenue | 7 | pending |
| line-2 | line-2-0544-0571-s016183 | forward | revenue | 7 | pending |
| line-2 | line-2-0544-0571-s016183 | reverse | revenue | 7 | pending |
| line-2 | line-2-0451-0616-s018865 | forward | revenue | 7 | pending |
| line-2 | line-2-0451-0616-s018865 | reverse | revenue | 6 | pending |
| line-2 | line-2-0399-0681-s020748 | forward | revenue | 6 | pending |
| line-2 | line-2-0399-0681-s020748 | reverse | revenue | 6 | pending |
| line-2 | line-2-0324-0669-s023097 | reverse | revenue | 6 | pending |
| line-2 | line-2-0451-0616-s018865 | reverse | spare | 1 | pending |
| line-2 | line-2-0399-0681-s020748 | forward | spare | 1 | pending |
| line-2 | line-2-0399-0681-s020748 | reverse | spare | 1 | pending |
| line-2 | line-2-0324-0669-s023097 | reverse | spare | 1 | pending |
| line-2 | line-2-0953-0093-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0588-0433-s012647 | forward | spare | 1 | pending |
| line-2 | line-2-0588-0433-s012647 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0621-0862-s000000 | forward | revenue | 6 | pending |
| line-3 | line-3-0547-0754-s002949 | forward | revenue | 6 | pending |
| line-3 | line-3-0547-0754-s002949 | reverse | revenue | 6 | pending |
| line-3 | line-3-0451-0616-s006680 | forward | revenue | 6 | pending |
| line-3 | line-3-0451-0616-s006680 | reverse | revenue | 6 | pending |
| line-3 | line-3-0300-0398-s012607 | reverse | revenue | 5 | pending |
| line-3 | line-3-0300-0398-s012607 | reverse | spare | 1 | pending |
| line-3 | line-3-0621-0862-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0547-0754-s002949 | forward | spare | 1 | pending |
| line-3 | line-3-0547-0754-s002949 | reverse | cold_reserve | 1 | pending |
| line-4 | line-4-0547-0754-s000000 | forward | revenue | 8 | pending |
| line-4 | line-4-0544-0571-s005384 | reverse | revenue | 8 | pending |
| line-4 | line-4-0547-0754-s000000 | forward | spare | 1 | pending |
| line-4 | line-4-0544-0571-s005384 | reverse | cold_reserve | 1 | pending |
| line-5 | line-5-0399-0681-s000000 | forward | revenue | 7 | pending |
| line-5 | line-5-0485-0861-s004656 | reverse | revenue | 7 | pending |
| line-5 | line-5-0399-0681-s000000 | forward | spare | 1 | pending |
| line-5 | line-5-0485-0861-s004656 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**131 trainsets exceed the reference platform envelope**, requiring **7,794.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0268-0383-s000000 | 6 | 2 | 4 | 238.0 |
| line-1-0490-0454-s005052 | 10 | 2 | 8 | 476.0 |
| line-1-0601-0490-s007593 | 10 | 2 | 8 | 476.0 |
| line-1-0712-0526-s010123 | 5 | 2 | 3 | 178.5 |
| line-2-0324-0669-s023097 | 7 | 2 | 5 | 297.5 |
| line-2-0399-0681-s020748 | 14 | 4 | 10 | 595.0 |
| line-2-0451-0616-s018865 | 14 | 4 | 10 | 595.0 |
| line-2-0544-0571-s016183 | 14 | 4 | 10 | 595.0 |
| line-2-0588-0433-s012647 | 16 | 2 | 14 | 833.0 |
| line-2-0953-0093-s000000 | 8 | 2 | 6 | 357.0 |
| line-3-0300-0398-s012607 | 6 | 2 | 4 | 238.0 |
| line-3-0451-0616-s006680 | 12 | 4 | 8 | 476.0 |
| line-3-0547-0754-s002949 | 14 | 4 | 10 | 595.0 |
| line-3-0621-0862-s000000 | 7 | 2 | 5 | 297.5 |
| line-4-0544-0571-s005384 | 9 | 2 | 7 | 416.5 |
| line-4-0547-0754-s000000 | 9 | 2 | 7 | 416.5 |
| line-5-0399-0681-s000000 | 8 | 2 | 6 | 357.0 |
| line-5-0485-0861-s004656 | 8 | 2 | 6 | 357.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Egypt/Luxor/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
