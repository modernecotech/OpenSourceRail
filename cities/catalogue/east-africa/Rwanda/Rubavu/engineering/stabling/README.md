# Station and depot overnight allocation

Plan: **38 trainsets at stations + 53 at depots = 91 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at declared depots.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot station | Stabling positions required | Usable slot length m | Workshop bays |
|---|---:|---:|---:|
| line-2-0253-0189-s015878 | 53 | 2,597.0 | 14 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0255-0427-s015332 | station | reverse | revenue | 2 |
| line-1 | line-1-0294-0029-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0316-0388-s013394 | station | forward | revenue | 1 |
| line-1 | line-1-0316-0388-s013394 | station | reverse | revenue | 1 |
| line-1 | line-1-0356-0080-s003014 | station | forward | revenue | 1 |
| line-1 | line-1-0356-0080-s003014 | station | reverse | revenue | 1 |
| line-1 | line-1-0369-0347-s011472 | station | forward | revenue | 1 |
| line-1 | line-1-0369-0347-s011472 | station | reverse | revenue | 1 |
| line-1 | line-1-0375-0200-s006026 | station | forward | revenue | 1 |
| line-1 | line-1-0375-0200-s006026 | station | reverse | revenue | 1 |
| line-1 | line-1-0376-0285-s009028 | station | forward | revenue | 1 |
| line-1 | line-1-0376-0285-s009028 | station | reverse | revenue | 1 |
| line-2 | line-2-0253-0189-s015878 | station | reverse | revenue | 2 |
| line-2 | line-2-0311-0264-s013039 | station | forward | revenue | 1 |
| line-2 | line-2-0311-0264-s013039 | station | reverse | revenue | 1 |
| line-2 | line-2-0369-0347-s010215 | station | forward | revenue | 1 |
| line-2 | line-2-0369-0347-s010215 | station | reverse | revenue | 1 |
| line-2 | line-2-0446-0343-s007640 | station | forward | revenue | 1 |
| line-2 | line-2-0446-0343-s007640 | station | reverse | revenue | 1 |
| line-2 | line-2-0552-0402-s004630 | station | forward | revenue | 1 |
| line-2 | line-2-0552-0402-s004630 | station | reverse | revenue | 1 |
| line-2 | line-2-0710-0450-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0205-0212-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0283-0322-s003025 | station | forward | revenue | 1 |
| line-3 | line-3-0283-0322-s003025 | station | reverse | revenue | 1 |
| line-3 | line-3-0369-0347-s005669 | station | forward | revenue | 1 |
| line-3 | line-3-0369-0347-s005669 | station | reverse | revenue | 1 |
| line-3 | line-3-0415-0434-s007969 | station | forward | revenue | 1 |
| line-3 | line-3-0415-0434-s007969 | station | reverse | revenue | 1 |
| line-3 | line-3-0427-0530-s010296 | station | forward | revenue | 1 |
| line-3 | line-3-0427-0530-s010296 | station | reverse | revenue | 1 |
| line-3 | line-3-0492-0723-s014930 | station | reverse | revenue | 2 |
| line-1 | line-2-0253-0189-s015878 | depot | — | revenue | 13 |
| line-1 | line-2-0253-0189-s015878 | depot | — | spare | 2 |
| line-1 | line-2-0253-0189-s015878 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0253-0189-s015878 | depot | — | revenue | 16 |
| line-2 | line-2-0253-0189-s015878 | depot | — | spare | 2 |
| line-2 | line-2-0253-0189-s015878 | depot | — | cold_reserve | 1 |
| line-3 | line-2-0253-0189-s015878 | depot | — | revenue | 15 |
| line-3 | line-2-0253-0189-s015878 | depot | — | spare | 2 |
| line-3 | line-2-0253-0189-s015878 | depot | — | cold_reserve | 1 |

Interline access to the assigned depot must be detailed for: line-1 (16 trains), line-3 (18 trains).

