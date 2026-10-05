# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **26 trainsets at stations + 103 at depots = 129 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0244-0147-s016055 | line-1 | declared-depot | 40 | 2,380.0 | 7 |
| line-2-0250-0492-s000000 | line-2 | declared-depot | 22 | 1,309.0 | 5 |
| line-3-0554-0343-s000000 | line-3 | declared-depot | 41 | 2,439.5 | 7 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0244-0147-s016055 | station | reverse | revenue | 2 |
| line-1 | line-1-0373-0435-s009034 | station | forward | revenue | 1 |
| line-1 | line-1-0373-0435-s009034 | station | reverse | revenue | 1 |
| line-1 | line-1-0420-0565-s006021 | station | forward | revenue | 1 |
| line-1 | line-1-0420-0565-s006021 | station | reverse | revenue | 1 |
| line-1 | line-1-0467-0694-s003005 | station | forward | revenue | 1 |
| line-1 | line-1-0467-0694-s003005 | station | reverse | revenue | 1 |
| line-1 | line-1-0514-0823-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0250-0492-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0398-0485-s003018 | station | forward | revenue | 1 |
| line-2 | line-2-0398-0485-s003018 | station | reverse | revenue | 1 |
| line-2 | line-2-0546-0479-s006028 | station | forward | revenue | 1 |
| line-2 | line-2-0546-0479-s006028 | station | reverse | revenue | 1 |
| line-2 | line-2-0702-0472-s009206 | station | reverse | revenue | 2 |
| line-3 | line-3-0223-0982-s015850 | station | reverse | revenue | 2 |
| line-3 | line-3-0435-0587-s006030 | station | forward | revenue | 1 |
| line-3 | line-3-0435-0587-s006030 | station | reverse | revenue | 1 |
| line-3 | line-3-0495-0464-s003002 | station | forward | revenue | 1 |
| line-3 | line-3-0495-0464-s003002 | station | reverse | revenue | 1 |
| line-3 | line-3-0554-0343-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0244-0147-s016055 | depot | — | revenue | 35 |
| line-1 | line-1-0244-0147-s016055 | depot | — | spare | 4 |
| line-1 | line-1-0244-0147-s016055 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0250-0492-s000000 | depot | — | revenue | 19 |
| line-2 | line-2-0250-0492-s000000 | depot | — | spare | 2 |
| line-2 | line-2-0250-0492-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0554-0343-s000000 | depot | — | revenue | 36 |
| line-3 | line-3-0554-0343-s000000 | depot | — | spare | 4 |
| line-3 | line-3-0554-0343-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/polokwane-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **129 trainsets at 13 stations**; largest initial station queue **16**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **116 revenue, 10 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **26 positions**; **103 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **13 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0514-0823-s000000 | forward | revenue | 6 | pending |
| line-1 | line-1-0467-0694-s003005 | forward | revenue | 6 | pending |
| line-1 | line-1-0467-0694-s003005 | reverse | revenue | 6 | pending |
| line-1 | line-1-0420-0565-s006021 | forward | revenue | 6 | pending |
| line-1 | line-1-0420-0565-s006021 | reverse | revenue | 6 | pending |
| line-1 | line-1-0373-0435-s009034 | forward | revenue | 5 | pending |
| line-1 | line-1-0373-0435-s009034 | reverse | revenue | 5 | pending |
| line-1 | line-1-0244-0147-s016055 | reverse | revenue | 5 | pending |
| line-1 | line-1-0373-0435-s009034 | forward | spare | 1 | pending |
| line-1 | line-1-0373-0435-s009034 | reverse | spare | 1 | pending |
| line-1 | line-1-0244-0147-s016055 | reverse | spare | 1 | pending |
| line-1 | line-1-0514-0823-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0467-0694-s003005 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0250-0492-s000000 | forward | revenue | 5 | pending |
| line-2 | line-2-0398-0485-s003018 | forward | revenue | 5 | pending |
| line-2 | line-2-0398-0485-s003018 | reverse | revenue | 5 | pending |
| line-2 | line-2-0546-0479-s006028 | forward | revenue | 4 | pending |
| line-2 | line-2-0546-0479-s006028 | reverse | revenue | 4 | pending |
| line-2 | line-2-0702-0472-s009206 | reverse | revenue | 4 | pending |
| line-2 | line-2-0546-0479-s006028 | forward | spare | 1 | pending |
| line-2 | line-2-0546-0479-s006028 | reverse | spare | 1 | pending |
| line-2 | line-2-0702-0472-s009206 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0554-0343-s000000 | forward | revenue | 8 | pending |
| line-3 | line-3-0495-0464-s003002 | forward | revenue | 8 | pending |
| line-3 | line-3-0495-0464-s003002 | reverse | revenue | 7 | pending |
| line-3 | line-3-0435-0587-s006030 | forward | revenue | 7 | pending |
| line-3 | line-3-0435-0587-s006030 | reverse | revenue | 7 | pending |
| line-3 | line-3-0223-0982-s015850 | reverse | revenue | 7 | pending |
| line-3 | line-3-0495-0464-s003002 | reverse | spare | 1 | pending |
| line-3 | line-3-0435-0587-s006030 | forward | spare | 1 | pending |
| line-3 | line-3-0435-0587-s006030 | reverse | spare | 1 | pending |
| line-3 | line-3-0223-0982-s015850 | reverse | spare | 1 | pending |
| line-3 | line-3-0554-0343-s000000 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**99 trainsets exceed the reference platform envelope**, requiring **5,890.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0244-0147-s016055 | 6 | 2 | 4 | 238.0 |
| line-1-0373-0435-s009034 | 12 | 2 | 10 | 595.0 |
| line-1-0420-0565-s006021 | 12 | 4 | 8 | 476.0 |
| line-1-0467-0694-s003005 | 13 | 2 | 11 | 654.5 |
| line-1-0514-0823-s000000 | 7 | 2 | 5 | 297.5 |
| line-2-0250-0492-s000000 | 5 | 2 | 3 | 178.5 |
| line-2-0398-0485-s003018 | 10 | 2 | 8 | 476.0 |
| line-2-0546-0479-s006028 | 10 | 2 | 8 | 476.0 |
| line-2-0702-0472-s009206 | 5 | 2 | 3 | 178.5 |
| line-3-0223-0982-s015850 | 8 | 2 | 6 | 357.0 |
| line-3-0435-0587-s006030 | 16 | 4 | 12 | 714.0 |
| line-3-0495-0464-s003002 | 16 | 2 | 14 | 833.0 |
| line-3-0554-0343-s000000 | 9 | 2 | 7 | 416.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/south-africa/South Africa/Polokwane/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
