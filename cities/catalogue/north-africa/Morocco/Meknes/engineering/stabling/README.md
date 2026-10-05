# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **28 trainsets at stations + 65 at depots = 93 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0763-0392-s012652 | line-1 | declared-depot | 29 | 1,725.5 | 6 |
| line-2-0324-0563-s000000 | line-2 | declared-depot | 22 | 1,309.0 | 5 |
| line-3-0769-0485-s000000 | line-3 | declared-depot | 14 | 833.0 | 4 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0413-0831-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0518-0699-s003803 | station | forward | revenue | 1 |
| line-1 | line-1-0518-0699-s003803 | station | reverse | revenue | 1 |
| line-1 | line-1-0601-0595-s006805 | station | forward | revenue | 1 |
| line-1 | line-1-0601-0595-s006805 | station | reverse | revenue | 1 |
| line-1 | line-1-0700-0472-s010360 | station | forward | revenue | 1 |
| line-1 | line-1-0700-0472-s010360 | station | reverse | revenue | 1 |
| line-1 | line-1-0763-0392-s012652 | station | reverse | revenue | 2 |
| line-2 | line-2-0324-0563-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0467-0580-s003001 | station | forward | revenue | 1 |
| line-2 | line-2-0467-0580-s003001 | station | reverse | revenue | 1 |
| line-2 | line-2-0601-0595-s005805 | station | forward | revenue | 1 |
| line-2 | line-2-0601-0595-s005805 | station | reverse | revenue | 1 |
| line-2 | line-2-0755-0613-s009034 | station | reverse | revenue | 2 |
| line-3 | line-3-0436-0420-s007198 | station | reverse | revenue | 2 |
| line-3 | line-3-0555-0443-s004628 | station | forward | revenue | 1 |
| line-3 | line-3-0555-0443-s004628 | station | reverse | revenue | 1 |
| line-3 | line-3-0630-0458-s003004 | station | forward | revenue | 1 |
| line-3 | line-3-0630-0458-s003004 | station | reverse | revenue | 1 |
| line-3 | line-3-0700-0472-s001502 | station | forward | revenue | 1 |
| line-3 | line-3-0700-0472-s001502 | station | reverse | revenue | 1 |
| line-3 | line-3-0769-0485-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0763-0392-s012652 | depot | — | revenue | 25 |
| line-1 | line-1-0763-0392-s012652 | depot | — | spare | 3 |
| line-1 | line-1-0763-0392-s012652 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0324-0563-s000000 | depot | — | revenue | 19 |
| line-2 | line-2-0324-0563-s000000 | depot | — | spare | 2 |
| line-2 | line-2-0324-0563-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0769-0485-s000000 | depot | — | revenue | 11 |
| line-3 | line-3-0769-0485-s000000 | depot | — | spare | 2 |
| line-3 | line-3-0769-0485-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/meknes-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **93 trainsets at 14 stations**; largest initial station queue **10**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **83 revenue, 7 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **28 positions**; **65 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **14 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0413-0831-s000000 | forward | revenue | 5 | pending |
| line-1 | line-1-0518-0699-s003803 | forward | revenue | 5 | pending |
| line-1 | line-1-0518-0699-s003803 | reverse | revenue | 5 | pending |
| line-1 | line-1-0601-0595-s006805 | forward | revenue | 4 | pending |
| line-1 | line-1-0601-0595-s006805 | reverse | revenue | 4 | pending |
| line-1 | line-1-0700-0472-s010360 | forward | revenue | 4 | pending |
| line-1 | line-1-0700-0472-s010360 | reverse | revenue | 4 | pending |
| line-1 | line-1-0763-0392-s012652 | reverse | revenue | 4 | pending |
| line-1 | line-1-0601-0595-s006805 | forward | spare | 1 | pending |
| line-1 | line-1-0601-0595-s006805 | reverse | spare | 1 | pending |
| line-1 | line-1-0700-0472-s010360 | forward | spare | 1 | pending |
| line-1 | line-1-0700-0472-s010360 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0324-0563-s000000 | forward | revenue | 5 | pending |
| line-2 | line-2-0467-0580-s003001 | forward | revenue | 5 | pending |
| line-2 | line-2-0467-0580-s003001 | reverse | revenue | 5 | pending |
| line-2 | line-2-0601-0595-s005805 | forward | revenue | 4 | pending |
| line-2 | line-2-0601-0595-s005805 | reverse | revenue | 4 | pending |
| line-2 | line-2-0755-0613-s009034 | reverse | revenue | 4 | pending |
| line-2 | line-2-0601-0595-s005805 | forward | spare | 1 | pending |
| line-2 | line-2-0601-0595-s005805 | reverse | spare | 1 | pending |
| line-2 | line-2-0755-0613-s009034 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0769-0485-s000000 | forward | revenue | 3 | pending |
| line-3 | line-3-0700-0472-s001502 | forward | revenue | 3 | pending |
| line-3 | line-3-0700-0472-s001502 | reverse | revenue | 3 | pending |
| line-3 | line-3-0630-0458-s003004 | forward | revenue | 3 | pending |
| line-3 | line-3-0630-0458-s003004 | reverse | revenue | 3 | pending |
| line-3 | line-3-0555-0443-s004628 | forward | revenue | 2 | pending |
| line-3 | line-3-0555-0443-s004628 | reverse | revenue | 2 | pending |
| line-3 | line-3-0436-0420-s007198 | reverse | revenue | 2 | pending |
| line-3 | line-3-0555-0443-s004628 | forward | spare | 1 | pending |
| line-3 | line-3-0555-0443-s004628 | reverse | spare | 1 | pending |
| line-3 | line-3-0436-0420-s007198 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**57 trainsets exceed the reference platform envelope**, requiring **3,391.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0413-0831-s000000 | 5 | 2 | 3 | 178.5 |
| line-1-0518-0699-s003803 | 10 | 2 | 8 | 476.0 |
| line-1-0601-0595-s006805 | 10 | 4 | 6 | 357.0 |
| line-1-0700-0472-s010360 | 10 | 4 | 6 | 357.0 |
| line-1-0763-0392-s012652 | 4 | 2 | 2 | 119.0 |
| line-2-0324-0563-s000000 | 5 | 2 | 3 | 178.5 |
| line-2-0467-0580-s003001 | 10 | 2 | 8 | 476.0 |
| line-2-0601-0595-s005805 | 10 | 4 | 6 | 357.0 |
| line-2-0755-0613-s009034 | 5 | 2 | 3 | 178.5 |
| line-3-0436-0420-s007198 | 3 | 2 | 1 | 59.5 |
| line-3-0555-0443-s004628 | 6 | 2 | 4 | 238.0 |
| line-3-0630-0458-s003004 | 6 | 2 | 4 | 238.0 |
| line-3-0700-0472-s001502 | 6 | 4 | 2 | 119.0 |
| line-3-0769-0485-s000000 | 3 | 2 | 1 | 59.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/north-africa/Morocco/Meknes/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
