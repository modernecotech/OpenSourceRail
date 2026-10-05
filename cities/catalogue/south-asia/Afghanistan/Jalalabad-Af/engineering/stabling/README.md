# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **28 trainsets at stations + 98 at depots = 126 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0798-0565-s000000 | line-1 | declared-depot | 19 | 1,130.5 | 4 |
| line-2-0286-0151-s020048 | line-2 | declared-depot | 51 | 3,034.5 | 9 |
| line-3-0320-0781-s000000 | line-3 | declared-depot | 28 | 1,666.0 | 6 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0399-0533-s008245 | station | reverse | revenue | 2 |
| line-1 | line-1-0555-0546-s005017 | station | forward | revenue | 1 |
| line-1 | line-1-0555-0546-s005017 | station | reverse | revenue | 1 |
| line-1 | line-1-0652-0553-s003019 | station | forward | revenue | 1 |
| line-1 | line-1-0652-0553-s003019 | station | reverse | revenue | 1 |
| line-1 | line-1-0798-0565-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0286-0151-s020048 | station | reverse | revenue | 2 |
| line-2 | line-2-0555-0481-s010172 | station | forward | revenue | 1 |
| line-2 | line-2-0555-0481-s010172 | station | reverse | revenue | 1 |
| line-2 | line-2-0622-0599-s007163 | station | forward | revenue | 1 |
| line-2 | line-2-0622-0599-s007163 | station | reverse | revenue | 1 |
| line-2 | line-2-0689-0716-s004151 | station | forward | revenue | 1 |
| line-2 | line-2-0689-0716-s004151 | station | reverse | revenue | 1 |
| line-2 | line-2-0782-0878-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0320-0781-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0495-0663-s004688 | station | forward | revenue | 1 |
| line-3 | line-3-0495-0663-s004688 | station | reverse | revenue | 1 |
| line-3 | line-3-0569-0613-s006712 | station | forward | revenue | 1 |
| line-3 | line-3-0569-0613-s006712 | station | reverse | revenue | 1 |
| line-3 | line-3-0667-0547-s009335 | station | forward | revenue | 1 |
| line-3 | line-3-0667-0547-s009335 | station | reverse | revenue | 1 |
| line-3 | line-3-0764-0482-s011943 | station | reverse | revenue | 2 |
| line-1 | line-1-0798-0565-s000000 | depot | — | revenue | 16 |
| line-1 | line-1-0798-0565-s000000 | depot | — | spare | 2 |
| line-1 | line-1-0798-0565-s000000 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0286-0151-s020048 | depot | — | revenue | 45 |
| line-2 | line-2-0286-0151-s020048 | depot | — | spare | 5 |
| line-2 | line-2-0286-0151-s020048 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0320-0781-s000000 | depot | — | revenue | 24 |
| line-3 | line-3-0320-0781-s000000 | depot | — | spare | 3 |
| line-3 | line-3-0320-0781-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/jalalabad-af-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **126 trainsets at 14 stations**; largest initial station queue **16**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **113 revenue, 10 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **28 positions**; **98 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **14 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0798-0565-s000000 | forward | revenue | 4 | pending |
| line-1 | line-1-0652-0553-s003019 | forward | revenue | 4 | pending |
| line-1 | line-1-0652-0553-s003019 | reverse | revenue | 4 | pending |
| line-1 | line-1-0555-0546-s005017 | forward | revenue | 4 | pending |
| line-1 | line-1-0555-0546-s005017 | reverse | revenue | 4 | pending |
| line-1 | line-1-0399-0533-s008245 | reverse | revenue | 4 | pending |
| line-1 | line-1-0798-0565-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0652-0553-s003019 | forward | spare | 1 | pending |
| line-1 | line-1-0652-0553-s003019 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0782-0878-s000000 | forward | revenue | 7 | pending |
| line-2 | line-2-0689-0716-s004151 | forward | revenue | 7 | pending |
| line-2 | line-2-0689-0716-s004151 | reverse | revenue | 7 | pending |
| line-2 | line-2-0622-0599-s007163 | forward | revenue | 7 | pending |
| line-2 | line-2-0622-0599-s007163 | reverse | revenue | 7 | pending |
| line-2 | line-2-0555-0481-s010172 | forward | revenue | 7 | pending |
| line-2 | line-2-0555-0481-s010172 | reverse | revenue | 7 | pending |
| line-2 | line-2-0286-0151-s020048 | reverse | revenue | 6 | pending |
| line-2 | line-2-0286-0151-s020048 | reverse | spare | 1 | pending |
| line-2 | line-2-0782-0878-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0689-0716-s004151 | forward | spare | 1 | pending |
| line-2 | line-2-0689-0716-s004151 | reverse | spare | 1 | pending |
| line-2 | line-2-0622-0599-s007163 | forward | spare | 1 | pending |
| line-2 | line-2-0622-0599-s007163 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0320-0781-s000000 | forward | revenue | 5 | pending |
| line-3 | line-3-0495-0663-s004688 | forward | revenue | 5 | pending |
| line-3 | line-3-0495-0663-s004688 | reverse | revenue | 4 | pending |
| line-3 | line-3-0569-0613-s006712 | forward | revenue | 4 | pending |
| line-3 | line-3-0569-0613-s006712 | reverse | revenue | 4 | pending |
| line-3 | line-3-0667-0547-s009335 | forward | revenue | 4 | pending |
| line-3 | line-3-0667-0547-s009335 | reverse | revenue | 4 | pending |
| line-3 | line-3-0764-0482-s011943 | reverse | revenue | 4 | pending |
| line-3 | line-3-0495-0663-s004688 | reverse | spare | 1 | pending |
| line-3 | line-3-0569-0613-s006712 | forward | spare | 1 | pending |
| line-3 | line-3-0569-0613-s006712 | reverse | spare | 1 | pending |
| line-3 | line-3-0667-0547-s009335 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**94 trainsets exceed the reference platform envelope**, requiring **5,593.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0399-0533-s008245 | 4 | 2 | 2 | 119.0 |
| line-1-0555-0546-s005017 | 8 | 2 | 6 | 357.0 |
| line-1-0652-0553-s003019 | 10 | 4 | 6 | 357.0 |
| line-1-0798-0565-s000000 | 5 | 2 | 3 | 178.5 |
| line-2-0286-0151-s020048 | 7 | 2 | 5 | 297.5 |
| line-2-0555-0481-s010172 | 14 | 2 | 12 | 714.0 |
| line-2-0622-0599-s007163 | 16 | 2 | 14 | 833.0 |
| line-2-0689-0716-s004151 | 16 | 2 | 14 | 833.0 |
| line-2-0782-0878-s000000 | 8 | 2 | 6 | 357.0 |
| line-3-0320-0781-s000000 | 5 | 2 | 3 | 178.5 |
| line-3-0495-0663-s004688 | 10 | 2 | 8 | 476.0 |
| line-3-0569-0613-s006712 | 10 | 2 | 8 | 476.0 |
| line-3-0667-0547-s009335 | 9 | 4 | 5 | 297.5 |
| line-3-0764-0482-s011943 | 4 | 2 | 2 | 119.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/south-asia/Afghanistan/Jalalabad-Af/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
