# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **32 trainsets at stations + 109 at depots = 141 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0781-0662-s000000 | line-1 | declared-depot | 22 | 1,309.0 | 5 |
| line-2-0399-0719-s000000 | line-2 | declared-depot | 19 | 1,130.5 | 4 |
| line-3-1100-0131-s024858 | line-3 | declared-depot | 68 | 4,046.0 | 11 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0292-0628-s010085 | station | reverse | revenue | 2 |
| line-1 | line-1-0427-0637-s007299 | station | forward | revenue | 1 |
| line-1 | line-1-0427-0637-s007299 | station | reverse | revenue | 1 |
| line-1 | line-1-0528-0644-s005221 | station | forward | revenue | 1 |
| line-1 | line-1-0528-0644-s005221 | station | reverse | revenue | 1 |
| line-1 | line-1-0628-0651-s003163 | station | forward | revenue | 1 |
| line-1 | line-1-0628-0651-s003163 | station | reverse | revenue | 1 |
| line-1 | line-1-0781-0662-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0399-0719-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0427-0637-s001872 | station | forward | revenue | 1 |
| line-2 | line-2-0427-0637-s001872 | station | reverse | revenue | 1 |
| line-2 | line-2-0463-0533-s004297 | station | forward | revenue | 1 |
| line-2 | line-2-0463-0533-s004297 | station | reverse | revenue | 1 |
| line-2 | line-2-0499-0428-s006742 | station | forward | revenue | 1 |
| line-2 | line-2-0499-0428-s006742 | station | reverse | revenue | 1 |
| line-2 | line-2-0536-0322-s009169 | station | reverse | revenue | 2 |
| line-3 | line-3-0405-0945-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0581-0703-s007016 | station | forward | revenue | 1 |
| line-3 | line-3-0581-0703-s007016 | station | reverse | revenue | 1 |
| line-3 | line-3-0628-0651-s008597 | station | forward | revenue | 1 |
| line-3 | line-3-0628-0651-s008597 | station | reverse | revenue | 1 |
| line-3 | line-3-0670-0604-s010026 | station | forward | revenue | 1 |
| line-3 | line-3-0670-0604-s010026 | station | reverse | revenue | 1 |
| line-3 | line-3-0763-0501-s013126 | station | forward | revenue | 1 |
| line-3 | line-3-0763-0501-s013126 | station | reverse | revenue | 1 |
| line-3 | line-3-1100-0131-s024858 | station | reverse | revenue | 2 |
| line-1 | line-1-0781-0662-s000000 | depot | — | revenue | 19 |
| line-1 | line-1-0781-0662-s000000 | depot | — | spare | 2 |
| line-1 | line-1-0781-0662-s000000 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0399-0719-s000000 | depot | — | revenue | 16 |
| line-2 | line-2-0399-0719-s000000 | depot | — | spare | 2 |
| line-2 | line-2-0399-0719-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-1100-0131-s024858 | depot | — | revenue | 60 |
| line-3 | line-3-1100-0131-s024858 | depot | — | spare | 7 |
| line-3 | line-3-1100-0131-s024858 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/mansoura-eg-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **141 trainsets at 16 stations**; largest initial station queue **16**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **127 revenue, 11 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **32 positions**; **109 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **16 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0781-0662-s000000 | forward | revenue | 4 | pending |
| line-1 | line-1-0628-0651-s003163 | forward | revenue | 4 | pending |
| line-1 | line-1-0628-0651-s003163 | reverse | revenue | 4 | pending |
| line-1 | line-1-0528-0644-s005221 | forward | revenue | 4 | pending |
| line-1 | line-1-0528-0644-s005221 | reverse | revenue | 4 | pending |
| line-1 | line-1-0427-0637-s007299 | forward | revenue | 3 | pending |
| line-1 | line-1-0427-0637-s007299 | reverse | revenue | 3 | pending |
| line-1 | line-1-0292-0628-s010085 | reverse | revenue | 3 | pending |
| line-1 | line-1-0427-0637-s007299 | forward | spare | 1 | pending |
| line-1 | line-1-0427-0637-s007299 | reverse | spare | 1 | pending |
| line-1 | line-1-0292-0628-s010085 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0399-0719-s000000 | forward | revenue | 4 | pending |
| line-2 | line-2-0427-0637-s001872 | forward | revenue | 4 | pending |
| line-2 | line-2-0427-0637-s001872 | reverse | revenue | 3 | pending |
| line-2 | line-2-0463-0533-s004297 | forward | revenue | 3 | pending |
| line-2 | line-2-0463-0533-s004297 | reverse | revenue | 3 | pending |
| line-2 | line-2-0499-0428-s006742 | forward | revenue | 3 | pending |
| line-2 | line-2-0499-0428-s006742 | reverse | revenue | 3 | pending |
| line-2 | line-2-0536-0322-s009169 | reverse | revenue | 3 | pending |
| line-2 | line-2-0427-0637-s001872 | reverse | spare | 1 | pending |
| line-2 | line-2-0463-0533-s004297 | forward | spare | 1 | pending |
| line-2 | line-2-0463-0533-s004297 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0405-0945-s000000 | forward | revenue | 8 | pending |
| line-3 | line-3-0581-0703-s007016 | forward | revenue | 8 | pending |
| line-3 | line-3-0581-0703-s007016 | reverse | revenue | 7 | pending |
| line-3 | line-3-0628-0651-s008597 | forward | revenue | 7 | pending |
| line-3 | line-3-0628-0651-s008597 | reverse | revenue | 7 | pending |
| line-3 | line-3-0670-0604-s010026 | forward | revenue | 7 | pending |
| line-3 | line-3-0670-0604-s010026 | reverse | revenue | 7 | pending |
| line-3 | line-3-0763-0501-s013126 | forward | revenue | 7 | pending |
| line-3 | line-3-0763-0501-s013126 | reverse | revenue | 7 | pending |
| line-3 | line-3-1100-0131-s024858 | reverse | revenue | 7 | pending |
| line-3 | line-3-0581-0703-s007016 | reverse | spare | 1 | pending |
| line-3 | line-3-0628-0651-s008597 | forward | spare | 1 | pending |
| line-3 | line-3-0628-0651-s008597 | reverse | spare | 1 | pending |
| line-3 | line-3-0670-0604-s010026 | forward | spare | 1 | pending |
| line-3 | line-3-0670-0604-s010026 | reverse | spare | 1 | pending |
| line-3 | line-3-0763-0501-s013126 | forward | spare | 1 | pending |
| line-3 | line-3-0763-0501-s013126 | reverse | spare | 1 | pending |
| line-3 | line-3-1100-0131-s024858 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**101 trainsets exceed the reference platform envelope**, requiring **6,009.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0292-0628-s010085 | 4 | 2 | 2 | 119.0 |
| line-1-0427-0637-s007299 | 8 | 4 | 4 | 238.0 |
| line-1-0528-0644-s005221 | 8 | 2 | 6 | 357.0 |
| line-1-0628-0651-s003163 | 8 | 4 | 4 | 238.0 |
| line-1-0781-0662-s000000 | 4 | 2 | 2 | 119.0 |
| line-2-0399-0719-s000000 | 4 | 2 | 2 | 119.0 |
| line-2-0427-0637-s001872 | 8 | 4 | 4 | 238.0 |
| line-2-0463-0533-s004297 | 8 | 2 | 6 | 357.0 |
| line-2-0499-0428-s006742 | 6 | 2 | 4 | 238.0 |
| line-2-0536-0322-s009169 | 3 | 2 | 1 | 59.5 |
| line-3-0405-0945-s000000 | 8 | 2 | 6 | 357.0 |
| line-3-0581-0703-s007016 | 16 | 2 | 14 | 833.0 |
| line-3-0628-0651-s008597 | 16 | 4 | 12 | 714.0 |
| line-3-0670-0604-s010026 | 16 | 2 | 14 | 833.0 |
| line-3-0763-0501-s013126 | 16 | 2 | 14 | 833.0 |
| line-3-1100-0131-s024858 | 8 | 2 | 6 | 357.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Egypt/Mansoura-Eg/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
