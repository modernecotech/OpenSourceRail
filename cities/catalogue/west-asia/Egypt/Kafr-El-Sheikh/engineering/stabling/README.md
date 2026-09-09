# Station and depot overnight allocation

Plan: **22 trainsets at stations + 43 at depots = 65 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at declared depots.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot station | Stabling positions required | Usable slot length m | Workshop bays |
|---|---:|---:|---:|
| line-1-0490-0183-s015744 | 43 | 2,107.0 | 10 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0120-0669-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0277-0448-s005721 | station | forward | revenue | 1 |
| line-1 | line-1-0277-0448-s005721 | station | reverse | revenue | 1 |
| line-1 | line-1-0376-0378-s009010 | station | forward | revenue | 1 |
| line-1 | line-1-0376-0378-s009010 | station | reverse | revenue | 1 |
| line-1 | line-1-0490-0183-s015744 | station | reverse | revenue | 2 |
| line-2 | line-2-0217-0202-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0316-0305-s003132 | station | forward | revenue | 1 |
| line-2 | line-2-0316-0305-s003132 | station | reverse | revenue | 1 |
| line-2 | line-2-0376-0378-s005867 | station | forward | revenue | 1 |
| line-2 | line-2-0376-0378-s005867 | station | reverse | revenue | 1 |
| line-2 | line-2-0512-0417-s009573 | station | reverse | revenue | 2 |
| line-3 | line-3-0291-0458-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0376-0378-s003122 | station | forward | revenue | 1 |
| line-3 | line-3-0376-0378-s003122 | station | reverse | revenue | 1 |
| line-3 | line-3-0505-0432-s006312 | station | reverse | revenue | 2 |
| line-1 | line-1-0490-0183-s015744 | depot | — | revenue | 20 |
| line-1 | line-1-0490-0183-s015744 | depot | — | spare | 2 |
| line-1 | line-1-0490-0183-s015744 | depot | — | cold_reserve | 1 |
| line-2 | line-1-0490-0183-s015744 | depot | — | revenue | 10 |
| line-2 | line-1-0490-0183-s015744 | depot | — | spare | 1 |
| line-2 | line-1-0490-0183-s015744 | depot | — | cold_reserve | 1 |
| line-3 | line-1-0490-0183-s015744 | depot | — | revenue | 6 |
| line-3 | line-1-0490-0183-s015744 | depot | — | spare | 1 |
| line-3 | line-1-0490-0183-s015744 | depot | — | cold_reserve | 1 |

Interline access to the assigned depot must be detailed for: line-2 (12 trains), line-3 (8 trains).

## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **65 trainsets at 11 stations**; largest initial station queue **10**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **58 revenue, 4 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **22 positions**; **43 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **11 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0120-0669-s000000 | forward | revenue | 5 | pending |
| line-1 | line-1-0277-0448-s005721 | forward | revenue | 5 | pending |
| line-1 | line-1-0277-0448-s005721 | reverse | revenue | 5 | pending |
| line-1 | line-1-0376-0378-s009010 | forward | revenue | 5 | pending |
| line-1 | line-1-0376-0378-s009010 | reverse | revenue | 4 | pending |
| line-1 | line-1-0490-0183-s015744 | reverse | revenue | 4 | pending |
| line-1 | line-1-0376-0378-s009010 | reverse | spare | 1 | pending |
| line-1 | line-1-0490-0183-s015744 | reverse | spare | 1 | pending |
| line-1 | line-1-0120-0669-s000000 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0217-0202-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0316-0305-s003132 | forward | revenue | 3 | pending |
| line-2 | line-2-0316-0305-s003132 | reverse | revenue | 3 | pending |
| line-2 | line-2-0376-0378-s005867 | forward | revenue | 3 | pending |
| line-2 | line-2-0376-0378-s005867 | reverse | revenue | 3 | pending |
| line-2 | line-2-0512-0417-s009573 | reverse | revenue | 3 | pending |
| line-2 | line-2-0217-0202-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0316-0305-s003132 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0291-0458-s000000 | forward | revenue | 3 | pending |
| line-3 | line-3-0376-0378-s003122 | forward | revenue | 3 | pending |
| line-3 | line-3-0376-0378-s003122 | reverse | revenue | 3 | pending |
| line-3 | line-3-0505-0432-s006312 | reverse | revenue | 3 | pending |
| line-3 | line-3-0291-0458-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0376-0378-s003122 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**35 trainsets exceed the reference platform envelope**, requiring **1,715.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0120-0669-s000000 | 6 | 2 | 4 | 196.0 |
| line-1-0277-0448-s005721 | 10 | 4 | 6 | 294.0 |
| line-1-0376-0378-s009010 | 10 | 4 | 6 | 294.0 |
| line-1-0490-0183-s015744 | 5 | 2 | 3 | 147.0 |
| line-2-0217-0202-s000000 | 4 | 2 | 2 | 98.0 |
| line-2-0316-0305-s003132 | 7 | 2 | 5 | 245.0 |
| line-2-0376-0378-s005867 | 6 | 4 | 2 | 98.0 |
| line-2-0512-0417-s009573 | 3 | 2 | 1 | 49.0 |
| line-3-0291-0458-s000000 | 4 | 2 | 2 | 98.0 |
| line-3-0376-0378-s003122 | 7 | 4 | 3 | 147.0 |
| line-3-0505-0432-s006312 | 3 | 2 | 1 | 49.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Egypt/Kafr-El-Sheikh/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
