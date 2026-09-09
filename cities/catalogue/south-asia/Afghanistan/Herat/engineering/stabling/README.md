# Station and depot overnight allocation

Plan: **34 trainsets at stations + 74 at depots = 108 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0707-0431-s013954 | line-1 | storage-at-existing-powered-service-point | 19 | 1,130.5 | 0 |
| line-2-0406-0262-s014286 | line-2 | storage-at-existing-powered-service-point | 19 | 1,130.5 | 0 |
| line-3-0486-1078-s021292 | line-3 | declared-depot | 36 | 2,142.0 | 17 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0423-0728-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0466-0621-s003016 | station | forward | revenue | 1 |
| line-1 | line-1-0466-0621-s003016 | station | reverse | revenue | 1 |
| line-1 | line-1-0557-0586-s006029 | station | forward | revenue | 1 |
| line-1 | line-1-0557-0586-s006029 | station | reverse | revenue | 1 |
| line-1 | line-1-0601-0528-s009033 | station | forward | revenue | 1 |
| line-1 | line-1-0601-0528-s009033 | station | reverse | revenue | 1 |
| line-1 | line-1-0655-0505-s011487 | station | forward | revenue | 1 |
| line-1 | line-1-0655-0505-s011487 | station | reverse | revenue | 1 |
| line-1 | line-1-0707-0431-s013954 | station | reverse | revenue | 2 |
| line-2 | line-2-0406-0262-s014286 | station | reverse | revenue | 2 |
| line-2 | line-2-0476-0467-s009019 | station | forward | revenue | 1 |
| line-2 | line-2-0476-0467-s009019 | station | reverse | revenue | 1 |
| line-2 | line-2-0550-0550-s004289 | station | forward | revenue | 1 |
| line-2 | line-2-0550-0550-s004289 | station | reverse | revenue | 1 |
| line-2 | line-2-0573-0521-s006015 | station | forward | revenue | 1 |
| line-2 | line-2-0573-0521-s006015 | station | reverse | revenue | 1 |
| line-2 | line-2-0574-0595-s003007 | station | forward | revenue | 1 |
| line-2 | line-2-0574-0595-s003007 | station | reverse | revenue | 1 |
| line-2 | line-2-0699-0615-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0289-0190-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0401-0444-s007018 | station | forward | revenue | 1 |
| line-3 | line-3-0401-0444-s007018 | station | reverse | revenue | 1 |
| line-3 | line-3-0401-0713-s012829 | station | forward | revenue | 1 |
| line-3 | line-3-0401-0713-s012829 | station | reverse | revenue | 1 |
| line-3 | line-3-0424-0582-s010019 | station | forward | revenue | 1 |
| line-3 | line-3-0424-0582-s010019 | station | reverse | revenue | 1 |
| line-3 | line-3-0486-1078-s021292 | station | reverse | revenue | 2 |
| line-1 | line-1-0707-0431-s013954 | depot | — | revenue | 16 |
| line-1 | line-1-0707-0431-s013954 | depot | — | spare | 2 |
| line-1 | line-1-0707-0431-s013954 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0406-0262-s014286 | depot | — | revenue | 16 |
| line-2 | line-2-0406-0262-s014286 | depot | — | spare | 2 |
| line-2 | line-2-0406-0262-s014286 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0486-1078-s021292 | depot | — | revenue | 31 |
| line-3 | line-3-0486-1078-s021292 | depot | — | spare | 4 |
| line-3 | line-3-0486-1078-s021292 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/herat-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **108 trainsets at 17 stations**; largest initial station queue **12**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **97 revenue, 8 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **34 positions**; **74 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **17 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0423-0728-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0466-0621-s003016 | forward | revenue | 3 | pending |
| line-1 | line-1-0466-0621-s003016 | reverse | revenue | 3 | pending |
| line-1 | line-1-0557-0586-s006029 | forward | revenue | 3 | pending |
| line-1 | line-1-0557-0586-s006029 | reverse | revenue | 3 | pending |
| line-1 | line-1-0601-0528-s009033 | forward | revenue | 3 | pending |
| line-1 | line-1-0601-0528-s009033 | reverse | revenue | 3 | pending |
| line-1 | line-1-0655-0505-s011487 | forward | revenue | 3 | pending |
| line-1 | line-1-0655-0505-s011487 | reverse | revenue | 2 | pending |
| line-1 | line-1-0707-0431-s013954 | reverse | revenue | 2 | pending |
| line-1 | line-1-0655-0505-s011487 | reverse | spare | 1 | pending |
| line-1 | line-1-0707-0431-s013954 | reverse | spare | 1 | pending |
| line-1 | line-1-0423-0728-s000000 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0699-0615-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0574-0595-s003007 | forward | revenue | 3 | pending |
| line-2 | line-2-0574-0595-s003007 | reverse | revenue | 3 | pending |
| line-2 | line-2-0550-0550-s004289 | forward | revenue | 3 | pending |
| line-2 | line-2-0550-0550-s004289 | reverse | revenue | 3 | pending |
| line-2 | line-2-0573-0521-s006015 | forward | revenue | 3 | pending |
| line-2 | line-2-0573-0521-s006015 | reverse | revenue | 3 | pending |
| line-2 | line-2-0476-0467-s009019 | forward | revenue | 3 | pending |
| line-2 | line-2-0476-0467-s009019 | reverse | revenue | 2 | pending |
| line-2 | line-2-0406-0262-s014286 | reverse | revenue | 2 | pending |
| line-2 | line-2-0476-0467-s009019 | reverse | spare | 1 | pending |
| line-2 | line-2-0406-0262-s014286 | reverse | spare | 1 | pending |
| line-2 | line-2-0699-0615-s000000 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0289-0190-s000000 | forward | revenue | 6 | pending |
| line-3 | line-3-0401-0444-s007018 | forward | revenue | 5 | pending |
| line-3 | line-3-0401-0444-s007018 | reverse | revenue | 5 | pending |
| line-3 | line-3-0424-0582-s010019 | forward | revenue | 5 | pending |
| line-3 | line-3-0424-0582-s010019 | reverse | revenue | 5 | pending |
| line-3 | line-3-0401-0713-s012829 | forward | revenue | 5 | pending |
| line-3 | line-3-0401-0713-s012829 | reverse | revenue | 5 | pending |
| line-3 | line-3-0486-1078-s021292 | reverse | revenue | 5 | pending |
| line-3 | line-3-0401-0444-s007018 | forward | spare | 1 | pending |
| line-3 | line-3-0401-0444-s007018 | reverse | spare | 1 | pending |
| line-3 | line-3-0424-0582-s010019 | forward | spare | 1 | pending |
| line-3 | line-3-0424-0582-s010019 | reverse | spare | 1 | pending |
| line-3 | line-3-0401-0713-s012829 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**64 trainsets exceed the reference platform envelope**, requiring **3,808.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0423-0728-s000000 | 4 | 2 | 2 | 119.0 |
| line-1-0466-0621-s003016 | 6 | 2 | 4 | 238.0 |
| line-1-0557-0586-s006029 | 6 | 4 | 2 | 119.0 |
| line-1-0601-0528-s009033 | 6 | 4 | 2 | 119.0 |
| line-1-0655-0505-s011487 | 6 | 2 | 4 | 238.0 |
| line-1-0707-0431-s013954 | 3 | 2 | 1 | 59.5 |
| line-2-0406-0262-s014286 | 3 | 2 | 1 | 59.5 |
| line-2-0476-0467-s009019 | 6 | 2 | 4 | 238.0 |
| line-2-0550-0550-s004289 | 6 | 2 | 4 | 238.0 |
| line-2-0573-0521-s006015 | 6 | 4 | 2 | 119.0 |
| line-2-0574-0595-s003007 | 6 | 4 | 2 | 119.0 |
| line-2-0699-0615-s000000 | 4 | 2 | 2 | 119.0 |
| line-3-0289-0190-s000000 | 6 | 2 | 4 | 238.0 |
| line-3-0401-0444-s007018 | 12 | 2 | 10 | 595.0 |
| line-3-0401-0713-s012829 | 11 | 4 | 7 | 416.5 |
| line-3-0424-0582-s010019 | 12 | 2 | 10 | 595.0 |
| line-3-0486-1078-s021292 | 5 | 2 | 3 | 178.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/south-asia/Afghanistan/Herat/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
