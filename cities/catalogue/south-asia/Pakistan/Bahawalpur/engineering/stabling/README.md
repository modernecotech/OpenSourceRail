# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **34 trainsets at stations + 86 at depots = 120 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0461-0724-s014492 | line-1 | declared-depot | 34 | 2,023.0 | 7 |
| line-2-0153-0365-s000000 | line-2 | declared-depot | 30 | 1,785.0 | 6 |
| line-3-0662-0893-s000000 | line-3 | declared-depot | 22 | 1,309.0 | 5 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0461-0724-s014492 | station | reverse | revenue | 2 |
| line-1 | line-1-0550-0650-s011912 | station | forward | revenue | 1 |
| line-1 | line-1-0550-0650-s011912 | station | reverse | revenue | 1 |
| line-1 | line-1-0587-0619-s010821 | station | forward | revenue | 1 |
| line-1 | line-1-0587-0619-s010821 | station | reverse | revenue | 1 |
| line-1 | line-1-0657-0561-s008788 | station | forward | revenue | 1 |
| line-1 | line-1-0657-0561-s008788 | station | reverse | revenue | 1 |
| line-1 | line-1-0726-0503-s006764 | station | forward | revenue | 1 |
| line-1 | line-1-0726-0503-s006764 | station | reverse | revenue | 1 |
| line-1 | line-1-0962-0331-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0153-0365-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0392-0541-s007002 | station | forward | revenue | 1 |
| line-2 | line-2-0392-0541-s007002 | station | reverse | revenue | 1 |
| line-2 | line-2-0503-0618-s010013 | station | forward | revenue | 1 |
| line-2 | line-2-0503-0618-s010013 | station | reverse | revenue | 1 |
| line-2 | line-2-0550-0650-s011276 | station | forward | revenue | 1 |
| line-2 | line-2-0550-0650-s011276 | station | reverse | revenue | 1 |
| line-2 | line-2-0602-0687-s012717 | station | forward | revenue | 1 |
| line-2 | line-2-0602-0687-s012717 | station | reverse | revenue | 1 |
| line-2 | line-2-0611-0693-s012958 | station | reverse | revenue | 2 |
| line-3 | line-3-0547-0439-s010091 | station | reverse | revenue | 2 |
| line-3 | line-3-0570-0544-s007789 | station | forward | revenue | 1 |
| line-3 | line-3-0570-0544-s007789 | station | reverse | revenue | 1 |
| line-3 | line-3-0587-0619-s006148 | station | forward | revenue | 1 |
| line-3 | line-3-0587-0619-s006148 | station | reverse | revenue | 1 |
| line-3 | line-3-0602-0687-s004664 | station | forward | revenue | 1 |
| line-3 | line-3-0602-0687-s004664 | station | reverse | revenue | 1 |
| line-3 | line-3-0662-0893-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0461-0724-s014492 | depot | — | revenue | 29 |
| line-1 | line-1-0461-0724-s014492 | depot | — | spare | 4 |
| line-1 | line-1-0461-0724-s014492 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0153-0365-s000000 | depot | — | revenue | 26 |
| line-2 | line-2-0153-0365-s000000 | depot | — | spare | 3 |
| line-2 | line-2-0153-0365-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0662-0893-s000000 | depot | — | revenue | 19 |
| line-3 | line-3-0662-0893-s000000 | depot | — | spare | 2 |
| line-3 | line-3-0662-0893-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/bahawalpur-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **120 trainsets at 17 stations**; largest initial station queue **10**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **108 revenue, 9 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **34 positions**; **86 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **17 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0962-0331-s000000 | forward | revenue | 5 | pending |
| line-1 | line-1-0726-0503-s006764 | forward | revenue | 4 | pending |
| line-1 | line-1-0726-0503-s006764 | reverse | revenue | 4 | pending |
| line-1 | line-1-0657-0561-s008788 | forward | revenue | 4 | pending |
| line-1 | line-1-0657-0561-s008788 | reverse | revenue | 4 | pending |
| line-1 | line-1-0587-0619-s010821 | forward | revenue | 4 | pending |
| line-1 | line-1-0587-0619-s010821 | reverse | revenue | 4 | pending |
| line-1 | line-1-0550-0650-s011912 | forward | revenue | 4 | pending |
| line-1 | line-1-0550-0650-s011912 | reverse | revenue | 4 | pending |
| line-1 | line-1-0461-0724-s014492 | reverse | revenue | 4 | pending |
| line-1 | line-1-0726-0503-s006764 | forward | spare | 1 | pending |
| line-1 | line-1-0726-0503-s006764 | reverse | spare | 1 | pending |
| line-1 | line-1-0657-0561-s008788 | forward | spare | 1 | pending |
| line-1 | line-1-0657-0561-s008788 | reverse | spare | 1 | pending |
| line-1 | line-1-0587-0619-s010821 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0153-0365-s000000 | forward | revenue | 4 | pending |
| line-2 | line-2-0392-0541-s007002 | forward | revenue | 4 | pending |
| line-2 | line-2-0392-0541-s007002 | reverse | revenue | 4 | pending |
| line-2 | line-2-0503-0618-s010013 | forward | revenue | 4 | pending |
| line-2 | line-2-0503-0618-s010013 | reverse | revenue | 4 | pending |
| line-2 | line-2-0550-0650-s011276 | forward | revenue | 4 | pending |
| line-2 | line-2-0550-0650-s011276 | reverse | revenue | 4 | pending |
| line-2 | line-2-0602-0687-s012717 | forward | revenue | 4 | pending |
| line-2 | line-2-0602-0687-s012717 | reverse | revenue | 3 | pending |
| line-2 | line-2-0611-0693-s012958 | reverse | revenue | 3 | pending |
| line-2 | line-2-0602-0687-s012717 | reverse | spare | 1 | pending |
| line-2 | line-2-0611-0693-s012958 | reverse | spare | 1 | pending |
| line-2 | line-2-0153-0365-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0392-0541-s007002 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0662-0893-s000000 | forward | revenue | 4 | pending |
| line-3 | line-3-0602-0687-s004664 | forward | revenue | 4 | pending |
| line-3 | line-3-0602-0687-s004664 | reverse | revenue | 4 | pending |
| line-3 | line-3-0587-0619-s006148 | forward | revenue | 4 | pending |
| line-3 | line-3-0587-0619-s006148 | reverse | revenue | 4 | pending |
| line-3 | line-3-0570-0544-s007789 | forward | revenue | 3 | pending |
| line-3 | line-3-0570-0544-s007789 | reverse | revenue | 3 | pending |
| line-3 | line-3-0547-0439-s010091 | reverse | revenue | 3 | pending |
| line-3 | line-3-0570-0544-s007789 | forward | spare | 1 | pending |
| line-3 | line-3-0570-0544-s007789 | reverse | spare | 1 | pending |
| line-3 | line-3-0547-0439-s010091 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**74 trainsets exceed the reference platform envelope**, requiring **4,403.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0461-0724-s014492 | 4 | 2 | 2 | 119.0 |
| line-1-0550-0650-s011912 | 8 | 4 | 4 | 238.0 |
| line-1-0587-0619-s010821 | 9 | 4 | 5 | 297.5 |
| line-1-0657-0561-s008788 | 10 | 2 | 8 | 476.0 |
| line-1-0726-0503-s006764 | 10 | 2 | 8 | 476.0 |
| line-1-0962-0331-s000000 | 5 | 2 | 3 | 178.5 |
| line-2-0153-0365-s000000 | 5 | 2 | 3 | 178.5 |
| line-2-0392-0541-s007002 | 9 | 2 | 7 | 416.5 |
| line-2-0503-0618-s010013 | 8 | 2 | 6 | 357.0 |
| line-2-0550-0650-s011276 | 8 | 4 | 4 | 238.0 |
| line-2-0602-0687-s012717 | 8 | 4 | 4 | 238.0 |
| line-2-0611-0693-s012958 | 4 | 2 | 2 | 119.0 |
| line-3-0547-0439-s010091 | 4 | 2 | 2 | 119.0 |
| line-3-0570-0544-s007789 | 8 | 2 | 6 | 357.0 |
| line-3-0587-0619-s006148 | 8 | 4 | 4 | 238.0 |
| line-3-0602-0687-s004664 | 8 | 4 | 4 | 238.0 |
| line-3-0662-0893-s000000 | 4 | 2 | 2 | 119.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/south-asia/Pakistan/Bahawalpur/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
