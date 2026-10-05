# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **32 trainsets at stations + 131 at depots = 163 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0279-0389-s000000 | line-1 | declared-depot | 33 | 1,963.5 | 6 |
| line-2-0445-0723-s000000 | line-2 | declared-depot | 35 | 2,082.5 | 7 |
| line-3-0761-0860-s023967 | line-3 | declared-depot | 63 | 3,748.5 | 11 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0279-0389-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0507-0464-s005216 | station | forward | revenue | 1 |
| line-1 | line-1-0507-0464-s005216 | station | reverse | revenue | 1 |
| line-1 | line-1-0639-0507-s008236 | station | forward | revenue | 1 |
| line-1 | line-1-0639-0507-s008236 | station | reverse | revenue | 1 |
| line-1 | line-1-0759-0547-s010979 | station | forward | revenue | 1 |
| line-1 | line-1-0759-0547-s010979 | station | reverse | revenue | 1 |
| line-1 | line-1-0879-0586-s013726 | station | reverse | revenue | 2 |
| line-2 | line-2-0445-0723-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0565-0659-s003024 | station | forward | revenue | 1 |
| line-2 | line-2-0565-0659-s003024 | station | reverse | revenue | 1 |
| line-2 | line-2-0685-0595-s006036 | station | forward | revenue | 1 |
| line-2 | line-2-0685-0595-s006036 | station | reverse | revenue | 1 |
| line-2 | line-2-0763-0554-s008018 | station | forward | revenue | 1 |
| line-2 | line-2-0763-0554-s008018 | station | reverse | revenue | 1 |
| line-2 | line-2-0841-0512-s010019 | station | forward | revenue | 1 |
| line-2 | line-2-0841-0512-s010019 | station | reverse | revenue | 1 |
| line-2 | line-2-1084-0450-s015347 | station | reverse | revenue | 2 |
| line-3 | line-3-0078-0053-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0412-0468-s012205 | station | forward | revenue | 1 |
| line-3 | line-3-0412-0468-s012205 | station | reverse | revenue | 1 |
| line-3 | line-3-0500-0567-s015184 | station | forward | revenue | 1 |
| line-3 | line-3-0500-0567-s015184 | station | reverse | revenue | 1 |
| line-3 | line-3-0590-0668-s018219 | station | forward | revenue | 1 |
| line-3 | line-3-0590-0668-s018219 | station | reverse | revenue | 1 |
| line-3 | line-3-0761-0860-s023967 | station | reverse | revenue | 2 |
| line-1 | line-1-0279-0389-s000000 | depot | — | revenue | 29 |
| line-1 | line-1-0279-0389-s000000 | depot | — | spare | 3 |
| line-1 | line-1-0279-0389-s000000 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0445-0723-s000000 | depot | — | revenue | 30 |
| line-2 | line-2-0445-0723-s000000 | depot | — | spare | 4 |
| line-2 | line-2-0445-0723-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0761-0860-s023967 | depot | — | revenue | 56 |
| line-3 | line-3-0761-0860-s023967 | depot | — | spare | 6 |
| line-3 | line-3-0761-0860-s023967 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/barisal-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **163 trainsets at 16 stations**; largest initial station queue **18**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **147 revenue, 13 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **32 positions**; **131 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **16 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0279-0389-s000000 | forward | revenue | 5 | pending |
| line-1 | line-1-0507-0464-s005216 | forward | revenue | 5 | pending |
| line-1 | line-1-0507-0464-s005216 | reverse | revenue | 5 | pending |
| line-1 | line-1-0639-0507-s008236 | forward | revenue | 5 | pending |
| line-1 | line-1-0639-0507-s008236 | reverse | revenue | 5 | pending |
| line-1 | line-1-0759-0547-s010979 | forward | revenue | 5 | pending |
| line-1 | line-1-0759-0547-s010979 | reverse | revenue | 5 | pending |
| line-1 | line-1-0879-0586-s013726 | reverse | revenue | 4 | pending |
| line-1 | line-1-0879-0586-s013726 | reverse | spare | 1 | pending |
| line-1 | line-1-0279-0389-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0507-0464-s005216 | forward | spare | 1 | pending |
| line-1 | line-1-0507-0464-s005216 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0445-0723-s000000 | forward | revenue | 5 | pending |
| line-2 | line-2-0565-0659-s003024 | forward | revenue | 5 | pending |
| line-2 | line-2-0565-0659-s003024 | reverse | revenue | 4 | pending |
| line-2 | line-2-0685-0595-s006036 | forward | revenue | 4 | pending |
| line-2 | line-2-0685-0595-s006036 | reverse | revenue | 4 | pending |
| line-2 | line-2-0763-0554-s008018 | forward | revenue | 4 | pending |
| line-2 | line-2-0763-0554-s008018 | reverse | revenue | 4 | pending |
| line-2 | line-2-0841-0512-s010019 | forward | revenue | 4 | pending |
| line-2 | line-2-0841-0512-s010019 | reverse | revenue | 4 | pending |
| line-2 | line-2-1084-0450-s015347 | reverse | revenue | 4 | pending |
| line-2 | line-2-0565-0659-s003024 | reverse | spare | 1 | pending |
| line-2 | line-2-0685-0595-s006036 | forward | spare | 1 | pending |
| line-2 | line-2-0685-0595-s006036 | reverse | spare | 1 | pending |
| line-2 | line-2-0763-0554-s008018 | forward | spare | 1 | pending |
| line-2 | line-2-0763-0554-s008018 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0078-0053-s000000 | forward | revenue | 9 | pending |
| line-3 | line-3-0412-0468-s012205 | forward | revenue | 9 | pending |
| line-3 | line-3-0412-0468-s012205 | reverse | revenue | 8 | pending |
| line-3 | line-3-0500-0567-s015184 | forward | revenue | 8 | pending |
| line-3 | line-3-0500-0567-s015184 | reverse | revenue | 8 | pending |
| line-3 | line-3-0590-0668-s018219 | forward | revenue | 8 | pending |
| line-3 | line-3-0590-0668-s018219 | reverse | revenue | 8 | pending |
| line-3 | line-3-0761-0860-s023967 | reverse | revenue | 8 | pending |
| line-3 | line-3-0412-0468-s012205 | reverse | spare | 1 | pending |
| line-3 | line-3-0500-0567-s015184 | forward | spare | 1 | pending |
| line-3 | line-3-0500-0567-s015184 | reverse | spare | 1 | pending |
| line-3 | line-3-0590-0668-s018219 | forward | spare | 1 | pending |
| line-3 | line-3-0590-0668-s018219 | reverse | spare | 1 | pending |
| line-3 | line-3-0761-0860-s023967 | reverse | spare | 1 | pending |
| line-3 | line-3-0078-0053-s000000 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**123 trainsets exceed the reference platform envelope**, requiring **7,318.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0279-0389-s000000 | 6 | 2 | 4 | 238.0 |
| line-1-0507-0464-s005216 | 12 | 2 | 10 | 595.0 |
| line-1-0639-0507-s008236 | 10 | 2 | 8 | 476.0 |
| line-1-0759-0547-s010979 | 10 | 4 | 6 | 357.0 |
| line-1-0879-0586-s013726 | 5 | 2 | 3 | 178.5 |
| line-2-0445-0723-s000000 | 5 | 2 | 3 | 178.5 |
| line-2-0565-0659-s003024 | 10 | 4 | 6 | 357.0 |
| line-2-0685-0595-s006036 | 10 | 2 | 8 | 476.0 |
| line-2-0763-0554-s008018 | 10 | 4 | 6 | 357.0 |
| line-2-0841-0512-s010019 | 8 | 2 | 6 | 357.0 |
| line-2-1084-0450-s015347 | 4 | 2 | 2 | 119.0 |
| line-3-0078-0053-s000000 | 10 | 2 | 8 | 476.0 |
| line-3-0412-0468-s012205 | 18 | 2 | 16 | 952.0 |
| line-3-0500-0567-s015184 | 18 | 2 | 16 | 952.0 |
| line-3-0590-0668-s018219 | 18 | 4 | 14 | 833.0 |
| line-3-0761-0860-s023967 | 9 | 2 | 7 | 416.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/south-asia/Bangladesh/Barisal/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
