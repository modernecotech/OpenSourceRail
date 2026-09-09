# Station and depot overnight allocation

Plan: **32 trainsets at stations + 44 at depots = 76 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at declared depots.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot station | Stabling positions required | Usable slot length m | Workshop bays |
|---|---:|---:|---:|
| line-2-0689-0283-s015065 | 44 | 2,156.0 | 12 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0341-0217-s010401 | station | reverse | revenue | 2 |
| line-1 | line-1-0372-0388-s005569 | station | forward | revenue | 1 |
| line-1 | line-1-0372-0388-s005569 | station | reverse | revenue | 1 |
| line-1 | line-1-0391-0320-s007632 | station | forward | revenue | 1 |
| line-1 | line-1-0391-0320-s007632 | station | reverse | revenue | 1 |
| line-1 | line-1-0452-0462-s003017 | station | forward | revenue | 1 |
| line-1 | line-1-0452-0462-s003017 | station | reverse | revenue | 1 |
| line-1 | line-1-0476-0588-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0096-0563-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0204-0460-s003013 | station | forward | revenue | 1 |
| line-2 | line-2-0204-0460-s003013 | station | reverse | revenue | 1 |
| line-2 | line-2-0297-0436-s005072 | station | forward | revenue | 1 |
| line-2 | line-2-0297-0436-s005072 | station | reverse | revenue | 1 |
| line-2 | line-2-0372-0388-s007148 | station | forward | revenue | 1 |
| line-2 | line-2-0372-0388-s007148 | station | reverse | revenue | 1 |
| line-2 | line-2-0445-0380-s009033 | station | forward | revenue | 1 |
| line-2 | line-2-0445-0380-s009033 | station | reverse | revenue | 1 |
| line-2 | line-2-0689-0283-s015065 | station | reverse | revenue | 2 |
| line-3 | line-3-0218-0436-s011214 | station | reverse | revenue | 2 |
| line-3 | line-3-0296-0406-s009330 | station | forward | revenue | 1 |
| line-3 | line-3-0296-0406-s009330 | station | reverse | revenue | 1 |
| line-3 | line-3-0372-0388-s007462 | station | forward | revenue | 1 |
| line-3 | line-3-0372-0388-s007462 | station | reverse | revenue | 1 |
| line-3 | line-3-0416-0275-s004310 | station | forward | revenue | 1 |
| line-3 | line-3-0416-0275-s004310 | station | reverse | revenue | 1 |
| line-3 | line-3-0525-0111-s000000 | station | forward | revenue | 2 |
| line-1 | line-2-0689-0283-s015065 | depot | — | revenue | 9 |
| line-1 | line-2-0689-0283-s015065 | depot | — | spare | 1 |
| line-1 | line-2-0689-0283-s015065 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0689-0283-s015065 | depot | — | revenue | 15 |
| line-2 | line-2-0689-0283-s015065 | depot | — | spare | 2 |
| line-2 | line-2-0689-0283-s015065 | depot | — | cold_reserve | 1 |
| line-3 | line-2-0689-0283-s015065 | depot | — | revenue | 12 |
| line-3 | line-2-0689-0283-s015065 | depot | — | spare | 2 |
| line-3 | line-2-0689-0283-s015065 | depot | — | cold_reserve | 1 |

Interline access to the assigned depot must be detailed for: line-1 (11 trains), line-3 (15 trains).

