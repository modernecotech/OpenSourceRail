# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **30 trainsets at stations + 85 at depots = 115 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0400-0426-s018709 | line-1 | declared-depot | 49 | 2,915.5 | 9 |
| line-2-0398-0611-s000000 | line-2 | declared-depot | 19 | 1,130.5 | 4 |
| line-3-0543-0652-s000000 | line-3 | declared-depot | 17 | 1,011.5 | 4 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0400-0426-s018709 | station | reverse | revenue | 2 |
| line-1 | line-1-0465-0496-s016548 | station | forward | revenue | 1 |
| line-1 | line-1-0465-0496-s016548 | station | reverse | revenue | 1 |
| line-1 | line-1-0532-0568-s014366 | station | forward | revenue | 1 |
| line-1 | line-1-0532-0568-s014366 | station | reverse | revenue | 1 |
| line-1 | line-1-0586-0627-s012565 | station | forward | revenue | 1 |
| line-1 | line-1-0586-0627-s012565 | station | reverse | revenue | 1 |
| line-1 | line-1-0645-0692-s010598 | station | forward | revenue | 1 |
| line-1 | line-1-0645-0692-s010598 | station | reverse | revenue | 1 |
| line-1 | line-1-0929-1021-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0398-0611-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0532-0568-s003083 | station | forward | revenue | 1 |
| line-2 | line-2-0532-0568-s003083 | station | reverse | revenue | 1 |
| line-2 | line-2-0647-0531-s005690 | station | forward | revenue | 1 |
| line-2 | line-2-0647-0531-s005690 | station | reverse | revenue | 1 |
| line-2 | line-2-0760-0495-s008295 | station | reverse | revenue | 2 |
| line-3 | line-3-0543-0652-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0586-0627-s001108 | station | forward | revenue | 1 |
| line-3 | line-3-0586-0627-s001108 | station | reverse | revenue | 1 |
| line-3 | line-3-0658-0583-s003012 | station | forward | revenue | 1 |
| line-3 | line-3-0658-0583-s003012 | station | reverse | revenue | 1 |
| line-3 | line-3-0747-0529-s005322 | station | forward | revenue | 1 |
| line-3 | line-3-0747-0529-s005322 | station | reverse | revenue | 1 |
| line-3 | line-3-0835-0476-s007626 | station | reverse | revenue | 2 |
| line-1 | line-1-0400-0426-s018709 | depot | — | revenue | 43 |
| line-1 | line-1-0400-0426-s018709 | depot | — | spare | 5 |
| line-1 | line-1-0400-0426-s018709 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0398-0611-s000000 | depot | — | revenue | 16 |
| line-2 | line-2-0398-0611-s000000 | depot | — | spare | 2 |
| line-2 | line-2-0398-0611-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0543-0652-s000000 | depot | — | revenue | 14 |
| line-3 | line-3-0543-0652-s000000 | depot | — | spare | 2 |
| line-3 | line-3-0543-0652-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/safi-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **115 trainsets at 15 stations**; largest initial station queue **12**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **103 revenue, 9 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **30 positions**; **85 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **15 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0929-1021-s000000 | forward | revenue | 6 | pending |
| line-1 | line-1-0645-0692-s010598 | forward | revenue | 6 | pending |
| line-1 | line-1-0645-0692-s010598 | reverse | revenue | 6 | pending |
| line-1 | line-1-0586-0627-s012565 | forward | revenue | 6 | pending |
| line-1 | line-1-0586-0627-s012565 | reverse | revenue | 6 | pending |
| line-1 | line-1-0532-0568-s014366 | forward | revenue | 5 | pending |
| line-1 | line-1-0532-0568-s014366 | reverse | revenue | 5 | pending |
| line-1 | line-1-0465-0496-s016548 | forward | revenue | 5 | pending |
| line-1 | line-1-0465-0496-s016548 | reverse | revenue | 5 | pending |
| line-1 | line-1-0400-0426-s018709 | reverse | revenue | 5 | pending |
| line-1 | line-1-0532-0568-s014366 | forward | spare | 1 | pending |
| line-1 | line-1-0532-0568-s014366 | reverse | spare | 1 | pending |
| line-1 | line-1-0465-0496-s016548 | forward | spare | 1 | pending |
| line-1 | line-1-0465-0496-s016548 | reverse | spare | 1 | pending |
| line-1 | line-1-0400-0426-s018709 | reverse | spare | 1 | pending |
| line-1 | line-1-0929-1021-s000000 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0398-0611-s000000 | forward | revenue | 4 | pending |
| line-2 | line-2-0532-0568-s003083 | forward | revenue | 4 | pending |
| line-2 | line-2-0532-0568-s003083 | reverse | revenue | 4 | pending |
| line-2 | line-2-0647-0531-s005690 | forward | revenue | 4 | pending |
| line-2 | line-2-0647-0531-s005690 | reverse | revenue | 4 | pending |
| line-2 | line-2-0760-0495-s008295 | reverse | revenue | 4 | pending |
| line-2 | line-2-0398-0611-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0532-0568-s003083 | forward | spare | 1 | pending |
| line-2 | line-2-0532-0568-s003083 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0543-0652-s000000 | forward | revenue | 3 | pending |
| line-3 | line-3-0586-0627-s001108 | forward | revenue | 3 | pending |
| line-3 | line-3-0586-0627-s001108 | reverse | revenue | 3 | pending |
| line-3 | line-3-0658-0583-s003012 | forward | revenue | 3 | pending |
| line-3 | line-3-0658-0583-s003012 | reverse | revenue | 3 | pending |
| line-3 | line-3-0747-0529-s005322 | forward | revenue | 3 | pending |
| line-3 | line-3-0747-0529-s005322 | reverse | revenue | 3 | pending |
| line-3 | line-3-0835-0476-s007626 | reverse | revenue | 3 | pending |
| line-3 | line-3-0543-0652-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0586-0627-s001108 | forward | spare | 1 | pending |
| line-3 | line-3-0586-0627-s001108 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**77 trainsets exceed the reference platform envelope**, requiring **4,581.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0400-0426-s018709 | 6 | 2 | 4 | 238.0 |
| line-1-0465-0496-s016548 | 12 | 2 | 10 | 595.0 |
| line-1-0532-0568-s014366 | 12 | 4 | 8 | 476.0 |
| line-1-0586-0627-s012565 | 12 | 4 | 8 | 476.0 |
| line-1-0645-0692-s010598 | 12 | 2 | 10 | 595.0 |
| line-1-0929-1021-s000000 | 7 | 2 | 5 | 297.5 |
| line-2-0398-0611-s000000 | 5 | 2 | 3 | 178.5 |
| line-2-0532-0568-s003083 | 10 | 4 | 6 | 357.0 |
| line-2-0647-0531-s005690 | 8 | 2 | 6 | 357.0 |
| line-2-0760-0495-s008295 | 4 | 2 | 2 | 119.0 |
| line-3-0543-0652-s000000 | 4 | 2 | 2 | 119.0 |
| line-3-0586-0627-s001108 | 8 | 4 | 4 | 238.0 |
| line-3-0658-0583-s003012 | 6 | 2 | 4 | 238.0 |
| line-3-0747-0529-s005322 | 6 | 2 | 4 | 238.0 |
| line-3-0835-0476-s007626 | 3 | 2 | 1 | 59.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/north-africa/Morocco/Safi/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
