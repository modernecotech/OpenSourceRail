# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **42 trainsets at stations + 140 at depots = 182 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0694-0708-s000000 | line-1 | declared-depot | 42 | 2,499.0 | 8 |
| line-2-0938-0810-s018943 | line-2 | declared-depot | 48 | 2,856.0 | 9 |
| line-3-0871-0768-s000000 | line-3 | declared-depot | 24 | 1,428.0 | 5 |
| line-4-0588-0607-s000000 | line-4 | declared-depot | 14 | 833.0 | 3 |
| line-5-0621-0715-s000000 | line-5 | declared-depot | 12 | 714.0 | 3 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0505-0384-s010214 | station | forward | revenue | 1 |
| line-1 | line-1-0505-0384-s010214 | station | reverse | revenue | 1 |
| line-1 | line-1-0512-0459-s008639 | station | forward | revenue | 1 |
| line-1 | line-1-0512-0459-s008639 | station | reverse | revenue | 1 |
| line-1 | line-1-0566-0133-s016925 | station | reverse | revenue | 2 |
| line-1 | line-1-0588-0607-s004278 | station | forward | revenue | 1 |
| line-1 | line-1-0588-0607-s004278 | station | reverse | revenue | 1 |
| line-1 | line-1-0694-0708-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0302-0278-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0512-0459-s006238 | station | forward | revenue | 1 |
| line-2 | line-2-0512-0459-s006238 | station | reverse | revenue | 1 |
| line-2 | line-2-0567-0507-s007888 | station | forward | revenue | 1 |
| line-2 | line-2-0567-0507-s007888 | station | reverse | revenue | 1 |
| line-2 | line-2-0685-0609-s011386 | station | forward | revenue | 1 |
| line-2 | line-2-0685-0609-s011386 | station | reverse | revenue | 1 |
| line-2 | line-2-0868-0767-s016824 | station | forward | revenue | 1 |
| line-2 | line-2-0868-0767-s016824 | station | reverse | revenue | 1 |
| line-2 | line-2-0938-0810-s018943 | station | reverse | revenue | 2 |
| line-3 | line-3-0383-0664-s010622 | station | reverse | revenue | 2 |
| line-3 | line-3-0472-0683-s008684 | station | forward | revenue | 1 |
| line-3 | line-3-0472-0683-s008684 | station | reverse | revenue | 1 |
| line-3 | line-3-0621-0715-s005439 | station | forward | revenue | 1 |
| line-3 | line-3-0621-0715-s005439 | station | reverse | revenue | 1 |
| line-3 | line-3-0868-0767-s000068 | station | forward | revenue | 1 |
| line-3 | line-3-0868-0767-s000068 | station | reverse | revenue | 1 |
| line-3 | line-3-0871-0768-s000000 | station | forward | revenue | 2 |
| line-4 | line-4-0473-0587-s003006 | station | forward | revenue | 1 |
| line-4 | line-4-0473-0587-s003006 | station | reverse | revenue | 1 |
| line-4 | line-4-0487-0486-s006506 | station | reverse | revenue | 2 |
| line-4 | line-4-0588-0607-s000000 | station | forward | revenue | 2 |
| line-5 | line-5-0562-0863-s004781 | station | reverse | revenue | 2 |
| line-5 | line-5-0621-0715-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0694-0708-s000000 | depot | — | revenue | 37 |
| line-1 | line-1-0694-0708-s000000 | depot | — | spare | 4 |
| line-1 | line-1-0694-0708-s000000 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0938-0810-s018943 | depot | — | revenue | 42 |
| line-2 | line-2-0938-0810-s018943 | depot | — | spare | 5 |
| line-2 | line-2-0938-0810-s018943 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0871-0768-s000000 | depot | — | revenue | 20 |
| line-3 | line-3-0871-0768-s000000 | depot | — | spare | 3 |
| line-3 | line-3-0871-0768-s000000 | depot | — | cold_reserve | 1 |
| line-4 | line-4-0588-0607-s000000 | depot | — | revenue | 12 |
| line-4 | line-4-0588-0607-s000000 | depot | — | spare | 1 |
| line-4 | line-4-0588-0607-s000000 | depot | — | cold_reserve | 1 |
| line-5 | line-5-0621-0715-s000000 | depot | — | revenue | 10 |
| line-5 | line-5-0621-0715-s000000 | depot | — | spare | 1 |
| line-5 | line-5-0621-0715-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/nampula-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **182 trainsets at 21 stations**; largest initial station queue **14**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **163 revenue, 14 spare, 5 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **42 positions**; **140 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **21 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0694-0708-s000000 | forward | revenue | 6 | pending |
| line-1 | line-1-0588-0607-s004278 | forward | revenue | 6 | pending |
| line-1 | line-1-0588-0607-s004278 | reverse | revenue | 6 | pending |
| line-1 | line-1-0512-0459-s008639 | forward | revenue | 6 | pending |
| line-1 | line-1-0512-0459-s008639 | reverse | revenue | 6 | pending |
| line-1 | line-1-0505-0384-s010214 | forward | revenue | 6 | pending |
| line-1 | line-1-0505-0384-s010214 | reverse | revenue | 6 | pending |
| line-1 | line-1-0566-0133-s016925 | reverse | revenue | 5 | pending |
| line-1 | line-1-0566-0133-s016925 | reverse | spare | 1 | pending |
| line-1 | line-1-0694-0708-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0588-0607-s004278 | forward | spare | 1 | pending |
| line-1 | line-1-0588-0607-s004278 | reverse | spare | 1 | pending |
| line-1 | line-1-0512-0459-s008639 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0302-0278-s000000 | forward | revenue | 6 | pending |
| line-2 | line-2-0512-0459-s006238 | forward | revenue | 6 | pending |
| line-2 | line-2-0512-0459-s006238 | reverse | revenue | 6 | pending |
| line-2 | line-2-0567-0507-s007888 | forward | revenue | 6 | pending |
| line-2 | line-2-0567-0507-s007888 | reverse | revenue | 5 | pending |
| line-2 | line-2-0685-0609-s011386 | forward | revenue | 5 | pending |
| line-2 | line-2-0685-0609-s011386 | reverse | revenue | 5 | pending |
| line-2 | line-2-0868-0767-s016824 | forward | revenue | 5 | pending |
| line-2 | line-2-0868-0767-s016824 | reverse | revenue | 5 | pending |
| line-2 | line-2-0938-0810-s018943 | reverse | revenue | 5 | pending |
| line-2 | line-2-0567-0507-s007888 | reverse | spare | 1 | pending |
| line-2 | line-2-0685-0609-s011386 | forward | spare | 1 | pending |
| line-2 | line-2-0685-0609-s011386 | reverse | spare | 1 | pending |
| line-2 | line-2-0868-0767-s016824 | forward | spare | 1 | pending |
| line-2 | line-2-0868-0767-s016824 | reverse | spare | 1 | pending |
| line-2 | line-2-0938-0810-s018943 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0871-0768-s000000 | forward | revenue | 4 | pending |
| line-3 | line-3-0868-0767-s000068 | forward | revenue | 4 | pending |
| line-3 | line-3-0868-0767-s000068 | reverse | revenue | 4 | pending |
| line-3 | line-3-0621-0715-s005439 | forward | revenue | 4 | pending |
| line-3 | line-3-0621-0715-s005439 | reverse | revenue | 4 | pending |
| line-3 | line-3-0472-0683-s008684 | forward | revenue | 4 | pending |
| line-3 | line-3-0472-0683-s008684 | reverse | revenue | 3 | pending |
| line-3 | line-3-0383-0664-s010622 | reverse | revenue | 3 | pending |
| line-3 | line-3-0472-0683-s008684 | reverse | spare | 1 | pending |
| line-3 | line-3-0383-0664-s010622 | reverse | spare | 1 | pending |
| line-3 | line-3-0871-0768-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0868-0767-s000068 | forward | cold_reserve | 1 | pending |
| line-4 | line-4-0588-0607-s000000 | forward | revenue | 5 | pending |
| line-4 | line-4-0473-0587-s003006 | forward | revenue | 5 | pending |
| line-4 | line-4-0473-0587-s003006 | reverse | revenue | 4 | pending |
| line-4 | line-4-0487-0486-s006506 | reverse | revenue | 4 | pending |
| line-4 | line-4-0473-0587-s003006 | reverse | spare | 1 | pending |
| line-4 | line-4-0487-0486-s006506 | reverse | cold_reserve | 1 | pending |
| line-5 | line-5-0621-0715-s000000 | forward | revenue | 7 | pending |
| line-5 | line-5-0562-0863-s004781 | reverse | revenue | 7 | pending |
| line-5 | line-5-0621-0715-s000000 | forward | spare | 1 | pending |
| line-5 | line-5-0562-0863-s004781 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**128 trainsets exceed the reference platform envelope**, requiring **7,616.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0505-0384-s010214 | 12 | 2 | 10 | 595.0 |
| line-1-0512-0459-s008639 | 13 | 4 | 9 | 535.5 |
| line-1-0566-0133-s016925 | 6 | 2 | 4 | 238.0 |
| line-1-0588-0607-s004278 | 14 | 4 | 10 | 595.0 |
| line-1-0694-0708-s000000 | 7 | 2 | 5 | 297.5 |
| line-2-0302-0278-s000000 | 6 | 2 | 4 | 238.0 |
| line-2-0512-0459-s006238 | 12 | 4 | 8 | 476.0 |
| line-2-0567-0507-s007888 | 12 | 2 | 10 | 595.0 |
| line-2-0685-0609-s011386 | 12 | 2 | 10 | 595.0 |
| line-2-0868-0767-s016824 | 12 | 4 | 8 | 476.0 |
| line-2-0938-0810-s018943 | 6 | 2 | 4 | 238.0 |
| line-3-0383-0664-s010622 | 4 | 2 | 2 | 119.0 |
| line-3-0472-0683-s008684 | 8 | 2 | 6 | 357.0 |
| line-3-0621-0715-s005439 | 8 | 4 | 4 | 238.0 |
| line-3-0868-0767-s000068 | 9 | 4 | 5 | 297.5 |
| line-3-0871-0768-s000000 | 5 | 2 | 3 | 178.5 |
| line-4-0473-0587-s003006 | 10 | 2 | 8 | 476.0 |
| line-4-0487-0486-s006506 | 5 | 2 | 3 | 178.5 |
| line-4-0588-0607-s000000 | 5 | 2 | 3 | 178.5 |
| line-5-0562-0863-s004781 | 8 | 2 | 6 | 357.0 |
| line-5-0621-0715-s000000 | 8 | 2 | 6 | 357.0 |

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
