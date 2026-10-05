# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **50 trainsets at stations + 165 at depots = 215 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-1093-1079-s000000 | line-1 | declared-depot | 54 | 3,213.0 | 10 |
| line-2-0790-0952-s023675 | line-2 | declared-depot | 54 | 3,213.0 | 10 |
| line-3-1061-0928-s000000 | line-3 | declared-depot | 57 | 3,391.5 | 11 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0435-0260-s023208 | station | reverse | revenue | 2 |
| line-1 | line-1-0533-0386-s019631 | station | forward | revenue | 1 |
| line-1 | line-1-0533-0386-s019631 | station | reverse | revenue | 1 |
| line-1 | line-1-0615-0492-s016620 | station | forward | revenue | 1 |
| line-1 | line-1-0615-0492-s016620 | station | reverse | revenue | 1 |
| line-1 | line-1-0698-0598-s013602 | station | forward | revenue | 1 |
| line-1 | line-1-0698-0598-s013602 | station | reverse | revenue | 1 |
| line-1 | line-1-0781-0705-s010575 | station | forward | revenue | 1 |
| line-1 | line-1-0781-0705-s010575 | station | reverse | revenue | 1 |
| line-1 | line-1-0863-0811-s007565 | station | forward | revenue | 1 |
| line-1 | line-1-0863-0811-s007565 | station | reverse | revenue | 1 |
| line-1 | line-1-0938-0925-s004555 | station | forward | revenue | 1 |
| line-1 | line-1-0938-0925-s004555 | station | reverse | revenue | 1 |
| line-1 | line-1-1093-1079-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0137-0141-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0354-0291-s005714 | station | forward | revenue | 1 |
| line-2 | line-2-0354-0291-s005714 | station | reverse | revenue | 1 |
| line-2 | line-2-0423-0408-s008731 | station | forward | revenue | 1 |
| line-2 | line-2-0423-0408-s008731 | station | reverse | revenue | 1 |
| line-2 | line-2-0492-0524-s011740 | station | forward | revenue | 1 |
| line-2 | line-2-0492-0524-s011740 | station | reverse | revenue | 1 |
| line-2 | line-2-0561-0641-s014757 | station | forward | revenue | 1 |
| line-2 | line-2-0561-0641-s014757 | station | reverse | revenue | 1 |
| line-2 | line-2-0630-0758-s017774 | station | forward | revenue | 1 |
| line-2 | line-2-0630-0758-s017774 | station | reverse | revenue | 1 |
| line-2 | line-2-0697-0872-s020726 | station | forward | revenue | 1 |
| line-2 | line-2-0697-0872-s020726 | station | reverse | revenue | 1 |
| line-2 | line-2-0790-0952-s023675 | station | reverse | revenue | 2 |
| line-3 | line-3-0104-0580-s023665 | station | reverse | revenue | 2 |
| line-3 | line-3-0297-0591-s019371 | station | forward | revenue | 1 |
| line-3 | line-3-0297-0591-s019371 | station | reverse | revenue | 1 |
| line-3 | line-3-0388-0626-s017226 | station | forward | revenue | 1 |
| line-3 | line-3-0388-0626-s017226 | station | reverse | revenue | 1 |
| line-3 | line-3-0480-0662-s015064 | station | forward | revenue | 1 |
| line-3 | line-3-0480-0662-s015064 | station | reverse | revenue | 1 |
| line-3 | line-3-0608-0711-s012052 | station | forward | revenue | 1 |
| line-3 | line-3-0608-0711-s012052 | station | reverse | revenue | 1 |
| line-3 | line-3-0736-0761-s009042 | station | forward | revenue | 1 |
| line-3 | line-3-0736-0761-s009042 | station | reverse | revenue | 1 |
| line-3 | line-3-0863-0810-s006038 | station | forward | revenue | 1 |
| line-3 | line-3-0863-0810-s006038 | station | reverse | revenue | 1 |
| line-3 | line-3-0974-0872-s003034 | station | forward | revenue | 1 |
| line-3 | line-3-0974-0872-s003034 | station | reverse | revenue | 1 |
| line-3 | line-3-1061-0928-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-1093-1079-s000000 | depot | — | revenue | 47 |
| line-1 | line-1-1093-1079-s000000 | depot | — | spare | 6 |
| line-1 | line-1-1093-1079-s000000 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0790-0952-s023675 | depot | — | revenue | 47 |
| line-2 | line-2-0790-0952-s023675 | depot | — | spare | 6 |
| line-2 | line-2-0790-0952-s023675 | depot | — | cold_reserve | 1 |
| line-3 | line-3-1061-0928-s000000 | depot | — | revenue | 50 |
| line-3 | line-3-1061-0928-s000000 | depot | — | spare | 6 |
| line-3 | line-3-1061-0928-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/agadir-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **215 trainsets at 25 stations**; largest initial station queue **10**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **194 revenue, 18 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **50 positions**; **165 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **25 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-1093-1079-s000000 | forward | revenue | 5 | pending |
| line-1 | line-1-0938-0925-s004555 | forward | revenue | 5 | pending |
| line-1 | line-1-0938-0925-s004555 | reverse | revenue | 5 | pending |
| line-1 | line-1-0863-0811-s007565 | forward | revenue | 5 | pending |
| line-1 | line-1-0863-0811-s007565 | reverse | revenue | 5 | pending |
| line-1 | line-1-0781-0705-s010575 | forward | revenue | 5 | pending |
| line-1 | line-1-0781-0705-s010575 | reverse | revenue | 5 | pending |
| line-1 | line-1-0698-0598-s013602 | forward | revenue | 4 | pending |
| line-1 | line-1-0698-0598-s013602 | reverse | revenue | 4 | pending |
| line-1 | line-1-0615-0492-s016620 | forward | revenue | 4 | pending |
| line-1 | line-1-0615-0492-s016620 | reverse | revenue | 4 | pending |
| line-1 | line-1-0533-0386-s019631 | forward | revenue | 4 | pending |
| line-1 | line-1-0533-0386-s019631 | reverse | revenue | 4 | pending |
| line-1 | line-1-0435-0260-s023208 | reverse | revenue | 4 | pending |
| line-1 | line-1-0698-0598-s013602 | forward | spare | 1 | pending |
| line-1 | line-1-0698-0598-s013602 | reverse | spare | 1 | pending |
| line-1 | line-1-0615-0492-s016620 | forward | spare | 1 | pending |
| line-1 | line-1-0615-0492-s016620 | reverse | spare | 1 | pending |
| line-1 | line-1-0533-0386-s019631 | forward | spare | 1 | pending |
| line-1 | line-1-0533-0386-s019631 | reverse | spare | 1 | pending |
| line-1 | line-1-0435-0260-s023208 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0137-0141-s000000 | forward | revenue | 5 | pending |
| line-2 | line-2-0354-0291-s005714 | forward | revenue | 5 | pending |
| line-2 | line-2-0354-0291-s005714 | reverse | revenue | 5 | pending |
| line-2 | line-2-0423-0408-s008731 | forward | revenue | 5 | pending |
| line-2 | line-2-0423-0408-s008731 | reverse | revenue | 5 | pending |
| line-2 | line-2-0492-0524-s011740 | forward | revenue | 5 | pending |
| line-2 | line-2-0492-0524-s011740 | reverse | revenue | 5 | pending |
| line-2 | line-2-0561-0641-s014757 | forward | revenue | 4 | pending |
| line-2 | line-2-0561-0641-s014757 | reverse | revenue | 4 | pending |
| line-2 | line-2-0630-0758-s017774 | forward | revenue | 4 | pending |
| line-2 | line-2-0630-0758-s017774 | reverse | revenue | 4 | pending |
| line-2 | line-2-0697-0872-s020726 | forward | revenue | 4 | pending |
| line-2 | line-2-0697-0872-s020726 | reverse | revenue | 4 | pending |
| line-2 | line-2-0790-0952-s023675 | reverse | revenue | 4 | pending |
| line-2 | line-2-0561-0641-s014757 | forward | spare | 1 | pending |
| line-2 | line-2-0561-0641-s014757 | reverse | spare | 1 | pending |
| line-2 | line-2-0630-0758-s017774 | forward | spare | 1 | pending |
| line-2 | line-2-0630-0758-s017774 | reverse | spare | 1 | pending |
| line-2 | line-2-0697-0872-s020726 | forward | spare | 1 | pending |
| line-2 | line-2-0697-0872-s020726 | reverse | spare | 1 | pending |
| line-2 | line-2-0790-0952-s023675 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-1061-0928-s000000 | forward | revenue | 5 | pending |
| line-3 | line-3-0974-0872-s003034 | forward | revenue | 5 | pending |
| line-3 | line-3-0974-0872-s003034 | reverse | revenue | 5 | pending |
| line-3 | line-3-0863-0810-s006038 | forward | revenue | 5 | pending |
| line-3 | line-3-0863-0810-s006038 | reverse | revenue | 4 | pending |
| line-3 | line-3-0736-0761-s009042 | forward | revenue | 4 | pending |
| line-3 | line-3-0736-0761-s009042 | reverse | revenue | 4 | pending |
| line-3 | line-3-0608-0711-s012052 | forward | revenue | 4 | pending |
| line-3 | line-3-0608-0711-s012052 | reverse | revenue | 4 | pending |
| line-3 | line-3-0480-0662-s015064 | forward | revenue | 4 | pending |
| line-3 | line-3-0480-0662-s015064 | reverse | revenue | 4 | pending |
| line-3 | line-3-0388-0626-s017226 | forward | revenue | 4 | pending |
| line-3 | line-3-0388-0626-s017226 | reverse | revenue | 4 | pending |
| line-3 | line-3-0297-0591-s019371 | forward | revenue | 4 | pending |
| line-3 | line-3-0297-0591-s019371 | reverse | revenue | 4 | pending |
| line-3 | line-3-0104-0580-s023665 | reverse | revenue | 4 | pending |
| line-3 | line-3-0863-0810-s006038 | reverse | spare | 1 | pending |
| line-3 | line-3-0736-0761-s009042 | forward | spare | 1 | pending |
| line-3 | line-3-0736-0761-s009042 | reverse | spare | 1 | pending |
| line-3 | line-3-0608-0711-s012052 | forward | spare | 1 | pending |
| line-3 | line-3-0608-0711-s012052 | reverse | spare | 1 | pending |
| line-3 | line-3-0480-0662-s015064 | forward | spare | 1 | pending |
| line-3 | line-3-0480-0662-s015064 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**161 trainsets exceed the reference platform envelope**, requiring **9,579.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0435-0260-s023208 | 5 | 2 | 3 | 178.5 |
| line-1-0533-0386-s019631 | 10 | 2 | 8 | 476.0 |
| line-1-0615-0492-s016620 | 10 | 2 | 8 | 476.0 |
| line-1-0698-0598-s013602 | 10 | 2 | 8 | 476.0 |
| line-1-0781-0705-s010575 | 10 | 2 | 8 | 476.0 |
| line-1-0863-0811-s007565 | 10 | 4 | 6 | 357.0 |
| line-1-0938-0925-s004555 | 10 | 2 | 8 | 476.0 |
| line-1-1093-1079-s000000 | 5 | 2 | 3 | 178.5 |
| line-2-0137-0141-s000000 | 5 | 2 | 3 | 178.5 |
| line-2-0354-0291-s005714 | 10 | 2 | 8 | 476.0 |
| line-2-0423-0408-s008731 | 10 | 2 | 8 | 476.0 |
| line-2-0492-0524-s011740 | 10 | 2 | 8 | 476.0 |
| line-2-0561-0641-s014757 | 10 | 2 | 8 | 476.0 |
| line-2-0630-0758-s017774 | 10 | 2 | 8 | 476.0 |
| line-2-0697-0872-s020726 | 10 | 2 | 8 | 476.0 |
| line-2-0790-0952-s023675 | 5 | 2 | 3 | 178.5 |
| line-3-0104-0580-s023665 | 4 | 2 | 2 | 119.0 |
| line-3-0297-0591-s019371 | 8 | 2 | 6 | 357.0 |
| line-3-0388-0626-s017226 | 8 | 2 | 6 | 357.0 |
| line-3-0480-0662-s015064 | 10 | 2 | 8 | 476.0 |
| line-3-0608-0711-s012052 | 10 | 2 | 8 | 476.0 |
| line-3-0736-0761-s009042 | 10 | 2 | 8 | 476.0 |
| line-3-0863-0810-s006038 | 10 | 4 | 6 | 357.0 |
| line-3-0974-0872-s003034 | 10 | 2 | 8 | 476.0 |
| line-3-1061-0928-s000000 | 5 | 2 | 3 | 178.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/north-africa/Morocco/Agadir/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
