# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **44 trainsets at stations + 121 at depots = 165 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0703-0822-s020752 | line-1 | declared-depot | 54 | 3,213.0 | 10 |
| line-2-0449-0338-s000000 | line-2 | declared-depot | 28 | 1,666.0 | 6 |
| line-3-0861-0445-s000000 | line-3 | declared-depot | 20 | 1,190.0 | 5 |
| line-4-0588-0547-s000000 | line-4 | declared-depot | 19 | 1,130.5 | 4 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0151-0084-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0327-0332-s007005 | station | forward | revenue | 1 |
| line-1 | line-1-0327-0332-s007005 | station | reverse | revenue | 1 |
| line-1 | line-1-0452-0496-s011578 | station | forward | revenue | 1 |
| line-1 | line-1-0452-0496-s011578 | station | reverse | revenue | 1 |
| line-1 | line-1-0602-0691-s017037 | station | forward | revenue | 1 |
| line-1 | line-1-0602-0691-s017037 | station | reverse | revenue | 1 |
| line-1 | line-1-0606-0695-s017162 | station | forward | revenue | 1 |
| line-1 | line-1-0606-0695-s017162 | station | reverse | revenue | 1 |
| line-1 | line-1-0607-0698-s017231 | station | forward | revenue | 1 |
| line-1 | line-1-0607-0698-s017231 | station | reverse | revenue | 1 |
| line-1 | line-1-0703-0822-s020752 | station | reverse | revenue | 2 |
| line-2 | line-2-0449-0338-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0527-0456-s003006 | station | forward | revenue | 1 |
| line-2 | line-2-0527-0456-s003006 | station | reverse | revenue | 1 |
| line-2 | line-2-0590-0549-s006025 | station | forward | revenue | 1 |
| line-2 | line-2-0590-0549-s006025 | station | reverse | revenue | 1 |
| line-2 | line-2-0774-0527-s010915 | station | forward | revenue | 1 |
| line-2 | line-2-0774-0527-s010915 | station | reverse | revenue | 1 |
| line-2 | line-2-0814-0509-s012041 | station | reverse | revenue | 2 |
| line-3 | line-3-0590-0702-s009044 | station | reverse | revenue | 2 |
| line-3 | line-3-0602-0691-s008678 | station | forward | revenue | 1 |
| line-3 | line-3-0602-0691-s008678 | station | reverse | revenue | 1 |
| line-3 | line-3-0606-0695-s008381 | station | forward | revenue | 1 |
| line-3 | line-3-0606-0695-s008381 | station | reverse | revenue | 1 |
| line-3 | line-3-0607-0698-s008313 | station | forward | revenue | 1 |
| line-3 | line-3-0607-0698-s008313 | station | reverse | revenue | 1 |
| line-3 | line-3-0774-0527-s002665 | station | forward | revenue | 1 |
| line-3 | line-3-0774-0527-s002665 | station | reverse | revenue | 1 |
| line-3 | line-3-0861-0445-s000000 | station | forward | revenue | 2 |
| line-4 | line-4-0485-0243-s008421 | station | reverse | revenue | 2 |
| line-4 | line-4-0528-0335-s006225 | station | forward | revenue | 1 |
| line-4 | line-4-0528-0335-s006225 | station | reverse | revenue | 1 |
| line-4 | line-4-0577-0424-s004039 | station | forward | revenue | 1 |
| line-4 | line-4-0577-0424-s004039 | station | reverse | revenue | 1 |
| line-4 | line-4-0588-0547-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0703-0822-s020752 | depot | — | revenue | 47 |
| line-1 | line-1-0703-0822-s020752 | depot | — | spare | 6 |
| line-1 | line-1-0703-0822-s020752 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0449-0338-s000000 | depot | — | revenue | 24 |
| line-2 | line-2-0449-0338-s000000 | depot | — | spare | 3 |
| line-2 | line-2-0449-0338-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0861-0445-s000000 | depot | — | revenue | 17 |
| line-3 | line-3-0861-0445-s000000 | depot | — | spare | 2 |
| line-3 | line-3-0861-0445-s000000 | depot | — | cold_reserve | 1 |
| line-4 | line-4-0588-0547-s000000 | depot | — | revenue | 16 |
| line-4 | line-4-0588-0547-s000000 | depot | — | spare | 2 |
| line-4 | line-4-0588-0547-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/sukkur-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **165 trainsets at 22 stations**; largest initial station queue **12**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **148 revenue, 13 spare, 4 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **44 positions**; **121 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **22 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0151-0084-s000000 | forward | revenue | 6 | pending |
| line-1 | line-1-0327-0332-s007005 | forward | revenue | 5 | pending |
| line-1 | line-1-0327-0332-s007005 | reverse | revenue | 5 | pending |
| line-1 | line-1-0452-0496-s011578 | forward | revenue | 5 | pending |
| line-1 | line-1-0452-0496-s011578 | reverse | revenue | 5 | pending |
| line-1 | line-1-0602-0691-s017037 | forward | revenue | 5 | pending |
| line-1 | line-1-0602-0691-s017037 | reverse | revenue | 5 | pending |
| line-1 | line-1-0606-0695-s017162 | forward | revenue | 5 | pending |
| line-1 | line-1-0606-0695-s017162 | reverse | revenue | 5 | pending |
| line-1 | line-1-0607-0698-s017231 | forward | revenue | 5 | pending |
| line-1 | line-1-0607-0698-s017231 | reverse | revenue | 5 | pending |
| line-1 | line-1-0703-0822-s020752 | reverse | revenue | 5 | pending |
| line-1 | line-1-0327-0332-s007005 | forward | spare | 1 | pending |
| line-1 | line-1-0327-0332-s007005 | reverse | spare | 1 | pending |
| line-1 | line-1-0452-0496-s011578 | forward | spare | 1 | pending |
| line-1 | line-1-0452-0496-s011578 | reverse | spare | 1 | pending |
| line-1 | line-1-0602-0691-s017037 | forward | spare | 1 | pending |
| line-1 | line-1-0602-0691-s017037 | reverse | spare | 1 | pending |
| line-1 | line-1-0606-0695-s017162 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0449-0338-s000000 | forward | revenue | 5 | pending |
| line-2 | line-2-0527-0456-s003006 | forward | revenue | 5 | pending |
| line-2 | line-2-0527-0456-s003006 | reverse | revenue | 4 | pending |
| line-2 | line-2-0590-0549-s006025 | forward | revenue | 4 | pending |
| line-2 | line-2-0590-0549-s006025 | reverse | revenue | 4 | pending |
| line-2 | line-2-0774-0527-s010915 | forward | revenue | 4 | pending |
| line-2 | line-2-0774-0527-s010915 | reverse | revenue | 4 | pending |
| line-2 | line-2-0814-0509-s012041 | reverse | revenue | 4 | pending |
| line-2 | line-2-0527-0456-s003006 | reverse | spare | 1 | pending |
| line-2 | line-2-0590-0549-s006025 | forward | spare | 1 | pending |
| line-2 | line-2-0590-0549-s006025 | reverse | spare | 1 | pending |
| line-2 | line-2-0774-0527-s010915 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0861-0445-s000000 | forward | revenue | 3 | pending |
| line-3 | line-3-0774-0527-s002665 | forward | revenue | 3 | pending |
| line-3 | line-3-0774-0527-s002665 | reverse | revenue | 3 | pending |
| line-3 | line-3-0607-0698-s008313 | forward | revenue | 3 | pending |
| line-3 | line-3-0607-0698-s008313 | reverse | revenue | 3 | pending |
| line-3 | line-3-0606-0695-s008381 | forward | revenue | 3 | pending |
| line-3 | line-3-0606-0695-s008381 | reverse | revenue | 3 | pending |
| line-3 | line-3-0602-0691-s008678 | forward | revenue | 3 | pending |
| line-3 | line-3-0602-0691-s008678 | reverse | revenue | 3 | pending |
| line-3 | line-3-0590-0702-s009044 | reverse | revenue | 2 | pending |
| line-3 | line-3-0590-0702-s009044 | reverse | spare | 1 | pending |
| line-3 | line-3-0861-0445-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0774-0527-s002665 | forward | cold_reserve | 1 | pending |
| line-4 | line-4-0588-0547-s000000 | forward | revenue | 4 | pending |
| line-4 | line-4-0577-0424-s004039 | forward | revenue | 4 | pending |
| line-4 | line-4-0577-0424-s004039 | reverse | revenue | 4 | pending |
| line-4 | line-4-0528-0335-s006225 | forward | revenue | 4 | pending |
| line-4 | line-4-0528-0335-s006225 | reverse | revenue | 4 | pending |
| line-4 | line-4-0485-0243-s008421 | reverse | revenue | 4 | pending |
| line-4 | line-4-0588-0547-s000000 | forward | spare | 1 | pending |
| line-4 | line-4-0577-0424-s004039 | forward | spare | 1 | pending |
| line-4 | line-4-0577-0424-s004039 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**103 trainsets exceed the reference platform envelope**, requiring **6,128.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0151-0084-s000000 | 6 | 2 | 4 | 238.0 |
| line-1-0327-0332-s007005 | 12 | 2 | 10 | 595.0 |
| line-1-0452-0496-s011578 | 12 | 2 | 10 | 595.0 |
| line-1-0602-0691-s017037 | 12 | 4 | 8 | 476.0 |
| line-1-0606-0695-s017162 | 11 | 4 | 7 | 416.5 |
| line-1-0607-0698-s017231 | 10 | 4 | 6 | 357.0 |
| line-1-0703-0822-s020752 | 5 | 2 | 3 | 178.5 |
| line-2-0449-0338-s000000 | 5 | 2 | 3 | 178.5 |
| line-2-0527-0456-s003006 | 10 | 2 | 8 | 476.0 |
| line-2-0590-0549-s006025 | 10 | 4 | 6 | 357.0 |
| line-2-0774-0527-s010915 | 9 | 4 | 5 | 297.5 |
| line-2-0814-0509-s012041 | 4 | 2 | 2 | 119.0 |
| line-3-0590-0702-s009044 | 3 | 2 | 1 | 59.5 |
| line-3-0602-0691-s008678 | 6 | 4 | 2 | 119.0 |
| line-3-0606-0695-s008381 | 6 | 4 | 2 | 119.0 |
| line-3-0607-0698-s008313 | 6 | 4 | 2 | 119.0 |
| line-3-0774-0527-s002665 | 7 | 4 | 3 | 178.5 |
| line-3-0861-0445-s000000 | 4 | 2 | 2 | 119.0 |
| line-4-0485-0243-s008421 | 4 | 2 | 2 | 119.0 |
| line-4-0528-0335-s006225 | 8 | 2 | 6 | 357.0 |
| line-4-0577-0424-s004039 | 10 | 2 | 8 | 476.0 |
| line-4-0588-0547-s000000 | 5 | 2 | 3 | 178.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/south-asia/Pakistan/Sukkur/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
