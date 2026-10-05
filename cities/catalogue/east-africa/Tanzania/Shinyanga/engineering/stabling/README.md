# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **18 trainsets at stations + 42 at depots = 60 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0494-0328-s013755 | line-1 | declared-depot | 21 | 1,029.0 | 4 |
| line-2-0254-0114-s000000 | line-2 | declared-depot | 10 | 490.0 | 3 |
| line-3-0422-0428-s000000 | line-3 | declared-depot | 11 | 539.0 | 3 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0031-0708-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0231-0480-s007014 | station | forward | revenue | 1 |
| line-1 | line-1-0231-0480-s007014 | station | reverse | revenue | 1 |
| line-1 | line-1-0389-0388-s011065 | station | forward | revenue | 1 |
| line-1 | line-1-0389-0388-s011065 | station | reverse | revenue | 1 |
| line-1 | line-1-0494-0328-s013755 | station | reverse | revenue | 2 |
| line-2 | line-2-0254-0114-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0397-0299-s005330 | station | forward | revenue | 1 |
| line-2 | line-2-0397-0299-s005330 | station | reverse | revenue | 1 |
| line-2 | line-2-0468-0382-s007836 | station | reverse | revenue | 2 |
| line-3 | line-3-0422-0428-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0661-0272-s006715 | station | reverse | revenue | 2 |
| line-1 | line-1-0494-0328-s013755 | depot | — | revenue | 18 |
| line-1 | line-1-0494-0328-s013755 | depot | — | spare | 2 |
| line-1 | line-1-0494-0328-s013755 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0254-0114-s000000 | depot | — | revenue | 8 |
| line-2 | line-2-0254-0114-s000000 | depot | — | spare | 1 |
| line-2 | line-2-0254-0114-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0422-0428-s000000 | depot | — | revenue | 9 |
| line-3 | line-3-0422-0428-s000000 | depot | — | spare | 1 |
| line-3 | line-3-0422-0428-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/shinyanga-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **60 trainsets at 9 stations**; largest initial station queue **10**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **53 revenue, 4 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **18 positions**; **42 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **9 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0031-0708-s000000 | forward | revenue | 5 | pending |
| line-1 | line-1-0231-0480-s007014 | forward | revenue | 5 | pending |
| line-1 | line-1-0231-0480-s007014 | reverse | revenue | 4 | pending |
| line-1 | line-1-0389-0388-s011065 | forward | revenue | 4 | pending |
| line-1 | line-1-0389-0388-s011065 | reverse | revenue | 4 | pending |
| line-1 | line-1-0494-0328-s013755 | reverse | revenue | 4 | pending |
| line-1 | line-1-0231-0480-s007014 | reverse | spare | 1 | pending |
| line-1 | line-1-0389-0388-s011065 | forward | spare | 1 | pending |
| line-1 | line-1-0389-0388-s011065 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0254-0114-s000000 | forward | revenue | 4 | pending |
| line-2 | line-2-0397-0299-s005330 | forward | revenue | 4 | pending |
| line-2 | line-2-0397-0299-s005330 | reverse | revenue | 3 | pending |
| line-2 | line-2-0468-0382-s007836 | reverse | revenue | 3 | pending |
| line-2 | line-2-0397-0299-s005330 | reverse | spare | 1 | pending |
| line-2 | line-2-0468-0382-s007836 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0422-0428-s000000 | forward | revenue | 7 | pending |
| line-3 | line-3-0661-0272-s006715 | reverse | revenue | 6 | pending |
| line-3 | line-3-0661-0272-s006715 | reverse | spare | 1 | pending |
| line-3 | line-3-0422-0428-s000000 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**42 trainsets exceed the reference platform envelope**, requiring **2,058.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0031-0708-s000000 | 5 | 2 | 3 | 147.0 |
| line-1-0231-0480-s007014 | 10 | 2 | 8 | 392.0 |
| line-1-0389-0388-s011065 | 10 | 2 | 8 | 392.0 |
| line-1-0494-0328-s013755 | 4 | 2 | 2 | 98.0 |
| line-2-0254-0114-s000000 | 4 | 2 | 2 | 98.0 |
| line-2-0397-0299-s005330 | 8 | 2 | 6 | 294.0 |
| line-2-0468-0382-s007836 | 4 | 2 | 2 | 98.0 |
| line-3-0422-0428-s000000 | 8 | 2 | 6 | 294.0 |
| line-3-0661-0272-s006715 | 7 | 2 | 5 | 245.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Tanzania/Shinyanga/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
