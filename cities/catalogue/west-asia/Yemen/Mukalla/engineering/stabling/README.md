# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **30 trainsets at stations + 148 at depots = 178 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0857-0110-s000000 | line-1 | declared-depot | 40 | 2,380.0 | 7 |
| line-2-0668-0713-s000000 | line-2 | declared-depot | 41 | 2,439.5 | 7 |
| line-3-0888-0083-s024546 | line-3 | declared-depot | 67 | 3,986.5 | 11 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0462-0618-s016053 | station | reverse | revenue | 2 |
| line-1 | line-1-0530-0541-s013739 | station | forward | revenue | 1 |
| line-1 | line-1-0530-0541-s013739 | station | reverse | revenue | 1 |
| line-1 | line-1-0620-0440-s010715 | station | forward | revenue | 1 |
| line-1 | line-1-0620-0440-s010715 | station | reverse | revenue | 1 |
| line-1 | line-1-0834-0200-s003510 | station | forward | revenue | 1 |
| line-1 | line-1-0834-0200-s003510 | station | reverse | revenue | 1 |
| line-1 | line-1-0857-0110-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0668-0713-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0727-0565-s003507 | station | forward | revenue | 1 |
| line-2 | line-2-0727-0565-s003507 | station | reverse | revenue | 1 |
| line-2 | line-2-0786-0418-s007006 | station | forward | revenue | 1 |
| line-2 | line-2-0786-0418-s007006 | station | reverse | revenue | 1 |
| line-2 | line-2-0946-0071-s015983 | station | reverse | revenue | 2 |
| line-3 | line-3-0414-1035-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0529-0754-s007009 | station | forward | revenue | 1 |
| line-3 | line-3-0529-0754-s007009 | station | reverse | revenue | 1 |
| line-3 | line-3-0580-0630-s010029 | station | forward | revenue | 1 |
| line-3 | line-3-0580-0630-s010029 | station | reverse | revenue | 1 |
| line-3 | line-3-0607-0564-s011631 | station | forward | revenue | 1 |
| line-3 | line-3-0607-0564-s011631 | station | reverse | revenue | 1 |
| line-3 | line-3-0667-0420-s015137 | station | forward | revenue | 1 |
| line-3 | line-3-0667-0420-s015137 | station | reverse | revenue | 1 |
| line-3 | line-3-0888-0083-s024546 | station | reverse | revenue | 2 |
| line-1 | line-1-0857-0110-s000000 | depot | — | revenue | 35 |
| line-1 | line-1-0857-0110-s000000 | depot | — | spare | 4 |
| line-1 | line-1-0857-0110-s000000 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0668-0713-s000000 | depot | — | revenue | 36 |
| line-2 | line-2-0668-0713-s000000 | depot | — | spare | 4 |
| line-2 | line-2-0668-0713-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0888-0083-s024546 | depot | — | revenue | 59 |
| line-3 | line-3-0888-0083-s024546 | depot | — | spare | 7 |
| line-3 | line-3-0888-0083-s024546 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/mukalla-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **178 trainsets at 15 stations**; largest initial station queue **16**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **160 revenue, 15 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **30 positions**; **148 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **15 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0857-0110-s000000 | forward | revenue | 6 | pending |
| line-1 | line-1-0834-0200-s003510 | forward | revenue | 6 | pending |
| line-1 | line-1-0834-0200-s003510 | reverse | revenue | 6 | pending |
| line-1 | line-1-0620-0440-s010715 | forward | revenue | 6 | pending |
| line-1 | line-1-0620-0440-s010715 | reverse | revenue | 6 | pending |
| line-1 | line-1-0530-0541-s013739 | forward | revenue | 5 | pending |
| line-1 | line-1-0530-0541-s013739 | reverse | revenue | 5 | pending |
| line-1 | line-1-0462-0618-s016053 | reverse | revenue | 5 | pending |
| line-1 | line-1-0530-0541-s013739 | forward | spare | 1 | pending |
| line-1 | line-1-0530-0541-s013739 | reverse | spare | 1 | pending |
| line-1 | line-1-0462-0618-s016053 | reverse | spare | 1 | pending |
| line-1 | line-1-0857-0110-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0834-0200-s003510 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0668-0713-s000000 | forward | revenue | 8 | pending |
| line-2 | line-2-0727-0565-s003507 | forward | revenue | 8 | pending |
| line-2 | line-2-0727-0565-s003507 | reverse | revenue | 7 | pending |
| line-2 | line-2-0786-0418-s007006 | forward | revenue | 7 | pending |
| line-2 | line-2-0786-0418-s007006 | reverse | revenue | 7 | pending |
| line-2 | line-2-0946-0071-s015983 | reverse | revenue | 7 | pending |
| line-2 | line-2-0727-0565-s003507 | reverse | spare | 1 | pending |
| line-2 | line-2-0786-0418-s007006 | forward | spare | 1 | pending |
| line-2 | line-2-0786-0418-s007006 | reverse | spare | 1 | pending |
| line-2 | line-2-0946-0071-s015983 | reverse | spare | 1 | pending |
| line-2 | line-2-0668-0713-s000000 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0414-1035-s000000 | forward | revenue | 8 | pending |
| line-3 | line-3-0529-0754-s007009 | forward | revenue | 7 | pending |
| line-3 | line-3-0529-0754-s007009 | reverse | revenue | 7 | pending |
| line-3 | line-3-0580-0630-s010029 | forward | revenue | 7 | pending |
| line-3 | line-3-0580-0630-s010029 | reverse | revenue | 7 | pending |
| line-3 | line-3-0607-0564-s011631 | forward | revenue | 7 | pending |
| line-3 | line-3-0607-0564-s011631 | reverse | revenue | 7 | pending |
| line-3 | line-3-0667-0420-s015137 | forward | revenue | 7 | pending |
| line-3 | line-3-0667-0420-s015137 | reverse | revenue | 7 | pending |
| line-3 | line-3-0888-0083-s024546 | reverse | revenue | 7 | pending |
| line-3 | line-3-0529-0754-s007009 | forward | spare | 1 | pending |
| line-3 | line-3-0529-0754-s007009 | reverse | spare | 1 | pending |
| line-3 | line-3-0580-0630-s010029 | forward | spare | 1 | pending |
| line-3 | line-3-0580-0630-s010029 | reverse | spare | 1 | pending |
| line-3 | line-3-0607-0564-s011631 | forward | spare | 1 | pending |
| line-3 | line-3-0607-0564-s011631 | reverse | spare | 1 | pending |
| line-3 | line-3-0667-0420-s015137 | forward | spare | 1 | pending |
| line-3 | line-3-0667-0420-s015137 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**148 trainsets exceed the reference platform envelope**, requiring **8,806.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0462-0618-s016053 | 6 | 2 | 4 | 238.0 |
| line-1-0530-0541-s013739 | 12 | 2 | 10 | 595.0 |
| line-1-0620-0440-s010715 | 12 | 2 | 10 | 595.0 |
| line-1-0834-0200-s003510 | 13 | 2 | 11 | 654.5 |
| line-1-0857-0110-s000000 | 7 | 2 | 5 | 297.5 |
| line-2-0668-0713-s000000 | 9 | 2 | 7 | 416.5 |
| line-2-0727-0565-s003507 | 16 | 2 | 14 | 833.0 |
| line-2-0786-0418-s007006 | 16 | 2 | 14 | 833.0 |
| line-2-0946-0071-s015983 | 8 | 2 | 6 | 357.0 |
| line-3-0414-1035-s000000 | 8 | 2 | 6 | 357.0 |
| line-3-0529-0754-s007009 | 16 | 2 | 14 | 833.0 |
| line-3-0580-0630-s010029 | 16 | 2 | 14 | 833.0 |
| line-3-0607-0564-s011631 | 16 | 2 | 14 | 833.0 |
| line-3-0667-0420-s015137 | 16 | 2 | 14 | 833.0 |
| line-3-0888-0083-s024546 | 7 | 2 | 5 | 297.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Yemen/Mukalla/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
