# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **30 trainsets at stations + 111 at depots = 141 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0445-0353-s000000 | line-1 | declared-depot | 33 | 1,963.5 | 7 |
| line-2-0145-0992-s020028 | line-2 | declared-depot | 51 | 3,034.5 | 9 |
| line-3-0533-0317-s000000 | line-3 | declared-depot | 27 | 1,606.5 | 5 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0445-0353-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0484-0487-s003015 | station | forward | revenue | 1 |
| line-1 | line-1-0484-0487-s003015 | station | reverse | revenue | 1 |
| line-1 | line-1-0523-0620-s006033 | station | forward | revenue | 1 |
| line-1 | line-1-0523-0620-s006033 | station | reverse | revenue | 1 |
| line-1 | line-1-0555-0729-s008502 | station | forward | revenue | 1 |
| line-1 | line-1-0555-0729-s008502 | station | reverse | revenue | 1 |
| line-1 | line-1-0588-0838-s010967 | station | forward | revenue | 1 |
| line-1 | line-1-0588-0838-s010967 | station | reverse | revenue | 1 |
| line-1 | line-1-0647-0895-s013415 | station | reverse | revenue | 2 |
| line-2 | line-2-0145-0992-s020028 | station | reverse | revenue | 2 |
| line-2 | line-2-0510-0663-s009271 | station | forward | revenue | 1 |
| line-2 | line-2-0510-0663-s009271 | station | reverse | revenue | 1 |
| line-2 | line-2-0611-0572-s006252 | station | forward | revenue | 1 |
| line-2 | line-2-0611-0572-s006252 | station | reverse | revenue | 1 |
| line-2 | line-2-0710-0482-s003233 | station | forward | revenue | 1 |
| line-2 | line-2-0710-0482-s003233 | station | reverse | revenue | 1 |
| line-2 | line-2-0818-0385-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0533-0317-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0584-0444-s003009 | station | forward | revenue | 1 |
| line-3 | line-3-0584-0444-s003009 | station | reverse | revenue | 1 |
| line-3 | line-3-0635-0570-s006010 | station | forward | revenue | 1 |
| line-3 | line-3-0635-0570-s006010 | station | reverse | revenue | 1 |
| line-3 | line-3-0725-0794-s011318 | station | reverse | revenue | 2 |
| line-1 | line-1-0445-0353-s000000 | depot | — | revenue | 28 |
| line-1 | line-1-0445-0353-s000000 | depot | — | spare | 4 |
| line-1 | line-1-0445-0353-s000000 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0145-0992-s020028 | depot | — | revenue | 45 |
| line-2 | line-2-0145-0992-s020028 | depot | — | spare | 5 |
| line-2 | line-2-0145-0992-s020028 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0533-0317-s000000 | depot | — | revenue | 23 |
| line-3 | line-3-0533-0317-s000000 | depot | — | spare | 3 |
| line-3 | line-3-0533-0317-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/lubango-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **141 trainsets at 15 stations**; largest initial station queue **16**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **126 revenue, 12 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **30 positions**; **111 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **15 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0445-0353-s000000 | forward | revenue | 4 | pending |
| line-1 | line-1-0484-0487-s003015 | forward | revenue | 4 | pending |
| line-1 | line-1-0484-0487-s003015 | reverse | revenue | 4 | pending |
| line-1 | line-1-0523-0620-s006033 | forward | revenue | 4 | pending |
| line-1 | line-1-0523-0620-s006033 | reverse | revenue | 4 | pending |
| line-1 | line-1-0555-0729-s008502 | forward | revenue | 4 | pending |
| line-1 | line-1-0555-0729-s008502 | reverse | revenue | 4 | pending |
| line-1 | line-1-0588-0838-s010967 | forward | revenue | 4 | pending |
| line-1 | line-1-0588-0838-s010967 | reverse | revenue | 4 | pending |
| line-1 | line-1-0647-0895-s013415 | reverse | revenue | 4 | pending |
| line-1 | line-1-0445-0353-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0484-0487-s003015 | forward | spare | 1 | pending |
| line-1 | line-1-0484-0487-s003015 | reverse | spare | 1 | pending |
| line-1 | line-1-0523-0620-s006033 | forward | spare | 1 | pending |
| line-1 | line-1-0523-0620-s006033 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0818-0385-s000000 | forward | revenue | 7 | pending |
| line-2 | line-2-0710-0482-s003233 | forward | revenue | 7 | pending |
| line-2 | line-2-0710-0482-s003233 | reverse | revenue | 7 | pending |
| line-2 | line-2-0611-0572-s006252 | forward | revenue | 7 | pending |
| line-2 | line-2-0611-0572-s006252 | reverse | revenue | 7 | pending |
| line-2 | line-2-0510-0663-s009271 | forward | revenue | 7 | pending |
| line-2 | line-2-0510-0663-s009271 | reverse | revenue | 7 | pending |
| line-2 | line-2-0145-0992-s020028 | reverse | revenue | 6 | pending |
| line-2 | line-2-0145-0992-s020028 | reverse | spare | 1 | pending |
| line-2 | line-2-0818-0385-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0710-0482-s003233 | forward | spare | 1 | pending |
| line-2 | line-2-0710-0482-s003233 | reverse | spare | 1 | pending |
| line-2 | line-2-0611-0572-s006252 | forward | spare | 1 | pending |
| line-2 | line-2-0611-0572-s006252 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0533-0317-s000000 | forward | revenue | 6 | pending |
| line-3 | line-3-0584-0444-s003009 | forward | revenue | 5 | pending |
| line-3 | line-3-0584-0444-s003009 | reverse | revenue | 5 | pending |
| line-3 | line-3-0635-0570-s006010 | forward | revenue | 5 | pending |
| line-3 | line-3-0635-0570-s006010 | reverse | revenue | 5 | pending |
| line-3 | line-3-0725-0794-s011318 | reverse | revenue | 5 | pending |
| line-3 | line-3-0584-0444-s003009 | forward | spare | 1 | pending |
| line-3 | line-3-0584-0444-s003009 | reverse | spare | 1 | pending |
| line-3 | line-3-0635-0570-s006010 | forward | spare | 1 | pending |
| line-3 | line-3-0635-0570-s006010 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**107 trainsets exceed the reference platform envelope**, requiring **6,366.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0445-0353-s000000 | 5 | 2 | 3 | 178.5 |
| line-1-0484-0487-s003015 | 10 | 2 | 8 | 476.0 |
| line-1-0523-0620-s006033 | 10 | 2 | 8 | 476.0 |
| line-1-0555-0729-s008502 | 8 | 2 | 6 | 357.0 |
| line-1-0588-0838-s010967 | 8 | 2 | 6 | 357.0 |
| line-1-0647-0895-s013415 | 4 | 2 | 2 | 119.0 |
| line-2-0145-0992-s020028 | 7 | 2 | 5 | 297.5 |
| line-2-0510-0663-s009271 | 14 | 2 | 12 | 714.0 |
| line-2-0611-0572-s006252 | 16 | 4 | 12 | 714.0 |
| line-2-0710-0482-s003233 | 16 | 2 | 14 | 833.0 |
| line-2-0818-0385-s000000 | 8 | 2 | 6 | 357.0 |
| line-3-0533-0317-s000000 | 6 | 2 | 4 | 238.0 |
| line-3-0584-0444-s003009 | 12 | 2 | 10 | 595.0 |
| line-3-0635-0570-s006010 | 12 | 4 | 8 | 476.0 |
| line-3-0725-0794-s011318 | 5 | 2 | 3 | 178.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Angola/Lubango/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
