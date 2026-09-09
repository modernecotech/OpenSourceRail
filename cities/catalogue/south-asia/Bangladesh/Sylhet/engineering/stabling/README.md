# Station and depot overnight allocation

Plan: **38 trainsets at stations + 71 at depots = 109 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at declared depots.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot station | Stabling positions required | Usable slot length m | Workshop bays |
|---|---:|---:|---:|
| line-2-0274-0567-s024135 | 71 | 4,224.5 | 17 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0393-0371-s014212 | station | reverse | revenue | 2 |
| line-1 | line-1-0431-0448-s012039 | station | forward | revenue | 1 |
| line-1 | line-1-0431-0448-s012039 | station | reverse | revenue | 1 |
| line-1 | line-1-0479-0844-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0485-0509-s009876 | station | forward | revenue | 1 |
| line-1 | line-1-0485-0509-s009876 | station | reverse | revenue | 1 |
| line-1 | line-1-0548-0731-s003003 | station | forward | revenue | 1 |
| line-1 | line-1-0548-0731-s003003 | station | reverse | revenue | 1 |
| line-1 | line-1-0551-0552-s007713 | station | forward | revenue | 1 |
| line-1 | line-1-0551-0552-s007713 | station | reverse | revenue | 1 |
| line-1 | line-1-0582-0615-s006020 | station | forward | revenue | 1 |
| line-1 | line-1-0582-0615-s006020 | station | reverse | revenue | 1 |
| line-2 | line-2-0274-0567-s024135 | station | reverse | revenue | 2 |
| line-2 | line-2-0406-0600-s020192 | station | forward | revenue | 1 |
| line-2 | line-2-0406-0600-s020192 | station | reverse | revenue | 1 |
| line-2 | line-2-0497-0607-s018215 | station | forward | revenue | 1 |
| line-2 | line-2-0497-0607-s018215 | station | reverse | revenue | 1 |
| line-2 | line-2-0551-0552-s016256 | station | forward | revenue | 1 |
| line-2 | line-2-0551-0552-s016256 | station | reverse | revenue | 1 |
| line-2 | line-2-0597-0518-s014439 | station | forward | revenue | 1 |
| line-2 | line-2-0597-0518-s014439 | station | reverse | revenue | 1 |
| line-2 | line-2-0716-0478-s011431 | station | forward | revenue | 1 |
| line-2 | line-2-0716-0478-s011431 | station | reverse | revenue | 1 |
| line-2 | line-2-1084-0152-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0454-0347-s011302 | station | reverse | revenue | 2 |
| line-3 | line-3-0537-0433-s008357 | station | forward | revenue | 1 |
| line-3 | line-3-0537-0433-s008357 | station | reverse | revenue | 1 |
| line-3 | line-3-0551-0552-s005434 | station | forward | revenue | 1 |
| line-3 | line-3-0551-0552-s005434 | station | reverse | revenue | 1 |
| line-3 | line-3-0631-0604-s003010 | station | forward | revenue | 1 |
| line-3 | line-3-0631-0604-s003010 | station | reverse | revenue | 1 |
| line-3 | line-3-0676-0728-s000000 | station | forward | revenue | 2 |
| line-1 | line-2-0274-0567-s024135 | depot | — | revenue | 14 |
| line-1 | line-2-0274-0567-s024135 | depot | — | spare | 2 |
| line-1 | line-2-0274-0567-s024135 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0274-0567-s024135 | depot | — | revenue | 33 |
| line-2 | line-2-0274-0567-s024135 | depot | — | spare | 4 |
| line-2 | line-2-0274-0567-s024135 | depot | — | cold_reserve | 1 |
| line-3 | line-2-0274-0567-s024135 | depot | — | revenue | 13 |
| line-3 | line-2-0274-0567-s024135 | depot | — | spare | 2 |
| line-3 | line-2-0274-0567-s024135 | depot | — | cold_reserve | 1 |

Interline access to the assigned depot must be detailed for: line-1 (17 trains), line-3 (16 trains).

## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **109 trainsets at 19 stations**; largest initial station queue **10**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **98 revenue, 8 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **38 positions**; **71 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **18 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0479-0844-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0548-0731-s003003 | forward | revenue | 3 | pending |
| line-1 | line-1-0548-0731-s003003 | reverse | revenue | 3 | pending |
| line-1 | line-1-0582-0615-s006020 | forward | revenue | 3 | pending |
| line-1 | line-1-0582-0615-s006020 | reverse | revenue | 2 | pending |
| line-1 | line-1-0551-0552-s007713 | forward | revenue | 2 | pending |
| line-1 | line-1-0551-0552-s007713 | reverse | revenue | 2 | pending |
| line-1 | line-1-0485-0509-s009876 | forward | revenue | 2 | pending |
| line-1 | line-1-0485-0509-s009876 | reverse | revenue | 2 | pending |
| line-1 | line-1-0431-0448-s012039 | forward | revenue | 2 | pending |
| line-1 | line-1-0431-0448-s012039 | reverse | revenue | 2 | pending |
| line-1 | line-1-0393-0371-s014212 | reverse | revenue | 2 | pending |
| line-1 | line-1-0582-0615-s006020 | reverse | spare | 1 | pending |
| line-1 | line-1-0551-0552-s007713 | forward | spare | 1 | pending |
| line-1 | line-1-0551-0552-s007713 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-1084-0152-s000000 | forward | revenue | 4 | pending |
| line-2 | line-2-0716-0478-s011431 | forward | revenue | 4 | pending |
| line-2 | line-2-0716-0478-s011431 | reverse | revenue | 4 | pending |
| line-2 | line-2-0597-0518-s014439 | forward | revenue | 4 | pending |
| line-2 | line-2-0597-0518-s014439 | reverse | revenue | 4 | pending |
| line-2 | line-2-0551-0552-s016256 | forward | revenue | 4 | pending |
| line-2 | line-2-0551-0552-s016256 | reverse | revenue | 4 | pending |
| line-2 | line-2-0497-0607-s018215 | forward | revenue | 4 | pending |
| line-2 | line-2-0497-0607-s018215 | reverse | revenue | 4 | pending |
| line-2 | line-2-0406-0600-s020192 | forward | revenue | 4 | pending |
| line-2 | line-2-0406-0600-s020192 | reverse | revenue | 4 | pending |
| line-2 | line-2-0274-0567-s024135 | reverse | revenue | 3 | pending |
| line-2 | line-2-0274-0567-s024135 | reverse | spare | 1 | pending |
| line-2 | line-2-1084-0152-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0716-0478-s011431 | forward | spare | 1 | pending |
| line-2 | line-2-0716-0478-s011431 | reverse | spare | 1 | pending |
| line-2 | line-2-0597-0518-s014439 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0676-0728-s000000 | forward | revenue | 3 | pending |
| line-3 | line-3-0631-0604-s003010 | forward | revenue | 3 | pending |
| line-3 | line-3-0631-0604-s003010 | reverse | revenue | 3 | pending |
| line-3 | line-3-0551-0552-s005434 | forward | revenue | 3 | pending |
| line-3 | line-3-0551-0552-s005434 | reverse | revenue | 3 | pending |
| line-3 | line-3-0537-0433-s008357 | forward | revenue | 3 | pending |
| line-3 | line-3-0537-0433-s008357 | reverse | revenue | 3 | pending |
| line-3 | line-3-0454-0347-s011302 | reverse | revenue | 2 | pending |
| line-3 | line-3-0454-0347-s011302 | reverse | spare | 1 | pending |
| line-3 | line-3-0676-0728-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0631-0604-s003010 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**65 trainsets exceed the reference platform envelope**, requiring **3,867.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0393-0371-s014212 | 2 | 2 | 0 | 0.0 |
| line-1-0431-0448-s012039 | 4 | 2 | 2 | 119.0 |
| line-1-0479-0844-s000000 | 3 | 2 | 1 | 59.5 |
| line-1-0485-0509-s009876 | 4 | 2 | 2 | 119.0 |
| line-1-0548-0731-s003003 | 6 | 2 | 4 | 238.0 |
| line-1-0551-0552-s007713 | 6 | 4 | 2 | 119.0 |
| line-1-0582-0615-s006020 | 6 | 2 | 4 | 238.0 |
| line-2-0274-0567-s024135 | 4 | 2 | 2 | 119.0 |
| line-2-0406-0600-s020192 | 8 | 2 | 6 | 357.0 |
| line-2-0497-0607-s018215 | 8 | 2 | 6 | 357.0 |
| line-2-0551-0552-s016256 | 8 | 4 | 4 | 238.0 |
| line-2-0597-0518-s014439 | 9 | 2 | 7 | 416.5 |
| line-2-0716-0478-s011431 | 10 | 2 | 8 | 476.0 |
| line-2-1084-0152-s000000 | 5 | 2 | 3 | 178.5 |
| line-3-0454-0347-s011302 | 3 | 2 | 1 | 59.5 |
| line-3-0537-0433-s008357 | 6 | 2 | 4 | 238.0 |
| line-3-0551-0552-s005434 | 6 | 4 | 2 | 119.0 |
| line-3-0631-0604-s003010 | 7 | 2 | 5 | 297.5 |
| line-3-0676-0728-s000000 | 4 | 2 | 2 | 119.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/south-asia/Bangladesh/Sylhet/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
