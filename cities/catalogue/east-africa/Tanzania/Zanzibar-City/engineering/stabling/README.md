# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **34 trainsets at stations + 116 at depots = 150 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0178-0650-s000000 | line-1 | declared-depot | 33 | 1,963.5 | 6 |
| line-2-0712-0922-s019039 | line-2 | declared-depot | 44 | 2,618.0 | 9 |
| line-3-1069-0872-s000000 | line-3 | declared-depot | 39 | 2,320.5 | 7 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0178-0650-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0415-0608-s005251 | station | forward | revenue | 1 |
| line-1 | line-1-0415-0608-s005251 | station | reverse | revenue | 1 |
| line-1 | line-1-0561-0597-s008262 | station | forward | revenue | 1 |
| line-1 | line-1-0561-0597-s008262 | station | reverse | revenue | 1 |
| line-1 | line-1-0694-0588-s010996 | station | forward | revenue | 1 |
| line-1 | line-1-0694-0588-s010996 | station | reverse | revenue | 1 |
| line-1 | line-1-0826-0578-s013719 | station | reverse | revenue | 2 |
| line-2 | line-2-0363-0136-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0504-0419-s006841 | station | forward | revenue | 1 |
| line-2 | line-2-0504-0419-s006841 | station | reverse | revenue | 1 |
| line-2 | line-2-0534-0485-s008445 | station | forward | revenue | 1 |
| line-2 | line-2-0534-0485-s008445 | station | reverse | revenue | 1 |
| line-2 | line-2-0564-0550-s010017 | station | forward | revenue | 1 |
| line-2 | line-2-0564-0550-s010017 | station | reverse | revenue | 1 |
| line-2 | line-2-0592-0610-s011472 | station | forward | revenue | 1 |
| line-2 | line-2-0592-0610-s011472 | station | reverse | revenue | 1 |
| line-2 | line-2-0628-0688-s013365 | station | forward | revenue | 1 |
| line-2 | line-2-0628-0688-s013365 | station | reverse | revenue | 1 |
| line-2 | line-2-0664-0766-s015259 | station | forward | revenue | 1 |
| line-2 | line-2-0664-0766-s015259 | station | reverse | revenue | 1 |
| line-2 | line-2-0712-0922-s019039 | station | reverse | revenue | 2 |
| line-3 | line-3-0434-0670-s014642 | station | reverse | revenue | 2 |
| line-3 | line-3-0531-0688-s012553 | station | forward | revenue | 1 |
| line-3 | line-3-0531-0688-s012553 | station | reverse | revenue | 1 |
| line-3 | line-3-0628-0706-s010464 | station | forward | revenue | 1 |
| line-3 | line-3-0628-0706-s010464 | station | reverse | revenue | 1 |
| line-3 | line-3-1069-0872-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0178-0650-s000000 | depot | — | revenue | 29 |
| line-1 | line-1-0178-0650-s000000 | depot | — | spare | 3 |
| line-1 | line-1-0178-0650-s000000 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0712-0922-s019039 | depot | — | revenue | 38 |
| line-2 | line-2-0712-0922-s019039 | depot | — | spare | 5 |
| line-2 | line-2-0712-0922-s019039 | depot | — | cold_reserve | 1 |
| line-3 | line-3-1069-0872-s000000 | depot | — | revenue | 34 |
| line-3 | line-3-1069-0872-s000000 | depot | — | spare | 4 |
| line-3 | line-3-1069-0872-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/zanzibar-city-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **150 trainsets at 17 stations**; largest initial station queue **16**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **135 revenue, 12 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **34 positions**; **116 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **17 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0178-0650-s000000 | forward | revenue | 5 | pending |
| line-1 | line-1-0415-0608-s005251 | forward | revenue | 5 | pending |
| line-1 | line-1-0415-0608-s005251 | reverse | revenue | 5 | pending |
| line-1 | line-1-0561-0597-s008262 | forward | revenue | 5 | pending |
| line-1 | line-1-0561-0597-s008262 | reverse | revenue | 5 | pending |
| line-1 | line-1-0694-0588-s010996 | forward | revenue | 5 | pending |
| line-1 | line-1-0694-0588-s010996 | reverse | revenue | 5 | pending |
| line-1 | line-1-0826-0578-s013719 | reverse | revenue | 4 | pending |
| line-1 | line-1-0826-0578-s013719 | reverse | spare | 1 | pending |
| line-1 | line-1-0178-0650-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0415-0608-s005251 | forward | spare | 1 | pending |
| line-1 | line-1-0415-0608-s005251 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0363-0136-s000000 | forward | revenue | 4 | pending |
| line-2 | line-2-0504-0419-s006841 | forward | revenue | 4 | pending |
| line-2 | line-2-0504-0419-s006841 | reverse | revenue | 4 | pending |
| line-2 | line-2-0534-0485-s008445 | forward | revenue | 4 | pending |
| line-2 | line-2-0534-0485-s008445 | reverse | revenue | 4 | pending |
| line-2 | line-2-0564-0550-s010017 | forward | revenue | 4 | pending |
| line-2 | line-2-0564-0550-s010017 | reverse | revenue | 4 | pending |
| line-2 | line-2-0592-0610-s011472 | forward | revenue | 4 | pending |
| line-2 | line-2-0592-0610-s011472 | reverse | revenue | 4 | pending |
| line-2 | line-2-0628-0688-s013365 | forward | revenue | 4 | pending |
| line-2 | line-2-0628-0688-s013365 | reverse | revenue | 4 | pending |
| line-2 | line-2-0664-0766-s015259 | forward | revenue | 4 | pending |
| line-2 | line-2-0664-0766-s015259 | reverse | revenue | 3 | pending |
| line-2 | line-2-0712-0922-s019039 | reverse | revenue | 3 | pending |
| line-2 | line-2-0664-0766-s015259 | reverse | spare | 1 | pending |
| line-2 | line-2-0712-0922-s019039 | reverse | spare | 1 | pending |
| line-2 | line-2-0363-0136-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0504-0419-s006841 | forward | spare | 1 | pending |
| line-2 | line-2-0504-0419-s006841 | reverse | spare | 1 | pending |
| line-2 | line-2-0534-0485-s008445 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-1069-0872-s000000 | forward | revenue | 7 | pending |
| line-3 | line-3-0628-0706-s010464 | forward | revenue | 7 | pending |
| line-3 | line-3-0628-0706-s010464 | reverse | revenue | 7 | pending |
| line-3 | line-3-0531-0688-s012553 | forward | revenue | 7 | pending |
| line-3 | line-3-0531-0688-s012553 | reverse | revenue | 7 | pending |
| line-3 | line-3-0434-0670-s014642 | reverse | revenue | 7 | pending |
| line-3 | line-3-1069-0872-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0628-0706-s010464 | forward | spare | 1 | pending |
| line-3 | line-3-0628-0706-s010464 | reverse | spare | 1 | pending |
| line-3 | line-3-0531-0688-s012553 | forward | spare | 1 | pending |
| line-3 | line-3-0531-0688-s012553 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**108 trainsets exceed the reference platform envelope**, requiring **6,426.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0178-0650-s000000 | 6 | 2 | 4 | 238.0 |
| line-1-0415-0608-s005251 | 12 | 2 | 10 | 595.0 |
| line-1-0561-0597-s008262 | 10 | 4 | 6 | 357.0 |
| line-1-0694-0588-s010996 | 10 | 2 | 8 | 476.0 |
| line-1-0826-0578-s013719 | 5 | 2 | 3 | 178.5 |
| line-2-0363-0136-s000000 | 5 | 2 | 3 | 178.5 |
| line-2-0504-0419-s006841 | 10 | 2 | 8 | 476.0 |
| line-2-0534-0485-s008445 | 9 | 2 | 7 | 416.5 |
| line-2-0564-0550-s010017 | 8 | 2 | 6 | 357.0 |
| line-2-0592-0610-s011472 | 8 | 4 | 4 | 238.0 |
| line-2-0628-0688-s013365 | 8 | 4 | 4 | 238.0 |
| line-2-0664-0766-s015259 | 8 | 2 | 6 | 357.0 |
| line-2-0712-0922-s019039 | 4 | 2 | 2 | 119.0 |
| line-3-0434-0670-s014642 | 7 | 2 | 5 | 297.5 |
| line-3-0531-0688-s012553 | 16 | 2 | 14 | 833.0 |
| line-3-0628-0706-s010464 | 16 | 4 | 12 | 714.0 |
| line-3-1069-0872-s000000 | 8 | 2 | 6 | 357.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Tanzania/Zanzibar-City/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
