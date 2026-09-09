# Station and depot overnight allocation

Plan: **34 trainsets at stations + 88 at depots = 122 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at declared depots.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot station | Stabling positions required | Usable slot length m | Workshop bays |
|---|---:|---:|---:|
| line-2-0938-0810-s022386 | 88 | 5,236.0 | 19 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0505-0387-s010210 | station | forward | revenue | 1 |
| line-1 | line-1-0505-0387-s010210 | station | reverse | revenue | 1 |
| line-1 | line-1-0521-0478-s008145 | station | forward | revenue | 1 |
| line-1 | line-1-0521-0478-s008145 | station | reverse | revenue | 1 |
| line-1 | line-1-0551-0542-s006084 | station | forward | revenue | 1 |
| line-1 | line-1-0551-0542-s006084 | station | reverse | revenue | 1 |
| line-1 | line-1-0566-0133-s016982 | station | reverse | revenue | 2 |
| line-1 | line-1-0624-0618-s003014 | station | forward | revenue | 1 |
| line-1 | line-1-0624-0618-s003014 | station | reverse | revenue | 1 |
| line-1 | line-1-0694-0708-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0302-0278-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0436-0480-s005162 | station | forward | revenue | 1 |
| line-2 | line-2-0436-0480-s005162 | station | reverse | revenue | 1 |
| line-2 | line-2-0510-0581-s008166 | station | forward | revenue | 1 |
| line-2 | line-2-0510-0581-s008166 | station | reverse | revenue | 1 |
| line-2 | line-2-0551-0542-s010016 | station | forward | revenue | 1 |
| line-2 | line-2-0551-0542-s010016 | station | reverse | revenue | 1 |
| line-2 | line-2-0631-0561-s012785 | station | forward | revenue | 1 |
| line-2 | line-2-0631-0561-s012785 | station | reverse | revenue | 1 |
| line-2 | line-2-0702-0663-s015881 | station | forward | revenue | 1 |
| line-2 | line-2-0702-0663-s015881 | station | reverse | revenue | 1 |
| line-2 | line-2-0938-0810-s022386 | station | reverse | revenue | 2 |
| line-3 | line-3-0383-0664-s012312 | station | reverse | revenue | 2 |
| line-3 | line-3-0498-0671-s009954 | station | forward | revenue | 1 |
| line-3 | line-3-0498-0671-s009954 | station | reverse | revenue | 1 |
| line-3 | line-3-0575-0754-s006948 | station | forward | revenue | 1 |
| line-3 | line-3-0575-0754-s006948 | station | reverse | revenue | 1 |
| line-3 | line-3-0871-0768-s000000 | station | forward | revenue | 2 |
| line-1 | line-2-0938-0810-s022386 | depot | — | revenue | 24 |
| line-1 | line-2-0938-0810-s022386 | depot | — | spare | 3 |
| line-1 | line-2-0938-0810-s022386 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0938-0810-s022386 | depot | — | revenue | 33 |
| line-2 | line-2-0938-0810-s022386 | depot | — | spare | 4 |
| line-2 | line-2-0938-0810-s022386 | depot | — | cold_reserve | 1 |
| line-3 | line-2-0938-0810-s022386 | depot | — | revenue | 19 |
| line-3 | line-2-0938-0810-s022386 | depot | — | spare | 2 |
| line-3 | line-2-0938-0810-s022386 | depot | — | cold_reserve | 1 |

Interline access to the assigned depot must be detailed for: line-1 (28 trains), line-3 (22 trains).

## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **122 trainsets at 17 stations**; largest initial station queue **10**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **110 revenue, 9 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **34 positions**; **88 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **17 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0694-0708-s000000 | forward | revenue | 4 | pending |
| line-1 | line-1-0624-0618-s003014 | forward | revenue | 4 | pending |
| line-1 | line-1-0624-0618-s003014 | reverse | revenue | 4 | pending |
| line-1 | line-1-0551-0542-s006084 | forward | revenue | 4 | pending |
| line-1 | line-1-0551-0542-s006084 | reverse | revenue | 4 | pending |
| line-1 | line-1-0521-0478-s008145 | forward | revenue | 4 | pending |
| line-1 | line-1-0521-0478-s008145 | reverse | revenue | 3 | pending |
| line-1 | line-1-0505-0387-s010210 | forward | revenue | 3 | pending |
| line-1 | line-1-0505-0387-s010210 | reverse | revenue | 3 | pending |
| line-1 | line-1-0566-0133-s016982 | reverse | revenue | 3 | pending |
| line-1 | line-1-0521-0478-s008145 | reverse | spare | 1 | pending |
| line-1 | line-1-0505-0387-s010210 | forward | spare | 1 | pending |
| line-1 | line-1-0505-0387-s010210 | reverse | spare | 1 | pending |
| line-1 | line-1-0566-0133-s016982 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0302-0278-s000000 | forward | revenue | 4 | pending |
| line-2 | line-2-0436-0480-s005162 | forward | revenue | 4 | pending |
| line-2 | line-2-0436-0480-s005162 | reverse | revenue | 4 | pending |
| line-2 | line-2-0510-0581-s008166 | forward | revenue | 4 | pending |
| line-2 | line-2-0510-0581-s008166 | reverse | revenue | 4 | pending |
| line-2 | line-2-0551-0542-s010016 | forward | revenue | 4 | pending |
| line-2 | line-2-0551-0542-s010016 | reverse | revenue | 4 | pending |
| line-2 | line-2-0631-0561-s012785 | forward | revenue | 4 | pending |
| line-2 | line-2-0631-0561-s012785 | reverse | revenue | 4 | pending |
| line-2 | line-2-0702-0663-s015881 | forward | revenue | 4 | pending |
| line-2 | line-2-0702-0663-s015881 | reverse | revenue | 4 | pending |
| line-2 | line-2-0938-0810-s022386 | reverse | revenue | 3 | pending |
| line-2 | line-2-0938-0810-s022386 | reverse | spare | 1 | pending |
| line-2 | line-2-0302-0278-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0436-0480-s005162 | forward | spare | 1 | pending |
| line-2 | line-2-0436-0480-s005162 | reverse | spare | 1 | pending |
| line-2 | line-2-0510-0581-s008166 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0871-0768-s000000 | forward | revenue | 5 | pending |
| line-3 | line-3-0575-0754-s006948 | forward | revenue | 5 | pending |
| line-3 | line-3-0575-0754-s006948 | reverse | revenue | 5 | pending |
| line-3 | line-3-0498-0671-s009954 | forward | revenue | 4 | pending |
| line-3 | line-3-0498-0671-s009954 | reverse | revenue | 4 | pending |
| line-3 | line-3-0383-0664-s012312 | reverse | revenue | 4 | pending |
| line-3 | line-3-0498-0671-s009954 | forward | spare | 1 | pending |
| line-3 | line-3-0498-0671-s009954 | reverse | spare | 1 | pending |
| line-3 | line-3-0383-0664-s012312 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**84 trainsets exceed the reference platform envelope**, requiring **4,998.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0505-0387-s010210 | 8 | 2 | 6 | 357.0 |
| line-1-0521-0478-s008145 | 8 | 2 | 6 | 357.0 |
| line-1-0551-0542-s006084 | 8 | 4 | 4 | 238.0 |
| line-1-0566-0133-s016982 | 4 | 2 | 2 | 119.0 |
| line-1-0624-0618-s003014 | 8 | 2 | 6 | 357.0 |
| line-1-0694-0708-s000000 | 4 | 2 | 2 | 119.0 |
| line-2-0302-0278-s000000 | 5 | 2 | 3 | 178.5 |
| line-2-0436-0480-s005162 | 10 | 2 | 8 | 476.0 |
| line-2-0510-0581-s008166 | 9 | 2 | 7 | 416.5 |
| line-2-0551-0542-s010016 | 8 | 4 | 4 | 238.0 |
| line-2-0631-0561-s012785 | 8 | 2 | 6 | 357.0 |
| line-2-0702-0663-s015881 | 8 | 2 | 6 | 357.0 |
| line-2-0938-0810-s022386 | 4 | 2 | 2 | 119.0 |
| line-3-0383-0664-s012312 | 5 | 2 | 3 | 178.5 |
| line-3-0498-0671-s009954 | 10 | 2 | 8 | 476.0 |
| line-3-0575-0754-s006948 | 10 | 2 | 8 | 476.0 |
| line-3-0871-0768-s000000 | 5 | 2 | 3 | 178.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Mozambique/Nampula/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
