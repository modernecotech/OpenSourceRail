# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **28 trainsets at stations + 36 at depots = 64 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0565-0491-s000000 | line-1 | declared-depot | 12 | 588.0 | 3 |
| line-2-0404-0455-s000000 | line-2 | declared-depot | 8 | 392.0 | 3 |
| line-3-0420-0164-s012784 | line-3 | declared-depot | 16 | 784.0 | 4 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0297-0166-s009294 | station | reverse | revenue | 2 |
| line-1 | line-1-0457-0360-s003749 | station | forward | revenue | 1 |
| line-1 | line-1-0457-0360-s003749 | station | reverse | revenue | 1 |
| line-1 | line-1-0485-0394-s002781 | station | forward | revenue | 1 |
| line-1 | line-1-0485-0394-s002781 | station | reverse | revenue | 1 |
| line-1 | line-1-0565-0491-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0404-0455-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0466-0408-s001688 | station | forward | revenue | 1 |
| line-2 | line-2-0466-0408-s001688 | station | reverse | revenue | 1 |
| line-2 | line-2-0485-0394-s002237 | station | forward | revenue | 1 |
| line-2 | line-2-0485-0394-s002237 | station | reverse | revenue | 1 |
| line-2 | line-2-0562-0335-s004447 | station | forward | revenue | 1 |
| line-2 | line-2-0562-0335-s004447 | station | reverse | revenue | 1 |
| line-2 | line-2-0638-0268-s006667 | station | reverse | revenue | 2 |
| line-3 | line-3-0420-0164-s012784 | station | reverse | revenue | 2 |
| line-3 | line-3-0457-0360-s008546 | station | forward | revenue | 1 |
| line-3 | line-3-0457-0360-s008546 | station | reverse | revenue | 1 |
| line-3 | line-3-0466-0408-s007512 | station | forward | revenue | 1 |
| line-3 | line-3-0466-0408-s007512 | station | reverse | revenue | 1 |
| line-3 | line-3-0477-0464-s006300 | station | forward | revenue | 1 |
| line-3 | line-3-0477-0464-s006300 | station | reverse | revenue | 1 |
| line-3 | line-3-0536-0748-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0565-0491-s000000 | depot | — | revenue | 10 |
| line-1 | line-1-0565-0491-s000000 | depot | — | spare | 1 |
| line-1 | line-1-0565-0491-s000000 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0404-0455-s000000 | depot | — | revenue | 6 |
| line-2 | line-2-0404-0455-s000000 | depot | — | spare | 1 |
| line-2 | line-2-0404-0455-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0420-0164-s012784 | depot | — | revenue | 13 |
| line-3 | line-3-0420-0164-s012784 | depot | — | spare | 2 |
| line-3 | line-3-0420-0164-s012784 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/fort-portal-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **64 trainsets at 14 stations**; largest initial station queue **7**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **57 revenue, 4 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **28 positions**; **36 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **13 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0565-0491-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0485-0394-s002781 | forward | revenue | 3 | pending |
| line-1 | line-1-0485-0394-s002781 | reverse | revenue | 3 | pending |
| line-1 | line-1-0457-0360-s003749 | forward | revenue | 3 | pending |
| line-1 | line-1-0457-0360-s003749 | reverse | revenue | 3 | pending |
| line-1 | line-1-0297-0166-s009294 | reverse | revenue | 3 | pending |
| line-1 | line-1-0565-0491-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0485-0394-s002781 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0404-0455-s000000 | forward | revenue | 2 | pending |
| line-2 | line-2-0466-0408-s001688 | forward | revenue | 2 | pending |
| line-2 | line-2-0466-0408-s001688 | reverse | revenue | 2 | pending |
| line-2 | line-2-0485-0394-s002237 | forward | revenue | 2 | pending |
| line-2 | line-2-0485-0394-s002237 | reverse | revenue | 2 | pending |
| line-2 | line-2-0562-0335-s004447 | forward | revenue | 2 | pending |
| line-2 | line-2-0562-0335-s004447 | reverse | revenue | 2 | pending |
| line-2 | line-2-0638-0268-s006667 | reverse | revenue | 2 | pending |
| line-2 | line-2-0404-0455-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0466-0408-s001688 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0536-0748-s000000 | forward | revenue | 3 | pending |
| line-3 | line-3-0477-0464-s006300 | forward | revenue | 3 | pending |
| line-3 | line-3-0477-0464-s006300 | reverse | revenue | 3 | pending |
| line-3 | line-3-0466-0408-s007512 | forward | revenue | 3 | pending |
| line-3 | line-3-0466-0408-s007512 | reverse | revenue | 3 | pending |
| line-3 | line-3-0457-0360-s008546 | forward | revenue | 3 | pending |
| line-3 | line-3-0457-0360-s008546 | reverse | revenue | 3 | pending |
| line-3 | line-3-0420-0164-s012784 | reverse | revenue | 2 | pending |
| line-3 | line-3-0420-0164-s012784 | reverse | spare | 1 | pending |
| line-3 | line-3-0536-0748-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0477-0464-s006300 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**24 trainsets exceed the reference platform envelope**, requiring **1,176.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0297-0166-s009294 | 3 | 2 | 1 | 49.0 |
| line-1-0457-0360-s003749 | 6 | 4 | 2 | 98.0 |
| line-1-0485-0394-s002781 | 7 | 4 | 3 | 147.0 |
| line-1-0565-0491-s000000 | 4 | 2 | 2 | 98.0 |
| line-2-0404-0455-s000000 | 3 | 2 | 1 | 49.0 |
| line-2-0466-0408-s001688 | 5 | 4 | 1 | 49.0 |
| line-2-0485-0394-s002237 | 4 | 4 | 0 | 0.0 |
| line-2-0562-0335-s004447 | 4 | 2 | 2 | 98.0 |
| line-2-0638-0268-s006667 | 2 | 2 | 0 | 0.0 |
| line-3-0420-0164-s012784 | 3 | 2 | 1 | 49.0 |
| line-3-0457-0360-s008546 | 6 | 4 | 2 | 98.0 |
| line-3-0466-0408-s007512 | 6 | 4 | 2 | 98.0 |
| line-3-0477-0464-s006300 | 7 | 2 | 5 | 245.0 |
| line-3-0536-0748-s000000 | 4 | 2 | 2 | 98.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Uganda/Fort-Portal/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