Native hybrid candidate unavailable: interline depot access is absent from the native track graph.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **76 trainsets at 16 stations**; largest initial station queue **6**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **68 revenue, 5 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **32 positions**; **44 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **15 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0476-0588-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0452-0462-s003017 | forward | revenue | 3 | pending |
| line-1 | line-1-0452-0462-s003017 | reverse | revenue | 3 | pending |
| line-1 | line-1-0372-0388-s005569 | forward | revenue | 2 | pending |
| line-1 | line-1-0372-0388-s005569 | reverse | revenue | 2 | pending |
| line-1 | line-1-0391-0320-s007632 | forward | revenue | 2 | pending |
| line-1 | line-1-0391-0320-s007632 | reverse | revenue | 2 | pending |
| line-1 | line-1-0341-0217-s010401 | reverse | revenue | 2 | pending |
| line-1 | line-1-0372-0388-s005569 | forward | spare | 1 | pending |
| line-1 | line-1-0372-0388-s005569 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0096-0563-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0204-0460-s003013 | forward | revenue | 3 | pending |
| line-2 | line-2-0204-0460-s003013 | reverse | revenue | 3 | pending |
| line-2 | line-2-0297-0436-s005072 | forward | revenue | 3 | pending |
| line-2 | line-2-0297-0436-s005072 | reverse | revenue | 3 | pending |
| line-2 | line-2-0372-0388-s007148 | forward | revenue | 3 | pending |
| line-2 | line-2-0372-0388-s007148 | reverse | revenue | 3 | pending |
| line-2 | line-2-0445-0380-s009033 | forward | revenue | 2 | pending |
| line-2 | line-2-0445-0380-s009033 | reverse | revenue | 2 | pending |
| line-2 | line-2-0689-0283-s015065 | reverse | revenue | 2 | pending |
| line-2 | line-2-0445-0380-s009033 | forward | spare | 1 | pending |
| line-2 | line-2-0445-0380-s009033 | reverse | spare | 1 | pending |
| line-2 | line-2-0689-0283-s015065 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0525-0111-s000000 | forward | revenue | 3 | pending |
| line-3 | line-3-0416-0275-s004310 | forward | revenue | 3 | pending |
| line-3 | line-3-0416-0275-s004310 | reverse | revenue | 3 | pending |
| line-3 | line-3-0372-0388-s007462 | forward | revenue | 3 | pending |
| line-3 | line-3-0372-0388-s007462 | reverse | revenue | 3 | pending |
| line-3 | line-3-0296-0406-s009330 | forward | revenue | 3 | pending |
| line-3 | line-3-0296-0406-s009330 | reverse | revenue | 2 | pending |
| line-3 | line-3-0218-0436-s011214 | reverse | revenue | 2 | pending |
| line-3 | line-3-0296-0406-s009330 | reverse | spare | 1 | pending |
| line-3 | line-3-0218-0436-s011214 | reverse | spare | 1 | pending |
| line-3 | line-3-0525-0111-s000000 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**32 trainsets exceed the reference platform envelope**, requiring **1,568.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0341-0217-s010401 | 2 | 2 | 0 | 0.0 |
| line-1-0372-0388-s005569 | 6 | 4 | 2 | 98.0 |
| line-1-0391-0320-s007632 | 4 | 2 | 2 | 98.0 |
| line-1-0452-0462-s003017 | 6 | 2 | 4 | 196.0 |
| line-1-0476-0588-s000000 | 3 | 2 | 1 | 49.0 |
| line-2-0096-0563-s000000 | 3 | 2 | 1 | 49.0 |
| line-2-0204-0460-s003013 | 6 | 4 | 2 | 98.0 |
| line-2-0297-0436-s005072 | 6 | 4 | 2 | 98.0 |
| line-2-0372-0388-s007148 | 6 | 4 | 2 | 98.0 |
| line-2-0445-0380-s009033 | 6 | 2 | 4 | 196.0 |
| line-2-0689-0283-s015065 | 3 | 2 | 1 | 49.0 |
| line-3-0218-0436-s011214 | 3 | 2 | 1 | 49.0 |
| line-3-0296-0406-s009330 | 6 | 4 | 2 | 98.0 |
| line-3-0372-0388-s007462 | 6 | 4 | 2 | 98.0 |
| line-3-0416-0275-s004310 | 6 | 2 | 4 | 196.0 |
| line-3-0525-0111-s000000 | 4 | 2 | 2 | 98.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Kenya/Nyeri/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
