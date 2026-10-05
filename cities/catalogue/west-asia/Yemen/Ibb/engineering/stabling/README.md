# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **28 trainsets at stations + 99 at depots = 127 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0398-0570-s000000 | line-1 | declared-depot | 26 | 1,547.0 | 5 |
| line-2-0113-0058-s017641 | line-2 | declared-depot | 46 | 2,737.0 | 8 |
| line-3-0903-0571-s000000 | line-3 | declared-depot | 27 | 1,606.5 | 6 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0398-0570-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0515-0504-s003004 | station | forward | revenue | 1 |
| line-1 | line-1-0515-0504-s003004 | station | reverse | revenue | 1 |
| line-1 | line-1-0627-0440-s005844 | station | forward | revenue | 1 |
| line-1 | line-1-0627-0440-s005844 | station | reverse | revenue | 1 |
| line-1 | line-1-0806-0339-s010413 | station | reverse | revenue | 2 |
| line-2 | line-2-0113-0058-s017641 | station | reverse | revenue | 2 |
| line-2 | line-2-0542-0387-s006036 | station | forward | revenue | 1 |
| line-2 | line-2-0542-0387-s006036 | station | reverse | revenue | 1 |
| line-2 | line-2-0627-0440-s003768 | station | forward | revenue | 1 |
| line-2 | line-2-0627-0440-s003768 | station | reverse | revenue | 1 |
| line-2 | line-2-0698-0486-s001885 | station | forward | revenue | 1 |
| line-2 | line-2-0698-0486-s001885 | station | reverse | revenue | 1 |
| line-2 | line-2-0772-0532-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0379-0667-s011322 | station | reverse | revenue | 2 |
| line-3 | line-3-0473-0649-s009281 | station | forward | revenue | 1 |
| line-3 | line-3-0473-0649-s009281 | station | reverse | revenue | 1 |
| line-3 | line-3-0567-0631-s007240 | station | forward | revenue | 1 |
| line-3 | line-3-0567-0631-s007240 | station | reverse | revenue | 1 |
| line-3 | line-3-0661-0613-s005211 | station | forward | revenue | 1 |
| line-3 | line-3-0661-0613-s005211 | station | reverse | revenue | 1 |
| line-3 | line-3-0903-0571-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0398-0570-s000000 | depot | — | revenue | 22 |
| line-1 | line-1-0398-0570-s000000 | depot | — | spare | 3 |
| line-1 | line-1-0398-0570-s000000 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0113-0058-s017641 | depot | — | revenue | 40 |
| line-2 | line-2-0113-0058-s017641 | depot | — | spare | 5 |
| line-2 | line-2-0113-0058-s017641 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0903-0571-s000000 | depot | — | revenue | 23 |
| line-3 | line-3-0903-0571-s000000 | depot | — | spare | 3 |
| line-3 | line-3-0903-0571-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/ibb-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **127 trainsets at 14 stations**; largest initial station queue **14**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **113 revenue, 11 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **28 positions**; **99 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **14 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0398-0570-s000000 | forward | revenue | 5 | pending |
| line-1 | line-1-0515-0504-s003004 | forward | revenue | 5 | pending |
| line-1 | line-1-0515-0504-s003004 | reverse | revenue | 5 | pending |
| line-1 | line-1-0627-0440-s005844 | forward | revenue | 5 | pending |
| line-1 | line-1-0627-0440-s005844 | reverse | revenue | 5 | pending |
| line-1 | line-1-0806-0339-s010413 | reverse | revenue | 5 | pending |
| line-1 | line-1-0398-0570-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0515-0504-s003004 | forward | spare | 1 | pending |
| line-1 | line-1-0515-0504-s003004 | reverse | spare | 1 | pending |
| line-1 | line-1-0627-0440-s005844 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0772-0532-s000000 | forward | revenue | 7 | pending |
| line-2 | line-2-0698-0486-s001885 | forward | revenue | 7 | pending |
| line-2 | line-2-0698-0486-s001885 | reverse | revenue | 6 | pending |
| line-2 | line-2-0627-0440-s003768 | forward | revenue | 6 | pending |
| line-2 | line-2-0627-0440-s003768 | reverse | revenue | 6 | pending |
| line-2 | line-2-0542-0387-s006036 | forward | revenue | 6 | pending |
| line-2 | line-2-0542-0387-s006036 | reverse | revenue | 6 | pending |
| line-2 | line-2-0113-0058-s017641 | reverse | revenue | 6 | pending |
| line-2 | line-2-0698-0486-s001885 | reverse | spare | 1 | pending |
| line-2 | line-2-0627-0440-s003768 | forward | spare | 1 | pending |
| line-2 | line-2-0627-0440-s003768 | reverse | spare | 1 | pending |
| line-2 | line-2-0542-0387-s006036 | forward | spare | 1 | pending |
| line-2 | line-2-0542-0387-s006036 | reverse | spare | 1 | pending |
| line-2 | line-2-0113-0058-s017641 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0903-0571-s000000 | forward | revenue | 5 | pending |
| line-3 | line-3-0661-0613-s005211 | forward | revenue | 4 | pending |
| line-3 | line-3-0661-0613-s005211 | reverse | revenue | 4 | pending |
| line-3 | line-3-0567-0631-s007240 | forward | revenue | 4 | pending |
| line-3 | line-3-0567-0631-s007240 | reverse | revenue | 4 | pending |
| line-3 | line-3-0473-0649-s009281 | forward | revenue | 4 | pending |
| line-3 | line-3-0473-0649-s009281 | reverse | revenue | 4 | pending |
| line-3 | line-3-0379-0667-s011322 | reverse | revenue | 4 | pending |
| line-3 | line-3-0661-0613-s005211 | forward | spare | 1 | pending |
| line-3 | line-3-0661-0613-s005211 | reverse | spare | 1 | pending |
| line-3 | line-3-0567-0631-s007240 | forward | spare | 1 | pending |
| line-3 | line-3-0567-0631-s007240 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**95 trainsets exceed the reference platform envelope**, requiring **5,652.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0398-0570-s000000 | 6 | 2 | 4 | 238.0 |
| line-1-0515-0504-s003004 | 12 | 2 | 10 | 595.0 |
| line-1-0627-0440-s005844 | 11 | 4 | 7 | 416.5 |
| line-1-0806-0339-s010413 | 5 | 2 | 3 | 178.5 |
| line-2-0113-0058-s017641 | 7 | 2 | 5 | 297.5 |
| line-2-0542-0387-s006036 | 14 | 2 | 12 | 714.0 |
| line-2-0627-0440-s003768 | 14 | 4 | 10 | 595.0 |
| line-2-0698-0486-s001885 | 14 | 2 | 12 | 714.0 |
| line-2-0772-0532-s000000 | 7 | 2 | 5 | 297.5 |
| line-3-0379-0667-s011322 | 4 | 2 | 2 | 119.0 |
| line-3-0473-0649-s009281 | 8 | 2 | 6 | 357.0 |
| line-3-0567-0631-s007240 | 10 | 2 | 8 | 476.0 |
| line-3-0661-0613-s005211 | 10 | 2 | 8 | 476.0 |
| line-3-0903-0571-s000000 | 5 | 2 | 3 | 178.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Yemen/Ibb/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
