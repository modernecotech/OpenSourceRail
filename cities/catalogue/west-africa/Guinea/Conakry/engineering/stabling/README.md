# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **44 trainsets at stations + 41 at depots = 85 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **FAIL**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0790-0413-s025183 | line-1 | declared-depot | 23 | 1,955.0 | 6 |
| line-2-0638-0556-s000000 | line-2 | declared-depot | 16 | 1,360.0 | 5 |
| line-3-0289-0675-s000000 | line-3 | declared-depot | 2 | 170.0 | 3 |

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
| line-1 | line-1-0712-0495-s022674 | station | forward | revenue | 1 |
| line-1 | line-1-0712-0495-s022674 | station | reverse | revenue | 1 |
| line-1 | line-1-0790-0413-s025183 | station | reverse | revenue | 2 |
| line-2 | line-2-0061-0925-s016963 | station | reverse | revenue | 2 |
| line-2 | line-2-0183-0821-s012289 | station | forward | revenue | 1 |
| line-2 | line-2-0183-0821-s012289 | station | reverse | revenue | 1 |
| line-2 | line-2-0342-0732-s007636 | station | forward | revenue | 1 |
| line-2 | line-2-0342-0732-s007636 | station | reverse | revenue | 1 |
| line-2 | line-2-0423-0684-s005560 | station | forward | revenue | 1 |
| line-2 | line-2-0423-0684-s005560 | station | reverse | revenue | 1 |
| line-2 | line-2-0503-0636-s003480 | station | forward | revenue | 1 |
| line-2 | line-2-0503-0636-s003480 | station | reverse | revenue | 1 |
| line-2 | line-2-0575-0593-s001613 | station | forward | revenue | 1 |
| line-2 | line-2-0575-0593-s001613 | station | reverse | revenue | 1 |
| line-2 | line-2-0638-0556-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0263-0687-s006528 | station | reverse | revenue | 1 |
| line-3 | line-3-0289-0675-s000000 | station | forward | revenue | 1 |
| line-3 | line-3-0289-0675-s000000 | station | reverse | revenue | 1 |
| line-3 | line-3-0390-0631-s009532 | station | forward | revenue | 1 |
| line-3 | line-3-0496-0624-s011710 | station | forward | revenue | 1 |
| line-3 | line-3-0496-0624-s011710 | station | reverse | revenue | 1 |
| line-3 | line-3-0566-0561-s013632 | station | reverse | revenue | 1 |
| line-3 | line-3-0619-0528-s029578 | station | forward | revenue | 1 |
| line-3 | line-3-0619-0528-s029578 | station | reverse | revenue | 1 |
| line-3 | line-3-0642-0514-s015541 | station | forward | revenue | 1 |
| line-3 | line-3-0691-0474-s027586 | station | forward | revenue | 1 |
| line-3 | line-3-0718-0446-s017742 | station | forward | revenue | 1 |
| line-3 | line-3-0718-0446-s017742 | station | reverse | revenue | 1 |
| line-3 | line-3-0737-0392-s025564 | station | reverse | revenue | 1 |
| line-1 | line-1-0790-0413-s025183 | depot | — | revenue | 19 |
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

