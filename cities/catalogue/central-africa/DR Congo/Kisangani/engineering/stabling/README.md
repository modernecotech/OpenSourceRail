# Station and depot overnight allocation

Plan: **25 trainsets at stations + 25 at depots = 50 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at declared depots.

Allocation check: **FAIL**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot station | Stabling positions required | Usable slot length m | Workshop bays |
|---|---:|---:|---:|
| line-1-0931-1133-s025786 | 25 | 2,125.0 | 8 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0541-0230-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0624-0501-s007023 | station | forward | revenue | 1 |
| line-1 | line-1-0624-0501-s007023 | station | reverse | revenue | 1 |
| line-1 | line-1-0717-0760-s013679 | station | forward | revenue | 1 |
| line-1 | line-1-0717-0760-s013679 | station | reverse | revenue | 1 |
| line-1 | line-1-0723-0698-s012278 | station | forward | revenue | 1 |
| line-1 | line-1-0723-0698-s012278 | station | reverse | revenue | 1 |
| line-1 | line-1-0798-0802-s016188 | station | forward | revenue | 1 |
| line-1 | line-1-0798-0802-s016188 | station | reverse | revenue | 1 |
| line-1 | line-1-0841-0806-s018323 | station | forward | revenue | 1 |
| line-1 | line-1-0841-0806-s018323 | station | reverse | revenue | 1 |
| line-1 | line-1-0866-0940-s021343 | station | forward | revenue | 1 |
| line-1 | line-1-0866-0940-s021343 | station | reverse | revenue | 1 |
| line-1 | line-1-0931-1133-s025786 | station | reverse | revenue | 2 |
| line-2 | line-2-0697-0843-s006015 | station | forward | revenue | 1 |
| line-2 | line-2-0703-0867-s009030 | station | forward | revenue | 1 |
| line-2 | line-2-0703-0867-s009030 | station | reverse | revenue | 1 |
| line-2 | line-2-0717-0760-s003798 | station | forward | revenue | 1 |
| line-2 | line-2-0775-0702-s001902 | station | reverse | revenue | 1 |
| line-2 | line-2-0794-0628-s000000 | station | forward | revenue | 1 |
| line-2 | line-2-0794-0628-s000000 | station | reverse | revenue | 1 |
| line-2 | line-2-0795-0819-s011675 | station | reverse | revenue | 1 |
| line-2 | line-2-0845-0820-s015185 | station | reverse | revenue | 1 |
| line-1 | line-1-0931-1133-s025786 | depot | — | revenue | 19 |
| line-1 | line-1-0931-1133-s025786 | depot | — | spare | 3 |
| line-1 | line-1-0931-1133-s025786 | depot | — | cold_reserve | 1 |
| line-2 | line-1-0931-1133-s025786 | depot | — | spare | 1 |
| line-2 | line-1-0931-1133-s025786 | depot | — | cold_reserve | 1 |

Interline access to the assigned depot must be detailed for: line-2 (2 trains).

Native hybrid candidate unavailable: morning station allocation is incomplete.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **50 trainsets at 17 stations**; largest initial station queue **6**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **44 revenue, 4 spare, 2 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **34 positions**; **16 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **7 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0541-0230-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0624-0501-s007023 | forward | revenue | 3 | pending |
| line-1 | line-1-0624-0501-s007023 | reverse | revenue | 3 | pending |
| line-1 | line-1-0723-0698-s012278 | forward | revenue | 3 | pending |
| line-1 | line-1-0723-0698-s012278 | reverse | revenue | 3 | pending |
| line-1 | line-1-0717-0760-s013679 | forward | revenue | 3 | pending |
| line-1 | line-1-0717-0760-s013679 | reverse | revenue | 3 | pending |
| line-1 | line-1-0798-0802-s016188 | forward | revenue | 2 | pending |
| line-1 | line-1-0798-0802-s016188 | reverse | revenue | 2 | pending |
| line-1 | line-1-0841-0806-s018323 | forward | revenue | 2 | pending |
| line-1 | line-1-0841-0806-s018323 | reverse | revenue | 2 | pending |
| line-1 | line-1-0866-0940-s021343 | forward | revenue | 2 | pending |
| line-1 | line-1-0866-0940-s021343 | reverse | revenue | 2 | pending |
| line-1 | line-1-0931-1133-s025786 | reverse | revenue | 2 | pending |
| line-1 | line-1-0798-0802-s016188 | forward | spare | 1 | pending |
| line-1 | line-1-0798-0802-s016188 | reverse | spare | 1 | pending |
| line-1 | line-1-0841-0806-s018323 | forward | spare | 1 | pending |
| line-1 | line-1-0841-0806-s018323 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0794-0628-s000000 | forward | revenue | 1 | pending |
| line-2 | line-2-0794-0628-s000000 | reverse | revenue | 1 | pending |
| line-2 | line-2-0775-0702-s001902 | reverse | revenue | 1 | pending |
| line-2 | line-2-0717-0760-s003798 | forward | revenue | 1 | pending |
| line-2 | line-2-0697-0843-s006015 | forward | revenue | 1 | pending |
| line-2 | line-2-0703-0867-s009030 | forward | revenue | 1 | pending |
| line-2 | line-2-0703-0867-s009030 | reverse | revenue | 1 | pending |
| line-2 | line-2-0795-0819-s011675 | reverse | revenue | 1 | pending |
| line-2 | line-2-0845-0820-s015185 | reverse | revenue | 1 | pending |
| line-2 | line-2-0838-0749-s018029 | forward | spare | 1 | pending |
| line-2 | line-2-0811-0668-s020134 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**17 trainsets exceed the reference platform envelope**, requiring **1,445.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0541-0230-s000000 | 3 | 2 | 1 | 85.0 |
| line-1-0624-0501-s007023 | 6 | 2 | 4 | 340.0 |
| line-1-0717-0760-s013679 | 6 | 4 | 2 | 170.0 |
| line-1-0723-0698-s012278 | 6 | 2 | 4 | 340.0 |
| line-1-0798-0802-s016188 | 6 | 4 | 2 | 170.0 |
| line-1-0841-0806-s018323 | 6 | 4 | 2 | 170.0 |
| line-1-0866-0940-s021343 | 4 | 2 | 2 | 170.0 |
| line-1-0931-1133-s025786 | 2 | 2 | 0 | 0.0 |
| line-2-0697-0843-s006015 | 1 | 2 | 0 | 0.0 |
| line-2-0703-0867-s009030 | 2 | 2 | 0 | 0.0 |
| line-2-0717-0760-s003798 | 1 | 4 | 0 | 0.0 |
| line-2-0775-0702-s001902 | 1 | 2 | 0 | 0.0 |
| line-2-0794-0628-s000000 | 2 | 2 | 0 | 0.0 |
| line-2-0795-0819-s011675 | 1 | 4 | 0 | 0.0 |
| line-2-0811-0668-s020134 | 1 | 2 | 0 | 0.0 |
| line-2-0838-0749-s018029 | 1 | 2 | 0 | 0.0 |
| line-2-0845-0820-s015185 | 1 | 4 | 0 | 0.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/central-africa/DR Congo/Kisangani/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