Native hybrid candidate unavailable: interline depot access is absent from the native track graph.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **91 trainsets at 19 stations**; largest initial station queue **6**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **82 revenue, 6 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **38 positions**; **53 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **18 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0294-0029-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0356-0080-s003014 | forward | revenue | 3 | pending |
| line-1 | line-1-0356-0080-s003014 | reverse | revenue | 3 | pending |
| line-1 | line-1-0375-0200-s006026 | forward | revenue | 2 | pending |
| line-1 | line-1-0375-0200-s006026 | reverse | revenue | 2 | pending |
| line-1 | line-1-0376-0285-s009028 | forward | revenue | 2 | pending |
| line-1 | line-1-0376-0285-s009028 | reverse | revenue | 2 | pending |
| line-1 | line-1-0369-0347-s011472 | forward | revenue | 2 | pending |
| line-1 | line-1-0369-0347-s011472 | reverse | revenue | 2 | pending |
| line-1 | line-1-0316-0388-s013394 | forward | revenue | 2 | pending |
| line-1 | line-1-0316-0388-s013394 | reverse | revenue | 2 | pending |
| line-1 | line-1-0255-0427-s015332 | reverse | revenue | 2 | pending |
| line-1 | line-1-0375-0200-s006026 | forward | spare | 1 | pending |
| line-1 | line-1-0375-0200-s006026 | reverse | spare | 1 | pending |
| line-1 | line-1-0376-0285-s009028 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0710-0450-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0552-0402-s004630 | forward | revenue | 3 | pending |
| line-2 | line-2-0552-0402-s004630 | reverse | revenue | 3 | pending |
| line-2 | line-2-0446-0343-s007640 | forward | revenue | 3 | pending |
| line-2 | line-2-0446-0343-s007640 | reverse | revenue | 3 | pending |
| line-2 | line-2-0369-0347-s010215 | forward | revenue | 3 | pending |
| line-2 | line-2-0369-0347-s010215 | reverse | revenue | 3 | pending |
| line-2 | line-2-0311-0264-s013039 | forward | revenue | 3 | pending |
| line-2 | line-2-0311-0264-s013039 | reverse | revenue | 2 | pending |
| line-2 | line-2-0253-0189-s015878 | reverse | revenue | 2 | pending |
| line-2 | line-2-0311-0264-s013039 | reverse | spare | 1 | pending |
| line-2 | line-2-0253-0189-s015878 | reverse | spare | 1 | pending |
| line-2 | line-2-0710-0450-s000000 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0205-0212-s000000 | forward | revenue | 3 | pending |
| line-3 | line-3-0283-0322-s003025 | forward | revenue | 3 | pending |
| line-3 | line-3-0283-0322-s003025 | reverse | revenue | 3 | pending |
| line-3 | line-3-0369-0347-s005669 | forward | revenue | 3 | pending |
| line-3 | line-3-0369-0347-s005669 | reverse | revenue | 3 | pending |
| line-3 | line-3-0415-0434-s007969 | forward | revenue | 3 | pending |
| line-3 | line-3-0415-0434-s007969 | reverse | revenue | 3 | pending |
| line-3 | line-3-0427-0530-s010296 | forward | revenue | 2 | pending |
| line-3 | line-3-0427-0530-s010296 | reverse | revenue | 2 | pending |
| line-3 | line-3-0492-0723-s014930 | reverse | revenue | 2 | pending |
| line-3 | line-3-0427-0530-s010296 | forward | spare | 1 | pending |
| line-3 | line-3-0427-0530-s010296 | reverse | spare | 1 | pending |
| line-3 | line-3-0492-0723-s014930 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**47 trainsets exceed the reference platform envelope**, requiring **2,303.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0255-0427-s015332 | 2 | 2 | 0 | 0.0 |
| line-1-0294-0029-s000000 | 3 | 2 | 1 | 49.0 |
| line-1-0316-0388-s013394 | 4 | 2 | 2 | 98.0 |
| line-1-0356-0080-s003014 | 6 | 2 | 4 | 196.0 |
| line-1-0369-0347-s011472 | 4 | 4 | 0 | 0.0 |
| line-1-0375-0200-s006026 | 6 | 2 | 4 | 196.0 |
| line-1-0376-0285-s009028 | 5 | 2 | 3 | 147.0 |
| line-2-0253-0189-s015878 | 3 | 2 | 1 | 49.0 |
| line-2-0311-0264-s013039 | 6 | 2 | 4 | 196.0 |
| line-2-0369-0347-s010215 | 6 | 4 | 2 | 98.0 |
| line-2-0446-0343-s007640 | 6 | 2 | 4 | 196.0 |
| line-2-0552-0402-s004630 | 6 | 2 | 4 | 196.0 |
| line-2-0710-0450-s000000 | 4 | 2 | 2 | 98.0 |
| line-3-0205-0212-s000000 | 3 | 2 | 1 | 49.0 |
| line-3-0283-0322-s003025 | 6 | 2 | 4 | 196.0 |
| line-3-0369-0347-s005669 | 6 | 4 | 2 | 98.0 |
| line-3-0415-0434-s007969 | 6 | 2 | 4 | 196.0 |
| line-3-0427-0530-s010296 | 6 | 2 | 4 | 196.0 |
| line-3-0492-0723-s014930 | 3 | 2 | 1 | 49.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Rwanda/Rubavu/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
