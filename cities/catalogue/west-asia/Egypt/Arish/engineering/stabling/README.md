# Station and depot overnight allocation

Plan: **16 trainsets at stations + 22 at depots = 38 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at declared depots.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot station | Stabling positions required | Usable slot length m | Workshop bays |
|---|---:|---:|---:|
| line-1-0307-0518-s012933 | 22 | 1,078.0 | 6 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0307-0518-s012933 | station | reverse | revenue | 2 |
| line-1 | line-1-0359-0450-s010861 | station | forward | revenue | 1 |
| line-1 | line-1-0359-0450-s010861 | station | reverse | revenue | 1 |
| line-1 | line-1-0381-0389-s008785 | station | forward | revenue | 1 |
| line-1 | line-1-0381-0389-s008785 | station | reverse | revenue | 1 |
| line-1 | line-1-0437-0446-s006727 | station | forward | revenue | 1 |
| line-1 | line-1-0437-0446-s006727 | station | reverse | revenue | 1 |
| line-1 | line-1-0697-0528-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0349-0427-s004328 | station | reverse | revenue | 2 |
| line-2 | line-2-0368-0517-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0381-0389-s003032 | station | forward | revenue | 1 |
| line-2 | line-2-0381-0389-s003032 | station | reverse | revenue | 1 |
| line-1 | line-1-0307-0518-s012933 | depot | — | revenue | 13 |
| line-1 | line-1-0307-0518-s012933 | depot | — | spare | 2 |
| line-1 | line-1-0307-0518-s012933 | depot | — | cold_reserve | 1 |
| line-2 | line-1-0307-0518-s012933 | depot | — | revenue | 4 |
| line-2 | line-1-0307-0518-s012933 | depot | — | spare | 1 |
| line-2 | line-1-0307-0518-s012933 | depot | — | cold_reserve | 1 |

Interline access to the assigned depot must be detailed for: line-2 (6 trains).

## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **38 trainsets at 8 stations**; largest initial station queue **7**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **33 revenue, 3 spare, 2 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **16 positions**; **22 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **8 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0697-0528-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0437-0446-s006727 | forward | revenue | 3 | pending |
| line-1 | line-1-0437-0446-s006727 | reverse | revenue | 3 | pending |
| line-1 | line-1-0381-0389-s008785 | forward | revenue | 3 | pending |
| line-1 | line-1-0381-0389-s008785 | reverse | revenue | 3 | pending |
| line-1 | line-1-0359-0450-s010861 | forward | revenue | 3 | pending |
| line-1 | line-1-0359-0450-s010861 | reverse | revenue | 3 | pending |
| line-1 | line-1-0307-0518-s012933 | reverse | revenue | 2 | pending |
| line-1 | line-1-0307-0518-s012933 | reverse | spare | 1 | pending |
| line-1 | line-1-0697-0528-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0437-0446-s006727 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0368-0517-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0381-0389-s003032 | forward | revenue | 3 | pending |
| line-2 | line-2-0381-0389-s003032 | reverse | revenue | 2 | pending |
| line-2 | line-2-0349-0427-s004328 | reverse | revenue | 2 | pending |
| line-2 | line-2-0381-0389-s003032 | reverse | spare | 1 | pending |
| line-2 | line-2-0349-0427-s004328 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**16 trainsets exceed the reference platform envelope**, requiring **784.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0307-0518-s012933 | 3 | 2 | 1 | 49.0 |
| line-1-0359-0450-s010861 | 6 | 4 | 2 | 98.0 |
| line-1-0381-0389-s008785 | 6 | 4 | 2 | 98.0 |
| line-1-0437-0446-s006727 | 7 | 2 | 5 | 245.0 |
| line-1-0697-0528-s000000 | 4 | 2 | 2 | 98.0 |
| line-2-0349-0427-s004328 | 3 | 2 | 1 | 49.0 |
| line-2-0368-0517-s000000 | 3 | 2 | 1 | 49.0 |
| line-2-0381-0389-s003032 | 6 | 4 | 2 | 98.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Egypt/Arish/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
