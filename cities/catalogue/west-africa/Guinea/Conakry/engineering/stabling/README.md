# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **38 trainsets at stations + 44 at depots = 82 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **FAIL**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0790-0413-s025183 | line-1 | declared-depot | 26 | 2,210.0 | 6 |
| line-2-0638-0556-s000000 | line-2 | declared-depot | 16 | 1,360.0 | 4 |
| line-3-0289-0675-s000000 | line-3 | declared-depot | 2 | 170.0 | 2 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0023-1227-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0186-1061-s005429 | station | forward | revenue | 1 |
| line-1 | line-1-0186-1061-s005429 | station | reverse | revenue | 1 |
| line-1 | line-1-0353-0875-s010894 | station | forward | revenue | 1 |
| line-1 | line-1-0353-0875-s010894 | station | reverse | revenue | 1 |
| line-1 | line-1-0444-0778-s013904 | station | forward | revenue | 1 |
| line-1 | line-1-0444-0778-s013904 | station | reverse | revenue | 1 |
| line-1 | line-1-0536-0681-s016911 | station | forward | revenue | 1 |
| line-1 | line-1-0536-0681-s016911 | station | reverse | revenue | 1 |
| line-1 | line-1-0629-0584-s019914 | station | forward | revenue | 1 |
| line-1 | line-1-0629-0584-s019914 | station | reverse | revenue | 1 |
| line-1 | line-1-0790-0413-s025183 | station | reverse | revenue | 2 |
| line-2 | line-2-0061-0925-s016963 | station | reverse | revenue | 2 |
| line-2 | line-2-0183-0821-s012289 | station | forward | revenue | 1 |
| line-2 | line-2-0183-0821-s012289 | station | reverse | revenue | 1 |
| line-2 | line-2-0342-0732-s007636 | station | forward | revenue | 1 |
| line-2 | line-2-0342-0732-s007636 | station | reverse | revenue | 1 |
| line-2 | line-2-0459-0663-s004619 | station | forward | revenue | 1 |
| line-2 | line-2-0459-0663-s004619 | station | reverse | revenue | 1 |
| line-2 | line-2-0575-0593-s001613 | station | forward | revenue | 1 |
| line-2 | line-2-0575-0593-s001613 | station | reverse | revenue | 1 |
| line-2 | line-2-0638-0556-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0283-0664-s006824 | station | forward | revenue | 1 |
| line-3 | line-3-0283-0664-s006824 | station | reverse | revenue | 1 |
| line-3 | line-3-0289-0675-s000000 | station | forward | revenue | 1 |
| line-3 | line-3-0289-0675-s000000 | station | reverse | revenue | 1 |
| line-3 | line-3-0445-0622-s010392 | station | forward | revenue | 1 |
| line-3 | line-3-0445-0622-s010392 | station | reverse | revenue | 1 |
| line-3 | line-3-0559-0526-s013424 | station | forward | revenue | 1 |
| line-3 | line-3-0564-0508-s027267 | station | forward | revenue | 1 |
| line-3 | line-3-0685-0403-s016963 | station | forward | revenue | 1 |
| line-3 | line-3-0685-0403-s016963 | station | reverse | revenue | 1 |
| line-3 | line-3-0811-0351-s020449 | station | forward | revenue | 1 |
| line-3 | line-3-0811-0351-s020449 | station | reverse | revenue | 1 |
| line-1 | line-1-0790-0413-s025183 | depot | — | revenue | 22 |
| line-1 | line-1-0790-0413-s025183 | depot | — | spare | 3 |
| line-1 | line-1-0790-0413-s025183 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0638-0556-s000000 | depot | — | revenue | 13 |
| line-2 | line-2-0638-0556-s000000 | depot | — | spare | 2 |
| line-2 | line-2-0638-0556-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0289-0675-s000000 | depot | — | spare | 1 |
| line-3 | line-3-0289-0675-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate unavailable: morning station allocation is incomplete.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **82 trainsets at 21 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **73 revenue, 6 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **42 positions**; **40 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **12 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0023-1227-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0186-1061-s005429 | forward | revenue | 3 | pending |
| line-1 | line-1-0186-1061-s005429 | reverse | revenue | 3 | pending |
| line-1 | line-1-0353-0875-s010894 | forward | revenue | 3 | pending |
| line-1 | line-1-0353-0875-s010894 | reverse | revenue | 3 | pending |
| line-1 | line-1-0444-0778-s013904 | forward | revenue | 3 | pending |
| line-1 | line-1-0444-0778-s013904 | reverse | revenue | 3 | pending |
| line-1 | line-1-0536-0681-s016911 | forward | revenue | 3 | pending |
| line-1 | line-1-0536-0681-s016911 | reverse | revenue | 3 | pending |
| line-1 | line-1-0629-0584-s019914 | forward | revenue | 3 | pending |
| line-1 | line-1-0629-0584-s019914 | reverse | revenue | 3 | pending |
| line-1 | line-1-0790-0413-s025183 | reverse | revenue | 3 | pending |
| line-1 | line-1-0023-1227-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0186-1061-s005429 | forward | spare | 1 | pending |
| line-1 | line-1-0186-1061-s005429 | reverse | spare | 1 | pending |
| line-1 | line-1-0353-0875-s010894 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0638-0556-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0575-0593-s001613 | forward | revenue | 3 | pending |
| line-2 | line-2-0575-0593-s001613 | reverse | revenue | 3 | pending |
| line-2 | line-2-0459-0663-s004619 | forward | revenue | 3 | pending |
| line-2 | line-2-0459-0663-s004619 | reverse | revenue | 3 | pending |
| line-2 | line-2-0342-0732-s007636 | forward | revenue | 2 | pending |
| line-2 | line-2-0342-0732-s007636 | reverse | revenue | 2 | pending |
| line-2 | line-2-0183-0821-s012289 | forward | revenue | 2 | pending |
| line-2 | line-2-0183-0821-s012289 | reverse | revenue | 2 | pending |
| line-2 | line-2-0061-0925-s016963 | reverse | revenue | 2 | pending |
| line-2 | line-2-0342-0732-s007636 | forward | spare | 1 | pending |
| line-2 | line-2-0342-0732-s007636 | reverse | spare | 1 | pending |
| line-2 | line-2-0183-0821-s012289 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0289-0675-s000000 | forward | revenue | 1 | pending |
| line-3 | line-3-0289-0675-s000000 | reverse | revenue | 1 | pending |
| line-3 | line-3-0283-0664-s006824 | forward | revenue | 1 | pending |
| line-3 | line-3-0283-0664-s006824 | reverse | revenue | 1 | pending |
| line-3 | line-3-0445-0622-s010392 | forward | revenue | 1 | pending |
| line-3 | line-3-0445-0622-s010392 | reverse | revenue | 1 | pending |
| line-3 | line-3-0559-0526-s013424 | forward | revenue | 1 | pending |
| line-3 | line-3-0685-0403-s016963 | forward | revenue | 1 | pending |
| line-3 | line-3-0685-0403-s016963 | reverse | revenue | 1 | pending |
| line-3 | line-3-0811-0351-s020449 | forward | revenue | 1 | pending |
| line-3 | line-3-0811-0351-s020449 | reverse | revenue | 1 | pending |
| line-3 | line-3-0564-0508-s027267 | forward | revenue | 1 | pending |
| line-3 | line-3-0564-0508-s027267 | reverse | spare | 1 | pending |
| line-3 | line-3-0336-0645-s032880 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**40 trainsets exceed the reference platform envelope**, requiring **3,400.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0023-1227-s000000 | 4 | 2 | 2 | 170.0 |
| line-1-0186-1061-s005429 | 8 | 2 | 6 | 510.0 |
| line-1-0353-0875-s010894 | 7 | 2 | 5 | 425.0 |
| line-1-0444-0778-s013904 | 6 | 2 | 4 | 340.0 |
| line-1-0536-0681-s016911 | 6 | 2 | 4 | 340.0 |
| line-1-0629-0584-s019914 | 6 | 4 | 2 | 170.0 |
| line-1-0790-0413-s025183 | 3 | 2 | 1 | 85.0 |
| line-2-0061-0925-s016963 | 2 | 2 | 0 | 0.0 |
| line-2-0183-0821-s012289 | 5 | 2 | 3 | 255.0 |
| line-2-0342-0732-s007636 | 6 | 2 | 4 | 340.0 |
| line-2-0459-0663-s004619 | 6 | 2 | 4 | 340.0 |
| line-2-0575-0593-s001613 | 6 | 2 | 4 | 340.0 |
| line-2-0638-0556-s000000 | 3 | 2 | 1 | 85.0 |
| line-3-0283-0664-s006824 | 2 | 2 | 0 | 0.0 |
| line-3-0289-0675-s000000 | 2 | 2 | 0 | 0.0 |
| line-3-0336-0645-s032880 | 1 | 2 | 0 | 0.0 |
| line-3-0445-0622-s010392 | 2 | 2 | 0 | 0.0 |
| line-3-0559-0526-s013424 | 1 | 2 | 0 | 0.0 |
| line-3-0564-0508-s027267 | 2 | 2 | 0 | 0.0 |
| line-3-0685-0403-s016963 | 2 | 2 | 0 | 0.0 |
| line-3-0811-0351-s020449 | 2 | 2 | 0 | 0.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-africa/Guinea/Conakry/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
