# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **34 trainsets at stations + 131 at depots = 165 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0457-0559-s000000 | line-1 | declared-depot | 18 | 1,071.0 | 4 |
| line-2-0742-0447-s000000 | line-2 | declared-depot | 47 | 2,796.5 | 9 |
| line-3-0885-0164-s025263 | line-3 | declared-depot | 66 | 3,927.0 | 11 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0457-0559-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0546-0637-s002649 | station | forward | revenue | 1 |
| line-1 | line-1-0546-0637-s002649 | station | reverse | revenue | 1 |
| line-1 | line-1-0550-0640-s002765 | station | forward | revenue | 1 |
| line-1 | line-1-0550-0640-s002765 | station | reverse | revenue | 1 |
| line-1 | line-1-0717-0786-s007713 | station | reverse | revenue | 2 |
| line-2 | line-2-0181-1033-s017996 | station | reverse | revenue | 2 |
| line-2 | line-2-0546-0637-s006127 | station | forward | revenue | 1 |
| line-2 | line-2-0546-0637-s006127 | station | reverse | revenue | 1 |
| line-2 | line-2-0567-0617-s005482 | station | forward | revenue | 1 |
| line-2 | line-2-0567-0617-s005482 | station | reverse | revenue | 1 |
| line-2 | line-2-0570-0614-s005398 | station | forward | revenue | 1 |
| line-2 | line-2-0570-0614-s005398 | station | reverse | revenue | 1 |
| line-2 | line-2-0635-0551-s003341 | station | forward | revenue | 1 |
| line-2 | line-2-0635-0551-s003341 | station | reverse | revenue | 1 |
| line-2 | line-2-0742-0447-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0212-1034-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0550-0640-s011960 | station | forward | revenue | 1 |
| line-3 | line-3-0550-0640-s011960 | station | reverse | revenue | 1 |
| line-3 | line-3-0566-0618-s012591 | station | forward | revenue | 1 |
| line-3 | line-3-0566-0618-s012591 | station | reverse | revenue | 1 |
| line-3 | line-3-0568-0616-s012659 | station | forward | revenue | 1 |
| line-3 | line-3-0568-0616-s012659 | station | reverse | revenue | 1 |
| line-3 | line-3-0570-0614-s012728 | station | forward | revenue | 1 |
| line-3 | line-3-0570-0614-s012728 | station | reverse | revenue | 1 |
| line-3 | line-3-0607-0564-s014081 | station | forward | revenue | 1 |
| line-3 | line-3-0607-0564-s014081 | station | reverse | revenue | 1 |
| line-3 | line-3-0885-0164-s025263 | station | reverse | revenue | 2 |
| line-1 | line-1-0457-0559-s000000 | depot | — | revenue | 15 |
| line-1 | line-1-0457-0559-s000000 | depot | — | spare | 2 |
| line-1 | line-1-0457-0559-s000000 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0742-0447-s000000 | depot | — | revenue | 41 |
| line-2 | line-2-0742-0447-s000000 | depot | — | spare | 5 |
| line-2 | line-2-0742-0447-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0885-0164-s025263 | depot | — | revenue | 58 |
| line-3 | line-3-0885-0164-s025263 | depot | — | spare | 7 |
| line-3 | line-3-0885-0164-s025263 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/rahim-yar-khan-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **165 trainsets at 17 stations**; largest initial station queue **14**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **148 revenue, 14 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **34 positions**; **131 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **17 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0457-0559-s000000 | forward | revenue | 4 | pending |
| line-1 | line-1-0546-0637-s002649 | forward | revenue | 4 | pending |
| line-1 | line-1-0546-0637-s002649 | reverse | revenue | 4 | pending |
| line-1 | line-1-0550-0640-s002765 | forward | revenue | 4 | pending |
| line-1 | line-1-0550-0640-s002765 | reverse | revenue | 4 | pending |
| line-1 | line-1-0717-0786-s007713 | reverse | revenue | 3 | pending |
| line-1 | line-1-0717-0786-s007713 | reverse | spare | 1 | pending |
| line-1 | line-1-0457-0559-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0546-0637-s002649 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0742-0447-s000000 | forward | revenue | 6 | pending |
| line-2 | line-2-0635-0551-s003341 | forward | revenue | 6 | pending |
| line-2 | line-2-0635-0551-s003341 | reverse | revenue | 6 | pending |
| line-2 | line-2-0570-0614-s005398 | forward | revenue | 5 | pending |
| line-2 | line-2-0570-0614-s005398 | reverse | revenue | 5 | pending |
| line-2 | line-2-0567-0617-s005482 | forward | revenue | 5 | pending |
| line-2 | line-2-0567-0617-s005482 | reverse | revenue | 5 | pending |
| line-2 | line-2-0546-0637-s006127 | forward | revenue | 5 | pending |
| line-2 | line-2-0546-0637-s006127 | reverse | revenue | 5 | pending |
| line-2 | line-2-0181-1033-s017996 | reverse | revenue | 5 | pending |
| line-2 | line-2-0570-0614-s005398 | forward | spare | 1 | pending |
| line-2 | line-2-0570-0614-s005398 | reverse | spare | 1 | pending |
| line-2 | line-2-0567-0617-s005482 | forward | spare | 1 | pending |
| line-2 | line-2-0567-0617-s005482 | reverse | spare | 1 | pending |
| line-2 | line-2-0546-0637-s006127 | forward | spare | 1 | pending |
| line-2 | line-2-0546-0637-s006127 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0212-1034-s000000 | forward | revenue | 6 | pending |
| line-3 | line-3-0550-0640-s011960 | forward | revenue | 6 | pending |
| line-3 | line-3-0550-0640-s011960 | reverse | revenue | 6 | pending |
| line-3 | line-3-0566-0618-s012591 | forward | revenue | 6 | pending |
| line-3 | line-3-0566-0618-s012591 | reverse | revenue | 6 | pending |
| line-3 | line-3-0568-0616-s012659 | forward | revenue | 6 | pending |
| line-3 | line-3-0568-0616-s012659 | reverse | revenue | 6 | pending |
| line-3 | line-3-0570-0614-s012728 | forward | revenue | 6 | pending |
| line-3 | line-3-0570-0614-s012728 | reverse | revenue | 6 | pending |
| line-3 | line-3-0607-0564-s014081 | forward | revenue | 6 | pending |
| line-3 | line-3-0607-0564-s014081 | reverse | revenue | 6 | pending |
| line-3 | line-3-0885-0164-s025263 | reverse | revenue | 6 | pending |
| line-3 | line-3-0212-1034-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0550-0640-s011960 | forward | spare | 1 | pending |
| line-3 | line-3-0550-0640-s011960 | reverse | spare | 1 | pending |
| line-3 | line-3-0566-0618-s012591 | forward | spare | 1 | pending |
| line-3 | line-3-0566-0618-s012591 | reverse | spare | 1 | pending |
| line-3 | line-3-0568-0616-s012659 | forward | spare | 1 | pending |
| line-3 | line-3-0568-0616-s012659 | reverse | spare | 1 | pending |
| line-3 | line-3-0570-0614-s012728 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**109 trainsets exceed the reference platform envelope**, requiring **6,485.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0457-0559-s000000 | 5 | 2 | 3 | 178.5 |
| line-1-0546-0637-s002649 | 9 | 4 | 5 | 297.5 |
| line-1-0550-0640-s002765 | 8 | 4 | 4 | 238.0 |
| line-1-0717-0786-s007713 | 4 | 2 | 2 | 119.0 |
| line-2-0181-1033-s017996 | 5 | 2 | 3 | 178.5 |
| line-2-0546-0637-s006127 | 12 | 4 | 8 | 476.0 |
| line-2-0567-0617-s005482 | 12 | 4 | 8 | 476.0 |
| line-2-0570-0614-s005398 | 12 | 4 | 8 | 476.0 |
| line-2-0635-0551-s003341 | 12 | 4 | 8 | 476.0 |
| line-2-0742-0447-s000000 | 6 | 2 | 4 | 238.0 |
| line-3-0212-1034-s000000 | 7 | 2 | 5 | 297.5 |
| line-3-0550-0640-s011960 | 14 | 4 | 10 | 595.0 |
| line-3-0566-0618-s012591 | 14 | 4 | 10 | 595.0 |
| line-3-0568-0616-s012659 | 14 | 4 | 10 | 595.0 |
| line-3-0570-0614-s012728 | 13 | 4 | 9 | 535.5 |
| line-3-0607-0564-s014081 | 12 | 4 | 8 | 476.0 |
| line-3-0885-0164-s025263 | 6 | 2 | 4 | 238.0 |

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
