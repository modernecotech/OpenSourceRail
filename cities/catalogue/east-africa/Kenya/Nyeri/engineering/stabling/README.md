# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **28 trainsets at stations + 41 at depots = 69 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0476-0588-s000000 | line-1 | declared-depot | 9 | 441.0 | 3 |
| line-2-0689-0283-s014355 | line-2 | declared-depot | 18 | 882.0 | 5 |
| line-3-0525-0111-s000000 | line-3 | declared-depot | 14 | 686.0 | 3 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0341-0217-s008656 | station | reverse | revenue | 2 |
| line-1 | line-1-0370-0297-s006780 | station | forward | revenue | 1 |
| line-1 | line-1-0370-0297-s006780 | station | reverse | revenue | 1 |
| line-1 | line-1-0399-0378-s004896 | station | forward | revenue | 1 |
| line-1 | line-1-0399-0378-s004896 | station | reverse | revenue | 1 |
| line-1 | line-1-0429-0459-s003016 | station | forward | revenue | 1 |
| line-1 | line-1-0429-0459-s003016 | station | reverse | revenue | 1 |
| line-1 | line-1-0476-0588-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0096-0563-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0295-0464-s004824 | station | forward | revenue | 1 |
| line-2 | line-2-0295-0464-s004824 | station | reverse | revenue | 1 |
| line-2 | line-2-0376-0436-s006699 | station | forward | revenue | 1 |
| line-2 | line-2-0376-0436-s006699 | station | reverse | revenue | 1 |
| line-2 | line-2-0458-0407-s008603 | station | forward | revenue | 1 |
| line-2 | line-2-0458-0407-s008603 | station | reverse | revenue | 1 |
| line-2 | line-2-0541-0377-s010523 | station | forward | revenue | 1 |
| line-2 | line-2-0541-0377-s010523 | station | reverse | revenue | 1 |
| line-2 | line-2-0689-0283-s014355 | station | reverse | revenue | 2 |
| line-3 | line-3-0218-0436-s010004 | station | reverse | revenue | 2 |
| line-3 | line-3-0386-0267-s004693 | station | forward | revenue | 1 |
| line-3 | line-3-0386-0267-s004693 | station | reverse | revenue | 1 |
| line-3 | line-3-0525-0111-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0476-0588-s000000 | depot | — | revenue | 7 |
| line-1 | line-1-0476-0588-s000000 | depot | — | spare | 1 |
| line-1 | line-1-0476-0588-s000000 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0689-0283-s014355 | depot | — | revenue | 15 |
| line-2 | line-2-0689-0283-s014355 | depot | — | spare | 2 |
| line-2 | line-2-0689-0283-s014355 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0525-0111-s000000 | depot | — | revenue | 12 |
| line-3 | line-3-0525-0111-s000000 | depot | — | spare | 1 |
| line-3 | line-3-0525-0111-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/nyeri-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **69 trainsets at 14 stations**; largest initial station queue **10**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **62 revenue, 4 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **28 positions**; **41 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **13 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0476-0588-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0429-0459-s003016 | forward | revenue | 2 | pending |
| line-1 | line-1-0429-0459-s003016 | reverse | revenue | 2 | pending |
| line-1 | line-1-0399-0378-s004896 | forward | revenue | 2 | pending |
| line-1 | line-1-0399-0378-s004896 | reverse | revenue | 2 | pending |
| line-1 | line-1-0370-0297-s006780 | forward | revenue | 2 | pending |
| line-1 | line-1-0370-0297-s006780 | reverse | revenue | 2 | pending |
| line-1 | line-1-0341-0217-s008656 | reverse | revenue | 2 | pending |
| line-1 | line-1-0429-0459-s003016 | forward | spare | 1 | pending |
| line-1 | line-1-0429-0459-s003016 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0096-0563-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0295-0464-s004824 | forward | revenue | 3 | pending |
| line-2 | line-2-0295-0464-s004824 | reverse | revenue | 3 | pending |
| line-2 | line-2-0376-0436-s006699 | forward | revenue | 3 | pending |
| line-2 | line-2-0376-0436-s006699 | reverse | revenue | 3 | pending |
| line-2 | line-2-0458-0407-s008603 | forward | revenue | 3 | pending |
| line-2 | line-2-0458-0407-s008603 | reverse | revenue | 3 | pending |
| line-2 | line-2-0541-0377-s010523 | forward | revenue | 2 | pending |
| line-2 | line-2-0541-0377-s010523 | reverse | revenue | 2 | pending |
| line-2 | line-2-0689-0283-s014355 | reverse | revenue | 2 | pending |
| line-2 | line-2-0541-0377-s010523 | forward | spare | 1 | pending |
| line-2 | line-2-0541-0377-s010523 | reverse | spare | 1 | pending |
| line-2 | line-2-0689-0283-s014355 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0525-0111-s000000 | forward | revenue | 5 | pending |
| line-3 | line-3-0386-0267-s004693 | forward | revenue | 5 | pending |
| line-3 | line-3-0386-0267-s004693 | reverse | revenue | 4 | pending |
| line-3 | line-3-0218-0436-s010004 | reverse | revenue | 4 | pending |
| line-3 | line-3-0386-0267-s004693 | reverse | spare | 1 | pending |
| line-3 | line-3-0218-0436-s010004 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**37 trainsets exceed the reference platform envelope**, requiring **1,813.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0341-0217-s008656 | 2 | 2 | 0 | 0.0 |
| line-1-0370-0297-s006780 | 4 | 4 | 0 | 0.0 |
| line-1-0399-0378-s004896 | 4 | 2 | 2 | 98.0 |
| line-1-0429-0459-s003016 | 6 | 2 | 4 | 196.0 |
| line-1-0476-0588-s000000 | 3 | 2 | 1 | 49.0 |
| line-2-0096-0563-s000000 | 3 | 2 | 1 | 49.0 |
| line-2-0295-0464-s004824 | 6 | 2 | 4 | 196.0 |
| line-2-0376-0436-s006699 | 6 | 2 | 4 | 196.0 |
| line-2-0458-0407-s008603 | 6 | 2 | 4 | 196.0 |
| line-2-0541-0377-s010523 | 6 | 2 | 4 | 196.0 |
| line-2-0689-0283-s014355 | 3 | 2 | 1 | 49.0 |
| line-3-0218-0436-s010004 | 5 | 2 | 3 | 147.0 |
| line-3-0386-0267-s004693 | 10 | 4 | 6 | 294.0 |
| line-3-0525-0111-s000000 | 5 | 2 | 3 | 147.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Kenya/Nyeri/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
