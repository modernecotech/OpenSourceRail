# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **48 trainsets at stations + 128 at depots = 176 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0623-0933-s000000 | line-1 | declared-depot | 42 | 2,499.0 | 9 |
| line-2-0846-0375-s020624 | line-2 | declared-depot | 49 | 2,915.5 | 9 |
| line-3-0463-0113-s000000 | line-3 | declared-depot | 37 | 2,201.5 | 8 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0496-0025-s019590 | station | reverse | revenue | 2 |
| line-1 | line-1-0500-0124-s017368 | station | forward | revenue | 1 |
| line-1 | line-1-0500-0124-s017368 | station | reverse | revenue | 1 |
| line-1 | line-1-0510-0224-s015182 | station | forward | revenue | 1 |
| line-1 | line-1-0510-0224-s015182 | station | reverse | revenue | 1 |
| line-1 | line-1-0526-0328-s012969 | station | forward | revenue | 1 |
| line-1 | line-1-0526-0328-s012969 | station | reverse | revenue | 1 |
| line-1 | line-1-0547-0470-s009955 | station | forward | revenue | 1 |
| line-1 | line-1-0547-0470-s009955 | station | reverse | revenue | 1 |
| line-1 | line-1-0559-0549-s008276 | station | forward | revenue | 1 |
| line-1 | line-1-0559-0549-s008276 | station | reverse | revenue | 1 |
| line-1 | line-1-0568-0612-s006941 | station | forward | revenue | 1 |
| line-1 | line-1-0568-0612-s006941 | station | reverse | revenue | 1 |
| line-1 | line-1-0589-0754-s003927 | station | forward | revenue | 1 |
| line-1 | line-1-0589-0754-s003927 | station | reverse | revenue | 1 |
| line-1 | line-1-0623-0933-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0024-0798-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0322-0692-s007014 | station | forward | revenue | 1 |
| line-2 | line-2-0322-0692-s007014 | station | reverse | revenue | 1 |
| line-2 | line-2-0462-0608-s010639 | station | forward | revenue | 1 |
| line-2 | line-2-0462-0608-s010639 | station | reverse | revenue | 1 |
| line-2 | line-2-0558-0549-s013141 | station | forward | revenue | 1 |
| line-2 | line-2-0558-0549-s013141 | station | reverse | revenue | 1 |
| line-2 | line-2-0671-0481-s016059 | station | forward | revenue | 1 |
| line-2 | line-2-0671-0481-s016059 | station | reverse | revenue | 1 |
| line-2 | line-2-0759-0428-s018340 | station | forward | revenue | 1 |
| line-2 | line-2-0759-0428-s018340 | station | reverse | revenue | 1 |
| line-2 | line-2-0846-0375-s020624 | station | reverse | revenue | 2 |
| line-3 | line-3-0450-0945-s016979 | station | reverse | revenue | 2 |
| line-3 | line-3-0453-0832-s014698 | station | forward | revenue | 1 |
| line-3 | line-3-0453-0832-s014698 | station | reverse | revenue | 1 |
| line-3 | line-3-0458-0720-s012417 | station | forward | revenue | 1 |
| line-3 | line-3-0458-0720-s012417 | station | reverse | revenue | 1 |
| line-3 | line-3-0462-0608-s010144 | station | forward | revenue | 1 |
| line-3 | line-3-0462-0608-s010144 | station | reverse | revenue | 1 |
| line-3 | line-3-0463-0113-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0467-0507-s008082 | station | forward | revenue | 1 |
| line-3 | line-3-0467-0507-s008082 | station | reverse | revenue | 1 |
| line-3 | line-3-0471-0406-s006029 | station | forward | revenue | 1 |
| line-3 | line-3-0471-0406-s006029 | station | reverse | revenue | 1 |
| line-3 | line-3-0478-0258-s003011 | station | forward | revenue | 1 |
| line-3 | line-3-0478-0258-s003011 | station | reverse | revenue | 1 |
| line-1 | line-1-0623-0933-s000000 | depot | — | revenue | 36 |
| line-1 | line-1-0623-0933-s000000 | depot | — | spare | 5 |
| line-1 | line-1-0623-0933-s000000 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0846-0375-s020624 | depot | — | revenue | 43 |
| line-2 | line-2-0846-0375-s020624 | depot | — | spare | 5 |
| line-2 | line-2-0846-0375-s020624 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0463-0113-s000000 | depot | — | revenue | 32 |
| line-3 | line-3-0463-0113-s000000 | depot | — | spare | 4 |
| line-3 | line-3-0463-0113-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/al-kharj-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **176 trainsets at 24 stations**; largest initial station queue **12**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **159 revenue, 14 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **48 positions**; **128 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **24 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0623-0933-s000000 | forward | revenue | 4 | pending |
| line-1 | line-1-0589-0754-s003927 | forward | revenue | 4 | pending |
| line-1 | line-1-0589-0754-s003927 | reverse | revenue | 4 | pending |
| line-1 | line-1-0568-0612-s006941 | forward | revenue | 4 | pending |
| line-1 | line-1-0568-0612-s006941 | reverse | revenue | 4 | pending |
| line-1 | line-1-0559-0549-s008276 | forward | revenue | 4 | pending |
| line-1 | line-1-0559-0549-s008276 | reverse | revenue | 3 | pending |
| line-1 | line-1-0547-0470-s009955 | forward | revenue | 3 | pending |
| line-1 | line-1-0547-0470-s009955 | reverse | revenue | 3 | pending |
| line-1 | line-1-0526-0328-s012969 | forward | revenue | 3 | pending |
| line-1 | line-1-0526-0328-s012969 | reverse | revenue | 3 | pending |
| line-1 | line-1-0510-0224-s015182 | forward | revenue | 3 | pending |
| line-1 | line-1-0510-0224-s015182 | reverse | revenue | 3 | pending |
| line-1 | line-1-0500-0124-s017368 | forward | revenue | 3 | pending |
| line-1 | line-1-0500-0124-s017368 | reverse | revenue | 3 | pending |
| line-1 | line-1-0496-0025-s019590 | reverse | revenue | 3 | pending |
| line-1 | line-1-0559-0549-s008276 | reverse | spare | 1 | pending |
| line-1 | line-1-0547-0470-s009955 | forward | spare | 1 | pending |
| line-1 | line-1-0547-0470-s009955 | reverse | spare | 1 | pending |
| line-1 | line-1-0526-0328-s012969 | forward | spare | 1 | pending |
| line-1 | line-1-0526-0328-s012969 | reverse | spare | 1 | pending |
| line-1 | line-1-0510-0224-s015182 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0024-0798-s000000 | forward | revenue | 5 | pending |
| line-2 | line-2-0322-0692-s007014 | forward | revenue | 5 | pending |
| line-2 | line-2-0322-0692-s007014 | reverse | revenue | 5 | pending |
| line-2 | line-2-0462-0608-s010639 | forward | revenue | 5 | pending |
| line-2 | line-2-0462-0608-s010639 | reverse | revenue | 5 | pending |
| line-2 | line-2-0558-0549-s013141 | forward | revenue | 5 | pending |
| line-2 | line-2-0558-0549-s013141 | reverse | revenue | 5 | pending |
| line-2 | line-2-0671-0481-s016059 | forward | revenue | 5 | pending |
| line-2 | line-2-0671-0481-s016059 | reverse | revenue | 5 | pending |
| line-2 | line-2-0759-0428-s018340 | forward | revenue | 4 | pending |
| line-2 | line-2-0759-0428-s018340 | reverse | revenue | 4 | pending |
| line-2 | line-2-0846-0375-s020624 | reverse | revenue | 4 | pending |
| line-2 | line-2-0759-0428-s018340 | forward | spare | 1 | pending |
| line-2 | line-2-0759-0428-s018340 | reverse | spare | 1 | pending |
| line-2 | line-2-0846-0375-s020624 | reverse | spare | 1 | pending |
| line-2 | line-2-0024-0798-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0322-0692-s007014 | forward | spare | 1 | pending |
| line-2 | line-2-0322-0692-s007014 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0463-0113-s000000 | forward | revenue | 4 | pending |
| line-3 | line-3-0478-0258-s003011 | forward | revenue | 4 | pending |
| line-3 | line-3-0478-0258-s003011 | reverse | revenue | 4 | pending |
| line-3 | line-3-0471-0406-s006029 | forward | revenue | 4 | pending |
| line-3 | line-3-0471-0406-s006029 | reverse | revenue | 4 | pending |
| line-3 | line-3-0467-0507-s008082 | forward | revenue | 4 | pending |
| line-3 | line-3-0467-0507-s008082 | reverse | revenue | 3 | pending |
| line-3 | line-3-0462-0608-s010144 | forward | revenue | 3 | pending |
| line-3 | line-3-0462-0608-s010144 | reverse | revenue | 3 | pending |
| line-3 | line-3-0458-0720-s012417 | forward | revenue | 3 | pending |
| line-3 | line-3-0458-0720-s012417 | reverse | revenue | 3 | pending |
| line-3 | line-3-0453-0832-s014698 | forward | revenue | 3 | pending |
| line-3 | line-3-0453-0832-s014698 | reverse | revenue | 3 | pending |
| line-3 | line-3-0450-0945-s016979 | reverse | revenue | 3 | pending |
| line-3 | line-3-0467-0507-s008082 | reverse | spare | 1 | pending |
| line-3 | line-3-0462-0608-s010144 | forward | spare | 1 | pending |
| line-3 | line-3-0462-0608-s010144 | reverse | spare | 1 | pending |
| line-3 | line-3-0458-0720-s012417 | forward | spare | 1 | pending |
| line-3 | line-3-0458-0720-s012417 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**120 trainsets exceed the reference platform envelope**, requiring **7,140.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0496-0025-s019590 | 3 | 2 | 1 | 59.5 |
| line-1-0500-0124-s017368 | 6 | 2 | 4 | 238.0 |
| line-1-0510-0224-s015182 | 7 | 2 | 5 | 297.5 |
| line-1-0526-0328-s012969 | 8 | 2 | 6 | 357.0 |
| line-1-0547-0470-s009955 | 8 | 2 | 6 | 357.0 |
| line-1-0559-0549-s008276 | 8 | 4 | 4 | 238.0 |
| line-1-0568-0612-s006941 | 8 | 2 | 6 | 357.0 |
| line-1-0589-0754-s003927 | 8 | 2 | 6 | 357.0 |
| line-1-0623-0933-s000000 | 4 | 2 | 2 | 119.0 |
| line-2-0024-0798-s000000 | 6 | 2 | 4 | 238.0 |
| line-2-0322-0692-s007014 | 12 | 2 | 10 | 595.0 |
| line-2-0462-0608-s010639 | 10 | 4 | 6 | 357.0 |
| line-2-0558-0549-s013141 | 10 | 4 | 6 | 357.0 |
| line-2-0671-0481-s016059 | 10 | 2 | 8 | 476.0 |
| line-2-0759-0428-s018340 | 10 | 2 | 8 | 476.0 |
| line-2-0846-0375-s020624 | 5 | 2 | 3 | 178.5 |
| line-3-0450-0945-s016979 | 3 | 2 | 1 | 59.5 |
| line-3-0453-0832-s014698 | 6 | 2 | 4 | 238.0 |
| line-3-0458-0720-s012417 | 8 | 2 | 6 | 357.0 |
| line-3-0462-0608-s010144 | 8 | 4 | 4 | 238.0 |
| line-3-0463-0113-s000000 | 4 | 2 | 2 | 119.0 |
| line-3-0467-0507-s008082 | 8 | 2 | 6 | 357.0 |
| line-3-0471-0406-s006029 | 8 | 2 | 6 | 357.0 |
| line-3-0478-0258-s003011 | 8 | 2 | 6 | 357.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Saudi Arabia/Al-Kharj/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
