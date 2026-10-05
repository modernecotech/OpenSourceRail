# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **28 trainsets at stations + 104 at depots = 132 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0694-0708-s000000 | line-1 | declared-depot | 31 | 1,844.5 | 6 |
| line-2-0938-0810-s018592 | line-2 | declared-depot | 49 | 2,915.5 | 9 |
| line-3-0871-0768-s000000 | line-3 | declared-depot | 24 | 1,428.0 | 5 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0566-0133-s012619 | station | reverse | revenue | 2 |
| line-1 | line-1-0631-0435-s006017 | station | forward | revenue | 1 |
| line-1 | line-1-0631-0435-s006017 | station | reverse | revenue | 1 |
| line-1 | line-1-0662-0571-s003017 | station | forward | revenue | 1 |
| line-1 | line-1-0662-0571-s003017 | station | reverse | revenue | 1 |
| line-1 | line-1-0694-0708-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0302-0278-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0470-0423-s005006 | station | forward | revenue | 1 |
| line-2 | line-2-0470-0423-s005006 | station | reverse | revenue | 1 |
| line-2 | line-2-0567-0507-s007888 | station | forward | revenue | 1 |
| line-2 | line-2-0567-0507-s007888 | station | reverse | revenue | 1 |
| line-2 | line-2-0685-0609-s011386 | station | forward | revenue | 1 |
| line-2 | line-2-0685-0609-s011386 | station | reverse | revenue | 1 |
| line-2 | line-2-0938-0810-s018592 | station | reverse | revenue | 2 |
| line-3 | line-3-0383-0664-s010622 | station | reverse | revenue | 2 |
| line-3 | line-3-0472-0683-s008684 | station | forward | revenue | 1 |
| line-3 | line-3-0472-0683-s008684 | station | reverse | revenue | 1 |
| line-3 | line-3-0560-0702-s006767 | station | forward | revenue | 1 |
| line-3 | line-3-0560-0702-s006767 | station | reverse | revenue | 1 |
| line-3 | line-3-0718-0735-s003333 | station | forward | revenue | 1 |
| line-3 | line-3-0718-0735-s003333 | station | reverse | revenue | 1 |
| line-3 | line-3-0871-0768-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0694-0708-s000000 | depot | — | revenue | 27 |
| line-1 | line-1-0694-0708-s000000 | depot | — | spare | 3 |
| line-1 | line-1-0694-0708-s000000 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0938-0810-s018592 | depot | — | revenue | 43 |
| line-2 | line-2-0938-0810-s018592 | depot | — | spare | 5 |
| line-2 | line-2-0938-0810-s018592 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0871-0768-s000000 | depot | — | revenue | 20 |
| line-3 | line-3-0871-0768-s000000 | depot | — | spare | 3 |
| line-3 | line-3-0871-0768-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/nampula-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **132 trainsets at 14 stations**; largest initial station queue **16**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **118 revenue, 11 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **28 positions**; **104 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **14 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0694-0708-s000000 | forward | revenue | 6 | pending |
| line-1 | line-1-0662-0571-s003017 | forward | revenue | 6 | pending |
| line-1 | line-1-0662-0571-s003017 | reverse | revenue | 6 | pending |
| line-1 | line-1-0631-0435-s006017 | forward | revenue | 6 | pending |
| line-1 | line-1-0631-0435-s006017 | reverse | revenue | 6 | pending |
| line-1 | line-1-0566-0133-s012619 | reverse | revenue | 5 | pending |
| line-1 | line-1-0566-0133-s012619 | reverse | spare | 1 | pending |
| line-1 | line-1-0694-0708-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0662-0571-s003017 | forward | spare | 1 | pending |
| line-1 | line-1-0662-0571-s003017 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0302-0278-s000000 | forward | revenue | 7 | pending |
| line-2 | line-2-0470-0423-s005006 | forward | revenue | 7 | pending |
| line-2 | line-2-0470-0423-s005006 | reverse | revenue | 7 | pending |
| line-2 | line-2-0567-0507-s007888 | forward | revenue | 7 | pending |
| line-2 | line-2-0567-0507-s007888 | reverse | revenue | 7 | pending |
| line-2 | line-2-0685-0609-s011386 | forward | revenue | 6 | pending |
| line-2 | line-2-0685-0609-s011386 | reverse | revenue | 6 | pending |
| line-2 | line-2-0938-0810-s018592 | reverse | revenue | 6 | pending |
| line-2 | line-2-0685-0609-s011386 | forward | spare | 1 | pending |
| line-2 | line-2-0685-0609-s011386 | reverse | spare | 1 | pending |
| line-2 | line-2-0938-0810-s018592 | reverse | spare | 1 | pending |
| line-2 | line-2-0302-0278-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0470-0423-s005006 | forward | spare | 1 | pending |
| line-2 | line-2-0470-0423-s005006 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0871-0768-s000000 | forward | revenue | 4 | pending |
| line-3 | line-3-0718-0735-s003333 | forward | revenue | 4 | pending |
| line-3 | line-3-0718-0735-s003333 | reverse | revenue | 4 | pending |
| line-3 | line-3-0560-0702-s006767 | forward | revenue | 4 | pending |
| line-3 | line-3-0560-0702-s006767 | reverse | revenue | 4 | pending |
| line-3 | line-3-0472-0683-s008684 | forward | revenue | 4 | pending |
| line-3 | line-3-0472-0683-s008684 | reverse | revenue | 3 | pending |
| line-3 | line-3-0383-0664-s010622 | reverse | revenue | 3 | pending |
| line-3 | line-3-0472-0683-s008684 | reverse | spare | 1 | pending |
| line-3 | line-3-0383-0664-s010622 | reverse | spare | 1 | pending |
| line-3 | line-3-0871-0768-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0718-0735-s003333 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**104 trainsets exceed the reference platform envelope**, requiring **6,188.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0566-0133-s012619 | 6 | 2 | 4 | 238.0 |
| line-1-0631-0435-s006017 | 12 | 2 | 10 | 595.0 |
| line-1-0662-0571-s003017 | 14 | 2 | 12 | 714.0 |
| line-1-0694-0708-s000000 | 7 | 2 | 5 | 297.5 |
| line-2-0302-0278-s000000 | 8 | 2 | 6 | 357.0 |
| line-2-0470-0423-s005006 | 16 | 2 | 14 | 833.0 |
| line-2-0567-0507-s007888 | 14 | 2 | 12 | 714.0 |
| line-2-0685-0609-s011386 | 14 | 2 | 12 | 714.0 |
| line-2-0938-0810-s018592 | 7 | 2 | 5 | 297.5 |
| line-3-0383-0664-s010622 | 4 | 2 | 2 | 119.0 |
| line-3-0472-0683-s008684 | 8 | 2 | 6 | 357.0 |
| line-3-0560-0702-s006767 | 8 | 2 | 6 | 357.0 |
| line-3-0718-0735-s003333 | 9 | 2 | 7 | 416.5 |
| line-3-0871-0768-s000000 | 5 | 2 | 3 | 178.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Mozambique/Nampula/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
