# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **36 trainsets at stations + 143 at depots = 179 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0250-0950-s000000 | line-1 | declared-depot | 40 | 2,380.0 | 8 |
| line-2-0000-0177-s020164 | line-2 | declared-depot | 52 | 3,094.0 | 9 |
| line-3-0139-0104-s000000 | line-3 | declared-depot | 51 | 3,034.5 | 9 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0250-0950-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0300-0845-s003020 | station | forward | revenue | 1 |
| line-1 | line-1-0300-0845-s003020 | station | reverse | revenue | 1 |
| line-1 | line-1-0401-0759-s006045 | station | forward | revenue | 1 |
| line-1 | line-1-0401-0759-s006045 | station | reverse | revenue | 1 |
| line-1 | line-1-0501-0674-s009054 | station | forward | revenue | 1 |
| line-1 | line-1-0501-0674-s009054 | station | reverse | revenue | 1 |
| line-1 | line-1-0601-0588-s012071 | station | forward | revenue | 1 |
| line-1 | line-1-0601-0588-s012071 | station | reverse | revenue | 1 |
| line-1 | line-1-0778-0438-s017369 | station | reverse | revenue | 2 |
| line-2 | line-2-0000-0177-s020164 | station | reverse | revenue | 2 |
| line-2 | line-2-0239-0322-s013038 | station | forward | revenue | 1 |
| line-2 | line-2-0239-0322-s013038 | station | reverse | revenue | 1 |
| line-2 | line-2-0330-0450-s009537 | station | forward | revenue | 1 |
| line-2 | line-2-0330-0450-s009537 | station | reverse | revenue | 1 |
| line-2 | line-2-0420-0578-s006020 | station | forward | revenue | 1 |
| line-2 | line-2-0420-0578-s006020 | station | reverse | revenue | 1 |
| line-2 | line-2-0498-0688-s003010 | station | forward | revenue | 1 |
| line-2 | line-2-0498-0688-s003010 | station | reverse | revenue | 1 |
| line-2 | line-2-0576-0798-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0139-0104-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0188-0374-s006716 | station | forward | revenue | 1 |
| line-3 | line-3-0188-0374-s006716 | station | reverse | revenue | 1 |
| line-3 | line-3-0220-0510-s009724 | station | forward | revenue | 1 |
| line-3 | line-3-0220-0510-s009724 | station | reverse | revenue | 1 |
| line-3 | line-3-0252-0647-s012729 | station | forward | revenue | 1 |
| line-3 | line-3-0252-0647-s012729 | station | reverse | revenue | 1 |
| line-3 | line-3-0284-0784-s015746 | station | forward | revenue | 1 |
| line-3 | line-3-0284-0784-s015746 | station | reverse | revenue | 1 |
| line-3 | line-3-0308-0981-s020141 | station | reverse | revenue | 2 |
| line-1 | line-1-0250-0950-s000000 | depot | — | revenue | 35 |
| line-1 | line-1-0250-0950-s000000 | depot | — | spare | 4 |
| line-1 | line-1-0250-0950-s000000 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0000-0177-s020164 | depot | — | revenue | 46 |
| line-2 | line-2-0000-0177-s020164 | depot | — | spare | 5 |
| line-2 | line-2-0000-0177-s020164 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0139-0104-s000000 | depot | — | revenue | 45 |
| line-3 | line-3-0139-0104-s000000 | depot | — | spare | 5 |
| line-3 | line-3-0139-0104-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/east-london-za-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **179 trainsets at 18 stations**; largest initial station queue **14**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **162 revenue, 14 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **36 positions**; **143 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **18 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0250-0950-s000000 | forward | revenue | 5 | pending |
| line-1 | line-1-0300-0845-s003020 | forward | revenue | 5 | pending |
| line-1 | line-1-0300-0845-s003020 | reverse | revenue | 5 | pending |
| line-1 | line-1-0401-0759-s006045 | forward | revenue | 5 | pending |
| line-1 | line-1-0401-0759-s006045 | reverse | revenue | 5 | pending |
| line-1 | line-1-0501-0674-s009054 | forward | revenue | 5 | pending |
| line-1 | line-1-0501-0674-s009054 | reverse | revenue | 5 | pending |
| line-1 | line-1-0601-0588-s012071 | forward | revenue | 4 | pending |
| line-1 | line-1-0601-0588-s012071 | reverse | revenue | 4 | pending |
| line-1 | line-1-0778-0438-s017369 | reverse | revenue | 4 | pending |
| line-1 | line-1-0601-0588-s012071 | forward | spare | 1 | pending |
| line-1 | line-1-0601-0588-s012071 | reverse | spare | 1 | pending |
| line-1 | line-1-0778-0438-s017369 | reverse | spare | 1 | pending |
| line-1 | line-1-0250-0950-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0300-0845-s003020 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0576-0798-s000000 | forward | revenue | 6 | pending |
| line-2 | line-2-0498-0688-s003010 | forward | revenue | 6 | pending |
| line-2 | line-2-0498-0688-s003010 | reverse | revenue | 6 | pending |
| line-2 | line-2-0420-0578-s006020 | forward | revenue | 6 | pending |
| line-2 | line-2-0420-0578-s006020 | reverse | revenue | 6 | pending |
| line-2 | line-2-0330-0450-s009537 | forward | revenue | 6 | pending |
| line-2 | line-2-0330-0450-s009537 | reverse | revenue | 6 | pending |
| line-2 | line-2-0239-0322-s013038 | forward | revenue | 6 | pending |
| line-2 | line-2-0239-0322-s013038 | reverse | revenue | 5 | pending |
| line-2 | line-2-0000-0177-s020164 | reverse | revenue | 5 | pending |
| line-2 | line-2-0239-0322-s013038 | reverse | spare | 1 | pending |
| line-2 | line-2-0000-0177-s020164 | reverse | spare | 1 | pending |
| line-2 | line-2-0576-0798-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0498-0688-s003010 | forward | spare | 1 | pending |
| line-2 | line-2-0498-0688-s003010 | reverse | spare | 1 | pending |
| line-2 | line-2-0420-0578-s006020 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0139-0104-s000000 | forward | revenue | 6 | pending |
| line-3 | line-3-0188-0374-s006716 | forward | revenue | 6 | pending |
| line-3 | line-3-0188-0374-s006716 | reverse | revenue | 6 | pending |
| line-3 | line-3-0220-0510-s009724 | forward | revenue | 6 | pending |
| line-3 | line-3-0220-0510-s009724 | reverse | revenue | 6 | pending |
| line-3 | line-3-0252-0647-s012729 | forward | revenue | 6 | pending |
| line-3 | line-3-0252-0647-s012729 | reverse | revenue | 6 | pending |
| line-3 | line-3-0284-0784-s015746 | forward | revenue | 5 | pending |
| line-3 | line-3-0284-0784-s015746 | reverse | revenue | 5 | pending |
| line-3 | line-3-0308-0981-s020141 | reverse | revenue | 5 | pending |
| line-3 | line-3-0284-0784-s015746 | forward | spare | 1 | pending |
| line-3 | line-3-0284-0784-s015746 | reverse | spare | 1 | pending |
| line-3 | line-3-0308-0981-s020141 | reverse | spare | 1 | pending |
| line-3 | line-3-0139-0104-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0188-0374-s006716 | forward | spare | 1 | pending |
| line-3 | line-3-0188-0374-s006716 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**139 trainsets exceed the reference platform envelope**, requiring **8,270.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0250-0950-s000000 | 6 | 2 | 4 | 238.0 |
| line-1-0300-0845-s003020 | 11 | 2 | 9 | 535.5 |
| line-1-0401-0759-s006045 | 10 | 2 | 8 | 476.0 |
| line-1-0501-0674-s009054 | 10 | 4 | 6 | 357.0 |
| line-1-0601-0588-s012071 | 10 | 2 | 8 | 476.0 |
| line-1-0778-0438-s017369 | 5 | 2 | 3 | 178.5 |
| line-2-0000-0177-s020164 | 6 | 2 | 4 | 238.0 |
| line-2-0239-0322-s013038 | 12 | 2 | 10 | 595.0 |
| line-2-0330-0450-s009537 | 12 | 2 | 10 | 595.0 |
| line-2-0420-0578-s006020 | 13 | 2 | 11 | 654.5 |
| line-2-0498-0688-s003010 | 14 | 4 | 10 | 595.0 |
| line-2-0576-0798-s000000 | 7 | 2 | 5 | 297.5 |
| line-3-0139-0104-s000000 | 7 | 2 | 5 | 297.5 |
| line-3-0188-0374-s006716 | 14 | 2 | 12 | 714.0 |
| line-3-0220-0510-s009724 | 12 | 2 | 10 | 595.0 |
| line-3-0252-0647-s012729 | 12 | 2 | 10 | 595.0 |
| line-3-0284-0784-s015746 | 12 | 2 | 10 | 595.0 |
| line-3-0308-0981-s020141 | 6 | 2 | 4 | 238.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/south-africa/South Africa/East-London-Za/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
