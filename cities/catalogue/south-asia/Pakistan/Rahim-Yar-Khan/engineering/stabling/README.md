# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **24 trainsets at stations + 133 at depots = 157 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0457-0559-s000000 | line-1 | declared-depot | 18 | 1,071.0 | 4 |
| line-2-0742-0447-s000000 | line-2 | declared-depot | 49 | 2,915.5 | 8 |
| line-3-0885-0164-s024392 | line-3 | declared-depot | 66 | 3,927.0 | 11 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0457-0559-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0558-0648-s003015 | station | forward | revenue | 1 |
| line-1 | line-1-0558-0648-s003015 | station | reverse | revenue | 1 |
| line-1 | line-1-0717-0786-s007713 | station | reverse | revenue | 2 |
| line-2 | line-2-0181-1033-s017996 | station | reverse | revenue | 2 |
| line-2 | line-2-0539-0644-s006360 | station | forward | revenue | 1 |
| line-2 | line-2-0539-0644-s006360 | station | reverse | revenue | 1 |
| line-2 | line-2-0635-0551-s003341 | station | forward | revenue | 1 |
| line-2 | line-2-0635-0551-s003341 | station | reverse | revenue | 1 |
| line-2 | line-2-0742-0447-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0212-1034-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0526-0672-s010497 | station | forward | revenue | 1 |
| line-3 | line-3-0526-0672-s010497 | station | reverse | revenue | 1 |
| line-3 | line-3-0607-0564-s013516 | station | forward | revenue | 1 |
| line-3 | line-3-0607-0564-s013516 | station | reverse | revenue | 1 |
| line-3 | line-3-0755-0370-s018950 | station | forward | revenue | 1 |
| line-3 | line-3-0755-0370-s018950 | station | reverse | revenue | 1 |
| line-3 | line-3-0885-0164-s024392 | station | reverse | revenue | 2 |
| line-1 | line-1-0457-0559-s000000 | depot | — | revenue | 15 |
| line-1 | line-1-0457-0559-s000000 | depot | — | spare | 2 |
| line-1 | line-1-0457-0559-s000000 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0742-0447-s000000 | depot | — | revenue | 43 |
| line-2 | line-2-0742-0447-s000000 | depot | — | spare | 5 |
| line-2 | line-2-0742-0447-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0885-0164-s024392 | depot | — | revenue | 59 |
| line-3 | line-3-0885-0164-s024392 | depot | — | spare | 6 |
| line-3 | line-3-0885-0164-s024392 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/rahim-yar-khan-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **157 trainsets at 12 stations**; largest initial station queue **20**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **141 revenue, 13 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **24 positions**; **133 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **12 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0457-0559-s000000 | forward | revenue | 6 | pending |
| line-1 | line-1-0558-0648-s003015 | forward | revenue | 5 | pending |
| line-1 | line-1-0558-0648-s003015 | reverse | revenue | 5 | pending |
| line-1 | line-1-0717-0786-s007713 | reverse | revenue | 5 | pending |
| line-1 | line-1-0558-0648-s003015 | forward | spare | 1 | pending |
| line-1 | line-1-0558-0648-s003015 | reverse | spare | 1 | pending |
| line-1 | line-1-0717-0786-s007713 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0742-0447-s000000 | forward | revenue | 9 | pending |
| line-2 | line-2-0635-0551-s003341 | forward | revenue | 9 | pending |
| line-2 | line-2-0635-0551-s003341 | reverse | revenue | 9 | pending |
| line-2 | line-2-0539-0644-s006360 | forward | revenue | 8 | pending |
| line-2 | line-2-0539-0644-s006360 | reverse | revenue | 8 | pending |
| line-2 | line-2-0181-1033-s017996 | reverse | revenue | 8 | pending |
| line-2 | line-2-0539-0644-s006360 | forward | spare | 1 | pending |
| line-2 | line-2-0539-0644-s006360 | reverse | spare | 1 | pending |
| line-2 | line-2-0181-1033-s017996 | reverse | spare | 1 | pending |
| line-2 | line-2-0742-0447-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0635-0551-s003341 | forward | spare | 1 | pending |
| line-2 | line-2-0635-0551-s003341 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0212-1034-s000000 | forward | revenue | 9 | pending |
| line-3 | line-3-0526-0672-s010497 | forward | revenue | 9 | pending |
| line-3 | line-3-0526-0672-s010497 | reverse | revenue | 9 | pending |
| line-3 | line-3-0607-0564-s013516 | forward | revenue | 9 | pending |
| line-3 | line-3-0607-0564-s013516 | reverse | revenue | 9 | pending |
| line-3 | line-3-0755-0370-s018950 | forward | revenue | 8 | pending |
| line-3 | line-3-0755-0370-s018950 | reverse | revenue | 8 | pending |
| line-3 | line-3-0885-0164-s024392 | reverse | revenue | 8 | pending |
| line-3 | line-3-0755-0370-s018950 | forward | spare | 1 | pending |
| line-3 | line-3-0755-0370-s018950 | reverse | spare | 1 | pending |
| line-3 | line-3-0885-0164-s024392 | reverse | spare | 1 | pending |
| line-3 | line-3-0212-1034-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0526-0672-s010497 | forward | spare | 1 | pending |
| line-3 | line-3-0526-0672-s010497 | reverse | spare | 1 | pending |
| line-3 | line-3-0607-0564-s013516 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**123 trainsets exceed the reference platform envelope**, requiring **7,318.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0457-0559-s000000 | 6 | 2 | 4 | 238.0 |
| line-1-0558-0648-s003015 | 12 | 4 | 8 | 476.0 |
| line-1-0717-0786-s007713 | 6 | 2 | 4 | 238.0 |
| line-2-0181-1033-s017996 | 9 | 2 | 7 | 416.5 |
| line-2-0539-0644-s006360 | 18 | 4 | 14 | 833.0 |
| line-2-0635-0551-s003341 | 20 | 4 | 16 | 952.0 |
| line-2-0742-0447-s000000 | 10 | 2 | 8 | 476.0 |
| line-3-0212-1034-s000000 | 10 | 2 | 8 | 476.0 |
| line-3-0526-0672-s010497 | 20 | 4 | 16 | 952.0 |
| line-3-0607-0564-s013516 | 19 | 4 | 15 | 892.5 |
| line-3-0755-0370-s018950 | 18 | 2 | 16 | 952.0 |
| line-3-0885-0164-s024392 | 9 | 2 | 7 | 416.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/south-asia/Pakistan/Rahim-Yar-Khan/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