Operating allocation: **85 trainsets at 27 stations**; largest initial station queue **6**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **76 revenue, 6 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **54 positions**; **31 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **13 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0023-1227-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0186-1061-s005429 | forward | revenue | 3 | pending |
| line-1 | line-1-0186-1061-s005429 | reverse | revenue | 3 | pending |
| line-1 | line-1-0353-0875-s010894 | forward | revenue | 3 | pending |
| line-1 | line-1-0353-0875-s010894 | reverse | revenue | 3 | pending |
| line-1 | line-1-0444-0778-s013904 | forward | revenue | 3 | pending |
| line-1 | line-1-0444-0778-s013904 | reverse | revenue | 3 | pending |
| line-1 | line-1-0536-0681-s016911 | forward | revenue | 2 | pending |
| line-1 | line-1-0536-0681-s016911 | reverse | revenue | 2 | pending |
| line-1 | line-1-0629-0584-s019914 | forward | revenue | 2 | pending |
| line-1 | line-1-0629-0584-s019914 | reverse | revenue | 2 | pending |
| line-1 | line-1-0712-0495-s022674 | forward | revenue | 2 | pending |
| line-1 | line-1-0712-0495-s022674 | reverse | revenue | 2 | pending |
| line-1 | line-1-0790-0413-s025183 | reverse | revenue | 2 | pending |
| line-1 | line-1-0536-0681-s016911 | forward | spare | 1 | pending |
| line-1 | line-1-0536-0681-s016911 | reverse | spare | 1 | pending |
| line-1 | line-1-0629-0584-s019914 | forward | spare | 1 | pending |
| line-1 | line-1-0629-0584-s019914 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0638-0556-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0575-0593-s001613 | forward | revenue | 3 | pending |
| line-2 | line-2-0575-0593-s001613 | reverse | revenue | 3 | pending |
| line-2 | line-2-0503-0636-s003480 | forward | revenue | 2 | pending |
| line-2 | line-2-0503-0636-s003480 | reverse | revenue | 2 | pending |
| line-2 | line-2-0423-0684-s005560 | forward | revenue | 2 | pending |
| line-2 | line-2-0423-0684-s005560 | reverse | revenue | 2 | pending |
| line-2 | line-2-0342-0732-s007636 | forward | revenue | 2 | pending |
| line-2 | line-2-0342-0732-s007636 | reverse | revenue | 2 | pending |
| line-2 | line-2-0183-0821-s012289 | forward | revenue | 2 | pending |
| line-2 | line-2-0183-0821-s012289 | reverse | revenue | 2 | pending |
| line-2 | line-2-0061-0925-s016963 | reverse | revenue | 2 | pending |
| line-2 | line-2-0503-0636-s003480 | forward | spare | 1 | pending |
| line-2 | line-2-0503-0636-s003480 | reverse | spare | 1 | pending |
| line-2 | line-2-0423-0684-s005560 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0289-0675-s000000 | forward | revenue | 1 | pending |
| line-3 | line-3-0289-0675-s000000 | reverse | revenue | 1 | pending |
| line-3 | line-3-0263-0687-s006528 | reverse | revenue | 1 | pending |
| line-3 | line-3-0390-0631-s009532 | forward | revenue | 1 | pending |
| line-3 | line-3-0496-0624-s011710 | forward | revenue | 1 | pending |
| line-3 | line-3-0496-0624-s011710 | reverse | revenue | 1 | pending |
| line-3 | line-3-0566-0561-s013632 | reverse | revenue | 1 | pending |
| line-3 | line-3-0642-0514-s015541 | forward | revenue | 1 | pending |
| line-3 | line-3-0718-0446-s017742 | forward | revenue | 1 | pending |
| line-3 | line-3-0718-0446-s017742 | reverse | revenue | 1 | pending |
| line-3 | line-3-0737-0392-s025564 | reverse | revenue | 1 | pending |
| line-3 | line-3-0691-0474-s027586 | forward | revenue | 1 | pending |
| line-3 | line-3-0619-0528-s029578 | forward | revenue | 1 | pending |
| line-3 | line-3-0619-0528-s029578 | reverse | revenue | 1 | pending |
| line-3 | line-3-0542-0585-s031591 | reverse | spare | 1 | pending |
| line-3 | line-3-0411-0631-s034592 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**31 trainsets exceed the reference platform envelope**, requiring **2,635.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0023-1227-s000000 | 3 | 2 | 1 | 85.0 |
| line-1-0186-1061-s005429 | 6 | 2 | 4 | 340.0 |
| line-1-0353-0875-s010894 | 6 | 2 | 4 | 340.0 |
| line-1-0444-0778-s013904 | 6 | 2 | 4 | 340.0 |
| line-1-0536-0681-s016911 | 6 | 2 | 4 | 340.0 |
| line-1-0629-0584-s019914 | 6 | 4 | 2 | 170.0 |
| line-1-0712-0495-s022674 | 4 | 4 | 0 | 0.0 |
| line-1-0790-0413-s025183 | 2 | 2 | 0 | 0.0 |
| line-2-0061-0925-s016963 | 2 | 2 | 0 | 0.0 |
| line-2-0183-0821-s012289 | 4 | 2 | 2 | 170.0 |
| line-2-0342-0732-s007636 | 4 | 2 | 2 | 170.0 |
| line-2-0423-0684-s005560 | 5 | 2 | 3 | 255.0 |
| line-2-0503-0636-s003480 | 6 | 4 | 2 | 170.0 |
| line-2-0575-0593-s001613 | 6 | 4 | 2 | 170.0 |
| line-2-0638-0556-s000000 | 3 | 2 | 1 | 85.0 |
| line-3-0263-0687-s006528 | 1 | 2 | 0 | 0.0 |
| line-3-0289-0675-s000000 | 2 | 2 | 0 | 0.0 |
| line-3-0390-0631-s009532 | 1 | 2 | 0 | 0.0 |
| line-3-0411-0631-s034592 | 1 | 2 | 0 | 0.0 |
| line-3-0496-0624-s011710 | 2 | 4 | 0 | 0.0 |
| line-3-0542-0585-s031591 | 1 | 4 | 0 | 0.0 |
| line-3-0566-0561-s013632 | 1 | 4 | 0 | 0.0 |
| line-3-0619-0528-s029578 | 2 | 4 | 0 | 0.0 |
| line-3-0642-0514-s015541 | 1 | 2 | 0 | 0.0 |
| line-3-0691-0474-s027586 | 1 | 4 | 0 | 0.0 |
| line-3-0718-0446-s017742 | 2 | 2 | 0 | 0.0 |
| line-3-0737-0392-s025564 | 1 | 2 | 0 | 0.0 |

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
