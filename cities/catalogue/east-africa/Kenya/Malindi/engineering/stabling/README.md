# Station and depot overnight allocation

Plan: **28 trainsets at stations + 33 at depots = 61 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at declared depots.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot station | Stabling positions required | Usable slot length m | Workshop bays |
|---|---:|---:|---:|
| line-2-0021-0316-s010363 | 33 | 1,617.0 | 10 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0117-0168-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0238-0242-s003033 | station | forward | revenue | 1 |
| line-1 | line-1-0238-0242-s003033 | station | reverse | revenue | 1 |
| line-1 | line-1-0351-0305-s006038 | station | forward | revenue | 1 |
| line-1 | line-1-0351-0305-s006038 | station | reverse | revenue | 1 |
| line-1 | line-1-0353-0364-s007390 | station | forward | revenue | 1 |
| line-1 | line-1-0353-0364-s007390 | station | reverse | revenue | 1 |
| line-1 | line-1-0412-0420-s010059 | station | reverse | revenue | 2 |
| line-2 | line-2-0021-0316-s010363 | station | reverse | revenue | 2 |
| line-2 | line-2-0188-0350-s006597 | station | forward | revenue | 1 |
| line-2 | line-2-0188-0350-s006597 | station | reverse | revenue | 1 |
| line-2 | line-2-0271-0376-s004722 | station | forward | revenue | 1 |
| line-2 | line-2-0271-0376-s004722 | station | reverse | revenue | 1 |
| line-2 | line-2-0353-0364-s002836 | station | forward | revenue | 1 |
| line-2 | line-2-0353-0364-s002836 | station | reverse | revenue | 1 |
| line-2 | line-2-0427-0275-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0033-0391-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0270-0402-s004831 | station | forward | revenue | 1 |
| line-3 | line-3-0270-0402-s004831 | station | reverse | revenue | 1 |
| line-3 | line-3-0353-0364-s007634 | station | forward | revenue | 1 |
| line-3 | line-3-0353-0364-s007634 | station | reverse | revenue | 1 |
| line-3 | line-3-0360-0410-s009018 | station | reverse | revenue | 2 |
| line-1 | line-2-0021-0316-s010363 | depot | — | revenue | 9 |
| line-1 | line-2-0021-0316-s010363 | depot | — | spare | 1 |
| line-1 | line-2-0021-0316-s010363 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0021-0316-s010363 | depot | — | revenue | 9 |
| line-2 | line-2-0021-0316-s010363 | depot | — | spare | 1 |
| line-2 | line-2-0021-0316-s010363 | depot | — | cold_reserve | 1 |
| line-3 | line-2-0021-0316-s010363 | depot | — | revenue | 9 |
| line-3 | line-2-0021-0316-s010363 | depot | — | spare | 1 |
| line-3 | line-2-0021-0316-s010363 | depot | — | cold_reserve | 1 |

Interline access to the assigned depot must be detailed for: line-1 (11 trains), line-3 (11 trains).

## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **61 trainsets at 14 stations**; largest initial station queue **6**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **55 revenue, 3 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **28 positions**; **33 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **12 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0117-0168-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0238-0242-s003033 | forward | revenue | 3 | pending |
| line-1 | line-1-0238-0242-s003033 | reverse | revenue | 3 | pending |
| line-1 | line-1-0351-0305-s006038 | forward | revenue | 2 | pending |
| line-1 | line-1-0351-0305-s006038 | reverse | revenue | 2 | pending |
| line-1 | line-1-0353-0364-s007390 | forward | revenue | 2 | pending |
| line-1 | line-1-0353-0364-s007390 | reverse | revenue | 2 | pending |
| line-1 | line-1-0412-0420-s010059 | reverse | revenue | 2 | pending |
| line-1 | line-1-0351-0305-s006038 | forward | spare | 1 | pending |
| line-1 | line-1-0351-0305-s006038 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0427-0275-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0353-0364-s002836 | forward | revenue | 3 | pending |
| line-2 | line-2-0353-0364-s002836 | reverse | revenue | 3 | pending |
| line-2 | line-2-0271-0376-s004722 | forward | revenue | 2 | pending |
| line-2 | line-2-0271-0376-s004722 | reverse | revenue | 2 | pending |
| line-2 | line-2-0188-0350-s006597 | forward | revenue | 2 | pending |
| line-2 | line-2-0188-0350-s006597 | reverse | revenue | 2 | pending |
| line-2 | line-2-0021-0316-s010363 | reverse | revenue | 2 | pending |
| line-2 | line-2-0271-0376-s004722 | forward | spare | 1 | pending |
| line-2 | line-2-0271-0376-s004722 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0033-0391-s000000 | forward | revenue | 3 | pending |
| line-3 | line-3-0270-0402-s004831 | forward | revenue | 3 | pending |
| line-3 | line-3-0270-0402-s004831 | reverse | revenue | 3 | pending |
| line-3 | line-3-0353-0364-s007634 | forward | revenue | 3 | pending |
| line-3 | line-3-0353-0364-s007634 | reverse | revenue | 3 | pending |
| line-3 | line-3-0360-0410-s009018 | reverse | revenue | 2 | pending |
| line-3 | line-3-0360-0410-s009018 | reverse | spare | 1 | pending |
| line-3 | line-3-0033-0391-s000000 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**23 trainsets exceed the reference platform envelope**, requiring **1,127.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0117-0168-s000000 | 3 | 2 | 1 | 49.0 |
| line-1-0238-0242-s003033 | 6 | 2 | 4 | 196.0 |
| line-1-0351-0305-s006038 | 6 | 2 | 4 | 196.0 |
| line-1-0353-0364-s007390 | 4 | 4 | 0 | 0.0 |
| line-1-0412-0420-s010059 | 2 | 2 | 0 | 0.0 |
| line-2-0021-0316-s010363 | 2 | 2 | 0 | 0.0 |
| line-2-0188-0350-s006597 | 4 | 2 | 2 | 98.0 |
| line-2-0271-0376-s004722 | 6 | 4 | 2 | 98.0 |
| line-2-0353-0364-s002836 | 6 | 4 | 2 | 98.0 |
| line-2-0427-0275-s000000 | 3 | 2 | 1 | 49.0 |
| line-3-0033-0391-s000000 | 4 | 2 | 2 | 98.0 |
| line-3-0270-0402-s004831 | 6 | 4 | 2 | 98.0 |
| line-3-0353-0364-s007634 | 6 | 4 | 2 | 98.0 |
| line-3-0360-0410-s009018 | 3 | 2 | 1 | 49.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Kenya/Malindi/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
