# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **26 trainsets at stations + 48 at depots = 74 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0204-0204-s000000 | line-1 | declared-depot | 17 | 833.0 | 4 |
| line-2-0706-0380-s000000 | line-2 | declared-depot | 11 | 539.0 | 3 |
| line-3-0122-0114-s014894 | line-3 | declared-depot | 20 | 980.0 | 5 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0204-0204-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0366-0302-s004204 | station | forward | revenue | 1 |
| line-1 | line-1-0366-0302-s004204 | station | reverse | revenue | 1 |
| line-1 | line-1-0500-0384-s007716 | station | forward | revenue | 1 |
| line-1 | line-1-0500-0384-s007716 | station | reverse | revenue | 1 |
| line-1 | line-1-0640-0455-s011221 | station | forward | revenue | 1 |
| line-1 | line-1-0640-0455-s011221 | station | reverse | revenue | 1 |
| line-1 | line-1-0728-0413-s013700 | station | reverse | revenue | 2 |
| line-2 | line-2-0354-0390-s008280 | station | reverse | revenue | 2 |
| line-2 | line-2-0464-0391-s006072 | station | forward | revenue | 1 |
| line-2 | line-2-0464-0391-s006072 | station | reverse | revenue | 1 |
| line-2 | line-2-0706-0380-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0122-0114-s014894 | station | reverse | revenue | 2 |
| line-3 | line-3-0253-0248-s010707 | station | forward | revenue | 1 |
| line-3 | line-3-0253-0248-s010707 | station | reverse | revenue | 1 |
| line-3 | line-3-0383-0380-s006521 | station | forward | revenue | 1 |
| line-3 | line-3-0383-0380-s006521 | station | reverse | revenue | 1 |
| line-3 | line-3-0444-0443-s004568 | station | forward | revenue | 1 |
| line-3 | line-3-0444-0443-s004568 | station | reverse | revenue | 1 |
| line-3 | line-3-0586-0588-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0204-0204-s000000 | depot | — | revenue | 14 |
| line-1 | line-1-0204-0204-s000000 | depot | — | spare | 2 |
| line-1 | line-1-0204-0204-s000000 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0706-0380-s000000 | depot | — | revenue | 9 |
| line-2 | line-2-0706-0380-s000000 | depot | — | spare | 1 |
| line-2 | line-2-0706-0380-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0122-0114-s014894 | depot | — | revenue | 17 |
| line-3 | line-3-0122-0114-s014894 | depot | — | spare | 2 |
| line-3 | line-3-0122-0114-s014894 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/naivasha-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **74 trainsets at 13 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **66 revenue, 5 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **26 positions**; **48 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **13 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0204-0204-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0366-0302-s004204 | forward | revenue | 3 | pending |
| line-1 | line-1-0366-0302-s004204 | reverse | revenue | 3 | pending |
| line-1 | line-1-0500-0384-s007716 | forward | revenue | 3 | pending |
| line-1 | line-1-0500-0384-s007716 | reverse | revenue | 3 | pending |
| line-1 | line-1-0640-0455-s011221 | forward | revenue | 3 | pending |
| line-1 | line-1-0640-0455-s011221 | reverse | revenue | 3 | pending |
| line-1 | line-1-0728-0413-s013700 | reverse | revenue | 3 | pending |
| line-1 | line-1-0204-0204-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0366-0302-s004204 | forward | spare | 1 | pending |
| line-1 | line-1-0366-0302-s004204 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0706-0380-s000000 | forward | revenue | 4 | pending |
| line-2 | line-2-0464-0391-s006072 | forward | revenue | 4 | pending |
| line-2 | line-2-0464-0391-s006072 | reverse | revenue | 4 | pending |
| line-2 | line-2-0354-0390-s008280 | reverse | revenue | 3 | pending |
| line-2 | line-2-0354-0390-s008280 | reverse | spare | 1 | pending |
| line-2 | line-2-0706-0380-s000000 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0586-0588-s000000 | forward | revenue | 4 | pending |
| line-3 | line-3-0444-0443-s004568 | forward | revenue | 4 | pending |
| line-3 | line-3-0444-0443-s004568 | reverse | revenue | 4 | pending |
| line-3 | line-3-0383-0380-s006521 | forward | revenue | 3 | pending |
| line-3 | line-3-0383-0380-s006521 | reverse | revenue | 3 | pending |
| line-3 | line-3-0253-0248-s010707 | forward | revenue | 3 | pending |
| line-3 | line-3-0253-0248-s010707 | reverse | revenue | 3 | pending |
| line-3 | line-3-0122-0114-s014894 | reverse | revenue | 3 | pending |
| line-3 | line-3-0383-0380-s006521 | forward | spare | 1 | pending |
| line-3 | line-3-0383-0380-s006521 | reverse | spare | 1 | pending |
| line-3 | line-3-0253-0248-s010707 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**46 trainsets exceed the reference platform envelope**, requiring **2,254.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0204-0204-s000000 | 4 | 2 | 2 | 98.0 |
| line-1-0366-0302-s004204 | 8 | 2 | 6 | 294.0 |
| line-1-0500-0384-s007716 | 6 | 2 | 4 | 196.0 |
| line-1-0640-0455-s011221 | 6 | 2 | 4 | 196.0 |
| line-1-0728-0413-s013700 | 3 | 2 | 1 | 49.0 |
| line-2-0354-0390-s008280 | 4 | 2 | 2 | 98.0 |
| line-2-0464-0391-s006072 | 8 | 2 | 6 | 294.0 |
| line-2-0706-0380-s000000 | 5 | 2 | 3 | 147.0 |
| line-3-0122-0114-s014894 | 3 | 2 | 1 | 49.0 |
| line-3-0253-0248-s010707 | 7 | 2 | 5 | 245.0 |
| line-3-0383-0380-s006521 | 8 | 4 | 4 | 196.0 |
| line-3-0444-0443-s004568 | 8 | 2 | 6 | 294.0 |
| line-3-0586-0588-s000000 | 4 | 2 | 2 | 98.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Kenya/Naivasha/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
