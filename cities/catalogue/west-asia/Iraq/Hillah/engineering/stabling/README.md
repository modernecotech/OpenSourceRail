# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **38 trainsets at stations + 125 at depots = 163 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0278-0667-s000000 | line-1 | declared-depot | 42 | 2,499.0 | 8 |
| line-2-0032-0601-s000000 | line-2 | declared-depot | 41 | 2,439.5 | 8 |
| line-3-0404-0807-s017723 | line-3 | declared-depot | 42 | 2,499.0 | 8 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0278-0667-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0412-0630-s003010 | station | forward | revenue | 1 |
| line-1 | line-1-0412-0630-s003010 | station | reverse | revenue | 1 |
| line-1 | line-1-0486-0609-s004664 | station | forward | revenue | 1 |
| line-1 | line-1-0486-0609-s004664 | station | reverse | revenue | 1 |
| line-1 | line-1-0557-0589-s006261 | station | forward | revenue | 1 |
| line-1 | line-1-0557-0589-s006261 | station | reverse | revenue | 1 |
| line-1 | line-1-0679-0555-s009018 | station | forward | revenue | 1 |
| line-1 | line-1-0679-0555-s009018 | station | reverse | revenue | 1 |
| line-1 | line-1-0968-0482-s015373 | station | forward | revenue | 1 |
| line-1 | line-1-0968-0482-s015373 | station | reverse | revenue | 1 |
| line-1 | line-1-1072-0471-s017505 | station | reverse | revenue | 2 |
| line-2 | line-2-0032-0601-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0269-0625-s007008 | station | forward | revenue | 1 |
| line-2 | line-2-0269-0625-s007008 | station | reverse | revenue | 1 |
| line-2 | line-2-0394-0570-s010022 | station | forward | revenue | 1 |
| line-2 | line-2-0394-0570-s010022 | station | reverse | revenue | 1 |
| line-2 | line-2-0527-0512-s013221 | station | forward | revenue | 1 |
| line-2 | line-2-0527-0512-s013221 | station | reverse | revenue | 1 |
| line-2 | line-2-0607-0477-s015135 | station | forward | revenue | 1 |
| line-2 | line-2-0607-0477-s015135 | station | reverse | revenue | 1 |
| line-2 | line-2-0687-0442-s017060 | station | reverse | revenue | 2 |
| line-3 | line-3-0404-0807-s017723 | station | reverse | revenue | 2 |
| line-3 | line-3-0445-0708-s015309 | station | forward | revenue | 1 |
| line-3 | line-3-0445-0708-s015309 | station | reverse | revenue | 1 |
| line-3 | line-3-0486-0609-s012908 | station | forward | revenue | 1 |
| line-3 | line-3-0486-0609-s012908 | station | reverse | revenue | 1 |
| line-3 | line-3-0527-0512-s010628 | station | forward | revenue | 1 |
| line-3 | line-3-0527-0512-s010628 | station | reverse | revenue | 1 |
| line-3 | line-3-0590-0360-s007019 | station | forward | revenue | 1 |
| line-3 | line-3-0590-0360-s007019 | station | reverse | revenue | 1 |
| line-3 | line-3-0598-0069-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0278-0667-s000000 | depot | — | revenue | 36 |
| line-1 | line-1-0278-0667-s000000 | depot | — | spare | 5 |
| line-1 | line-1-0278-0667-s000000 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0032-0601-s000000 | depot | — | revenue | 36 |
| line-2 | line-2-0032-0601-s000000 | depot | — | spare | 4 |
| line-2 | line-2-0032-0601-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0404-0807-s017723 | depot | — | revenue | 37 |
| line-3 | line-3-0404-0807-s017723 | depot | — | spare | 4 |
| line-3 | line-3-0404-0807-s017723 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/hillah-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **163 trainsets at 19 stations**; largest initial station queue **12**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **147 revenue, 13 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **38 positions**; **125 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **19 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0278-0667-s000000 | forward | revenue | 5 | pending |
| line-1 | line-1-0412-0630-s003010 | forward | revenue | 5 | pending |
| line-1 | line-1-0412-0630-s003010 | reverse | revenue | 4 | pending |
| line-1 | line-1-0486-0609-s004664 | forward | revenue | 4 | pending |
| line-1 | line-1-0486-0609-s004664 | reverse | revenue | 4 | pending |
| line-1 | line-1-0557-0589-s006261 | forward | revenue | 4 | pending |
| line-1 | line-1-0557-0589-s006261 | reverse | revenue | 4 | pending |
| line-1 | line-1-0679-0555-s009018 | forward | revenue | 4 | pending |
| line-1 | line-1-0679-0555-s009018 | reverse | revenue | 4 | pending |
| line-1 | line-1-0968-0482-s015373 | forward | revenue | 4 | pending |
| line-1 | line-1-0968-0482-s015373 | reverse | revenue | 4 | pending |
| line-1 | line-1-1072-0471-s017505 | reverse | revenue | 4 | pending |
| line-1 | line-1-0412-0630-s003010 | reverse | spare | 1 | pending |
| line-1 | line-1-0486-0609-s004664 | forward | spare | 1 | pending |
| line-1 | line-1-0486-0609-s004664 | reverse | spare | 1 | pending |
| line-1 | line-1-0557-0589-s006261 | forward | spare | 1 | pending |
| line-1 | line-1-0557-0589-s006261 | reverse | spare | 1 | pending |
| line-1 | line-1-0679-0555-s009018 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0032-0601-s000000 | forward | revenue | 5 | pending |
| line-2 | line-2-0269-0625-s007008 | forward | revenue | 5 | pending |
| line-2 | line-2-0269-0625-s007008 | reverse | revenue | 5 | pending |
| line-2 | line-2-0394-0570-s010022 | forward | revenue | 5 | pending |
| line-2 | line-2-0394-0570-s010022 | reverse | revenue | 5 | pending |
| line-2 | line-2-0527-0512-s013221 | forward | revenue | 5 | pending |
| line-2 | line-2-0527-0512-s013221 | reverse | revenue | 5 | pending |
| line-2 | line-2-0607-0477-s015135 | forward | revenue | 5 | pending |
| line-2 | line-2-0607-0477-s015135 | reverse | revenue | 4 | pending |
| line-2 | line-2-0687-0442-s017060 | reverse | revenue | 4 | pending |
| line-2 | line-2-0607-0477-s015135 | reverse | spare | 1 | pending |
| line-2 | line-2-0687-0442-s017060 | reverse | spare | 1 | pending |
| line-2 | line-2-0032-0601-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0269-0625-s007008 | forward | spare | 1 | pending |
| line-2 | line-2-0269-0625-s007008 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0598-0069-s000000 | forward | revenue | 5 | pending |
| line-3 | line-3-0590-0360-s007019 | forward | revenue | 5 | pending |
| line-3 | line-3-0590-0360-s007019 | reverse | revenue | 5 | pending |
| line-3 | line-3-0527-0512-s010628 | forward | revenue | 5 | pending |
| line-3 | line-3-0527-0512-s010628 | reverse | revenue | 5 | pending |
| line-3 | line-3-0486-0609-s012908 | forward | revenue | 5 | pending |
| line-3 | line-3-0486-0609-s012908 | reverse | revenue | 5 | pending |
| line-3 | line-3-0445-0708-s015309 | forward | revenue | 5 | pending |
| line-3 | line-3-0445-0708-s015309 | reverse | revenue | 5 | pending |
| line-3 | line-3-0404-0807-s017723 | reverse | revenue | 4 | pending |
| line-3 | line-3-0404-0807-s017723 | reverse | spare | 1 | pending |
| line-3 | line-3-0598-0069-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0590-0360-s007019 | forward | spare | 1 | pending |
| line-3 | line-3-0590-0360-s007019 | reverse | spare | 1 | pending |
| line-3 | line-3-0527-0512-s010628 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**117 trainsets exceed the reference platform envelope**, requiring **6,961.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0278-0667-s000000 | 5 | 2 | 3 | 178.5 |
| line-1-0412-0630-s003010 | 10 | 2 | 8 | 476.0 |
| line-1-0486-0609-s004664 | 10 | 4 | 6 | 357.0 |
| line-1-0557-0589-s006261 | 10 | 2 | 8 | 476.0 |
| line-1-0679-0555-s009018 | 9 | 2 | 7 | 416.5 |
| line-1-0968-0482-s015373 | 8 | 2 | 6 | 357.0 |
| line-1-1072-0471-s017505 | 4 | 2 | 2 | 119.0 |
| line-2-0032-0601-s000000 | 6 | 2 | 4 | 238.0 |
| line-2-0269-0625-s007008 | 12 | 2 | 10 | 595.0 |
| line-2-0394-0570-s010022 | 10 | 2 | 8 | 476.0 |
| line-2-0527-0512-s013221 | 10 | 4 | 6 | 357.0 |
| line-2-0607-0477-s015135 | 10 | 2 | 8 | 476.0 |
| line-2-0687-0442-s017060 | 5 | 2 | 3 | 178.5 |
| line-3-0404-0807-s017723 | 5 | 2 | 3 | 178.5 |
| line-3-0445-0708-s015309 | 10 | 2 | 8 | 476.0 |
| line-3-0486-0609-s012908 | 10 | 4 | 6 | 357.0 |
| line-3-0527-0512-s010628 | 11 | 4 | 7 | 416.5 |
| line-3-0590-0360-s007019 | 12 | 2 | 10 | 595.0 |
| line-3-0598-0069-s000000 | 6 | 2 | 4 | 238.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Iraq/Hillah/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
