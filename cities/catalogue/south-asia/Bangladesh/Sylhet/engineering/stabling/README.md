# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **40 trainsets at stations + 152 at depots = 192 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0479-0844-s000000 | line-1 | declared-depot | 32 | 1,904.0 | 7 |
| line-2-0274-0567-s026629 | line-2 | declared-depot | 69 | 4,105.5 | 12 |
| line-3-0676-0728-s000000 | line-3 | declared-depot | 23 | 1,368.5 | 5 |
| line-4-0513-0606-s000000 | line-4 | declared-depot | 28 | 1,666.0 | 5 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0393-0371-s014228 | station | reverse | revenue | 2 |
| line-1 | line-1-0431-0448-s012056 | station | forward | revenue | 1 |
| line-1 | line-1-0431-0448-s012056 | station | reverse | revenue | 1 |
| line-1 | line-1-0479-0844-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0485-0509-s009893 | station | forward | revenue | 1 |
| line-1 | line-1-0485-0509-s009893 | station | reverse | revenue | 1 |
| line-1 | line-1-0551-0552-s007713 | station | forward | revenue | 1 |
| line-1 | line-1-0551-0552-s007713 | station | reverse | revenue | 1 |
| line-1 | line-1-0567-0700-s003971 | station | forward | revenue | 1 |
| line-1 | line-1-0567-0700-s003971 | station | reverse | revenue | 1 |
| line-1 | line-1-0582-0615-s006020 | station | forward | revenue | 1 |
| line-1 | line-1-0582-0615-s006020 | station | reverse | revenue | 1 |
| line-2 | line-2-0274-0567-s026629 | station | reverse | revenue | 2 |
| line-2 | line-2-0513-0606-s019797 | station | forward | revenue | 1 |
| line-2 | line-2-0513-0606-s019797 | station | reverse | revenue | 1 |
| line-2 | line-2-0551-0551-s018108 | station | forward | revenue | 1 |
| line-2 | line-2-0551-0551-s018108 | station | reverse | revenue | 1 |
| line-2 | line-2-0573-0551-s017315 | station | forward | revenue | 1 |
| line-2 | line-2-0573-0551-s017315 | station | reverse | revenue | 1 |
| line-2 | line-2-0716-0477-s012908 | station | forward | revenue | 1 |
| line-2 | line-2-0716-0477-s012908 | station | reverse | revenue | 1 |
| line-2 | line-2-1084-0152-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0454-0347-s009670 | station | reverse | revenue | 2 |
| line-3 | line-3-0573-0551-s004487 | station | forward | revenue | 1 |
| line-3 | line-3-0573-0551-s004487 | station | reverse | revenue | 1 |
| line-3 | line-3-0607-0610-s003002 | station | forward | revenue | 1 |
| line-3 | line-3-0607-0610-s003002 | station | reverse | revenue | 1 |
| line-3 | line-3-0676-0728-s000000 | station | forward | revenue | 2 |
| line-4 | line-4-0513-0606-s000000 | station | forward | revenue | 2 |
| line-4 | line-4-0567-0700-s002525 | station | forward | revenue | 1 |
| line-4 | line-4-0567-0700-s002525 | station | reverse | revenue | 1 |
| line-4 | line-4-0794-0964-s010361 | station | reverse | revenue | 2 |
| line-1 | line-1-0479-0844-s000000 | depot | — | revenue | 27 |
| line-1 | line-1-0479-0844-s000000 | depot | — | spare | 4 |
| line-1 | line-1-0479-0844-s000000 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0274-0567-s026629 | depot | — | revenue | 61 |
| line-2 | line-2-0274-0567-s026629 | depot | — | spare | 7 |
| line-2 | line-2-0274-0567-s026629 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0676-0728-s000000 | depot | — | revenue | 20 |
| line-3 | line-3-0676-0728-s000000 | depot | — | spare | 2 |
| line-3 | line-3-0676-0728-s000000 | depot | — | cold_reserve | 1 |
| line-4 | line-4-0513-0606-s000000 | depot | — | revenue | 24 |
| line-4 | line-4-0513-0606-s000000 | depot | — | spare | 3 |
| line-4 | line-4-0513-0606-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/sylhet-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **192 trainsets at 20 stations**; largest initial station queue **17**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **172 revenue, 16 spare, 4 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **40 positions**; **152 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **20 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0479-0844-s000000 | forward | revenue | 4 | pending |
| line-1 | line-1-0567-0700-s003971 | forward | revenue | 4 | pending |
| line-1 | line-1-0567-0700-s003971 | reverse | revenue | 4 | pending |
| line-1 | line-1-0582-0615-s006020 | forward | revenue | 4 | pending |
| line-1 | line-1-0582-0615-s006020 | reverse | revenue | 4 | pending |
| line-1 | line-1-0551-0552-s007713 | forward | revenue | 3 | pending |
| line-1 | line-1-0551-0552-s007713 | reverse | revenue | 3 | pending |
| line-1 | line-1-0485-0509-s009893 | forward | revenue | 3 | pending |
| line-1 | line-1-0485-0509-s009893 | reverse | revenue | 3 | pending |
| line-1 | line-1-0431-0448-s012056 | forward | revenue | 3 | pending |
| line-1 | line-1-0431-0448-s012056 | reverse | revenue | 3 | pending |
| line-1 | line-1-0393-0371-s014228 | reverse | revenue | 3 | pending |
| line-1 | line-1-0551-0552-s007713 | forward | spare | 1 | pending |
| line-1 | line-1-0551-0552-s007713 | reverse | spare | 1 | pending |
| line-1 | line-1-0485-0509-s009893 | forward | spare | 1 | pending |
| line-1 | line-1-0485-0509-s009893 | reverse | spare | 1 | pending |
| line-1 | line-1-0431-0448-s012056 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-1084-0152-s000000 | forward | revenue | 8 | pending |
| line-2 | line-2-0716-0477-s012908 | forward | revenue | 8 | pending |
| line-2 | line-2-0716-0477-s012908 | reverse | revenue | 8 | pending |
| line-2 | line-2-0573-0551-s017315 | forward | revenue | 7 | pending |
| line-2 | line-2-0573-0551-s017315 | reverse | revenue | 7 | pending |
| line-2 | line-2-0551-0551-s018108 | forward | revenue | 7 | pending |
| line-2 | line-2-0551-0551-s018108 | reverse | revenue | 7 | pending |
| line-2 | line-2-0513-0606-s019797 | forward | revenue | 7 | pending |
| line-2 | line-2-0513-0606-s019797 | reverse | revenue | 7 | pending |
| line-2 | line-2-0274-0567-s026629 | reverse | revenue | 7 | pending |
| line-2 | line-2-0573-0551-s017315 | forward | spare | 1 | pending |
| line-2 | line-2-0573-0551-s017315 | reverse | spare | 1 | pending |
| line-2 | line-2-0551-0551-s018108 | forward | spare | 1 | pending |
| line-2 | line-2-0551-0551-s018108 | reverse | spare | 1 | pending |
| line-2 | line-2-0513-0606-s019797 | forward | spare | 1 | pending |
| line-2 | line-2-0513-0606-s019797 | reverse | spare | 1 | pending |
| line-2 | line-2-0274-0567-s026629 | reverse | spare | 1 | pending |
| line-2 | line-2-1084-0152-s000000 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0676-0728-s000000 | forward | revenue | 5 | pending |
| line-3 | line-3-0607-0610-s003002 | forward | revenue | 5 | pending |
| line-3 | line-3-0607-0610-s003002 | reverse | revenue | 5 | pending |
| line-3 | line-3-0573-0551-s004487 | forward | revenue | 5 | pending |
| line-3 | line-3-0573-0551-s004487 | reverse | revenue | 4 | pending |
| line-3 | line-3-0454-0347-s009670 | reverse | revenue | 4 | pending |
| line-3 | line-3-0573-0551-s004487 | reverse | spare | 1 | pending |
| line-3 | line-3-0454-0347-s009670 | reverse | spare | 1 | pending |
| line-3 | line-3-0676-0728-s000000 | forward | cold_reserve | 1 | pending |
| line-4 | line-4-0513-0606-s000000 | forward | revenue | 8 | pending |
| line-4 | line-4-0567-0700-s002525 | forward | revenue | 8 | pending |
| line-4 | line-4-0567-0700-s002525 | reverse | revenue | 7 | pending |
| line-4 | line-4-0794-0964-s010361 | reverse | revenue | 7 | pending |
| line-4 | line-4-0567-0700-s002525 | reverse | spare | 1 | pending |
| line-4 | line-4-0794-0964-s010361 | reverse | spare | 1 | pending |
| line-4 | line-4-0513-0606-s000000 | forward | spare | 1 | pending |
| line-4 | line-4-0567-0700-s002525 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**134 trainsets exceed the reference platform envelope**, requiring **7,973.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0393-0371-s014228 | 3 | 2 | 1 | 59.5 |
| line-1-0431-0448-s012056 | 7 | 2 | 5 | 297.5 |
| line-1-0479-0844-s000000 | 4 | 2 | 2 | 119.0 |
| line-1-0485-0509-s009893 | 8 | 2 | 6 | 357.0 |
| line-1-0551-0552-s007713 | 8 | 4 | 4 | 238.0 |
| line-1-0567-0700-s003971 | 8 | 4 | 4 | 238.0 |
| line-1-0582-0615-s006020 | 8 | 4 | 4 | 238.0 |
| line-2-0274-0567-s026629 | 8 | 2 | 6 | 357.0 |
| line-2-0513-0606-s019797 | 16 | 4 | 12 | 714.0 |
| line-2-0551-0551-s018108 | 16 | 4 | 12 | 714.0 |
| line-2-0573-0551-s017315 | 16 | 4 | 12 | 714.0 |
| line-2-0716-0477-s012908 | 16 | 2 | 14 | 833.0 |
| line-2-1084-0152-s000000 | 9 | 2 | 7 | 416.5 |
| line-3-0454-0347-s009670 | 5 | 2 | 3 | 178.5 |
| line-3-0573-0551-s004487 | 10 | 4 | 6 | 357.0 |
| line-3-0607-0610-s003002 | 10 | 4 | 6 | 357.0 |
| line-3-0676-0728-s000000 | 6 | 2 | 4 | 238.0 |
| line-4-0513-0606-s000000 | 9 | 2 | 7 | 416.5 |
| line-4-0567-0700-s002525 | 17 | 4 | 13 | 773.5 |
| line-4-0794-0964-s010361 | 8 | 2 | 6 | 357.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/south-asia/Bangladesh/Sylhet/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
