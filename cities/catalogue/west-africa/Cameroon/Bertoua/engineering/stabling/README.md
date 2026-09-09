# Station and depot overnight allocation

Plan: **24 trainsets at stations + 39 at depots = 63 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at declared depots.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot station | Stabling positions required | Usable slot length m | Workshop bays |
|---|---:|---:|---:|
| line-2-0458-0856-s010330 | 39 | 2,320.5 | 10 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0551-0552-s002731 | station | forward | revenue | 1 |
| line-1 | line-1-0551-0552-s002731 | station | reverse | revenue | 1 |
| line-1 | line-1-0571-0618-s004614 | station | forward | revenue | 1 |
| line-1 | line-1-0571-0618-s004614 | station | reverse | revenue | 1 |
| line-1 | line-1-0582-0451-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0665-0763-s009379 | station | reverse | revenue | 2 |
| line-2 | line-2-0458-0856-s010330 | station | reverse | revenue | 2 |
| line-2 | line-2-0512-0478-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0519-0638-s004896 | station | forward | revenue | 1 |
| line-2 | line-2-0519-0638-s004896 | station | reverse | revenue | 1 |
| line-2 | line-2-0551-0552-s002248 | station | forward | revenue | 1 |
| line-2 | line-2-0551-0552-s002248 | station | reverse | revenue | 1 |
| line-3 | line-3-0493-0543-s009644 | station | reverse | revenue | 2 |
| line-3 | line-3-0551-0552-s008150 | station | forward | revenue | 1 |
| line-3 | line-3-0551-0552-s008150 | station | reverse | revenue | 1 |
| line-3 | line-3-0643-0551-s005714 | station | forward | revenue | 1 |
| line-3 | line-3-0643-0551-s005714 | station | reverse | revenue | 1 |
| line-3 | line-3-0860-0665-s000000 | station | forward | revenue | 2 |
| line-1 | line-2-0458-0856-s010330 | depot | — | revenue | 11 |
| line-1 | line-2-0458-0856-s010330 | depot | — | spare | 1 |
| line-1 | line-2-0458-0856-s010330 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0458-0856-s010330 | depot | — | revenue | 11 |
| line-2 | line-2-0458-0856-s010330 | depot | — | spare | 1 |
| line-2 | line-2-0458-0856-s010330 | depot | — | cold_reserve | 1 |
| line-3 | line-2-0458-0856-s010330 | depot | — | revenue | 11 |
| line-3 | line-2-0458-0856-s010330 | depot | — | spare | 1 |
| line-3 | line-2-0458-0856-s010330 | depot | — | cold_reserve | 1 |

Interline access to the assigned depot must be detailed for: line-1 (13 trains), line-3 (13 trains).

## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **63 trainsets at 12 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **57 revenue, 3 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **24 positions**; **39 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **12 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0582-0451-s000000 | forward | revenue | 4 | pending |
| line-1 | line-1-0551-0552-s002731 | forward | revenue | 3 | pending |
| line-1 | line-1-0551-0552-s002731 | reverse | revenue | 3 | pending |
| line-1 | line-1-0571-0618-s004614 | forward | revenue | 3 | pending |
| line-1 | line-1-0571-0618-s004614 | reverse | revenue | 3 | pending |
| line-1 | line-1-0665-0763-s009379 | reverse | revenue | 3 | pending |
| line-1 | line-1-0551-0552-s002731 | forward | spare | 1 | pending |
| line-1 | line-1-0551-0552-s002731 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0512-0478-s000000 | forward | revenue | 4 | pending |
| line-2 | line-2-0551-0552-s002248 | forward | revenue | 3 | pending |
| line-2 | line-2-0551-0552-s002248 | reverse | revenue | 3 | pending |
| line-2 | line-2-0519-0638-s004896 | forward | revenue | 3 | pending |
| line-2 | line-2-0519-0638-s004896 | reverse | revenue | 3 | pending |
| line-2 | line-2-0458-0856-s010330 | reverse | revenue | 3 | pending |
| line-2 | line-2-0551-0552-s002248 | forward | spare | 1 | pending |
| line-2 | line-2-0551-0552-s002248 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0860-0665-s000000 | forward | revenue | 4 | pending |
| line-3 | line-3-0643-0551-s005714 | forward | revenue | 3 | pending |
| line-3 | line-3-0643-0551-s005714 | reverse | revenue | 3 | pending |
| line-3 | line-3-0551-0552-s008150 | forward | revenue | 3 | pending |
| line-3 | line-3-0551-0552-s008150 | reverse | revenue | 3 | pending |
| line-3 | line-3-0493-0543-s009644 | reverse | revenue | 3 | pending |
| line-3 | line-3-0643-0551-s005714 | forward | spare | 1 | pending |
| line-3 | line-3-0643-0551-s005714 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**33 trainsets exceed the reference platform envelope**, requiring **1,963.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0551-0552-s002731 | 8 | 4 | 4 | 238.0 |
| line-1-0571-0618-s004614 | 6 | 2 | 4 | 238.0 |
| line-1-0582-0451-s000000 | 4 | 2 | 2 | 119.0 |
| line-1-0665-0763-s009379 | 3 | 2 | 1 | 59.5 |
| line-2-0458-0856-s010330 | 3 | 2 | 1 | 59.5 |
| line-2-0512-0478-s000000 | 4 | 2 | 2 | 119.0 |
| line-2-0519-0638-s004896 | 6 | 2 | 4 | 238.0 |
| line-2-0551-0552-s002248 | 8 | 4 | 4 | 238.0 |
| line-3-0493-0543-s009644 | 3 | 2 | 1 | 59.5 |
| line-3-0551-0552-s008150 | 6 | 4 | 2 | 119.0 |
| line-3-0643-0551-s005714 | 8 | 2 | 6 | 357.0 |
| line-3-0860-0665-s000000 | 4 | 2 | 2 | 119.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-africa/Cameroon/Bertoua/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
