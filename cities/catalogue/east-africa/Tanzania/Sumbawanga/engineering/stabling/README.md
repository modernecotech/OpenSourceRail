# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **40 trainsets at stations + 30 at depots = 70 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0318-0457-s000000 | line-1 | declared-depot | 5 | 245.0 | 2 |
| line-2-0270-0428-s004130 | line-2 | declared-depot | 6 | 294.0 | 2 |
| line-3-0277-0363-s000000 | line-3 | declared-depot | 4 | 196.0 | 2 |
| line-4-0404-0404-s000000 | line-4 | declared-depot | 5 | 245.0 | 2 |
| line-5-0311-0363-s000000 | line-5 | declared-depot | 5 | 245.0 | 2 |
| line-6-0247-0366-s000000 | line-6 | declared-depot | 5 | 245.0 | 2 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0215-0324-s003771 | station | reverse | revenue | 2 |
| line-1 | line-1-0247-0366-s002607 | station | forward | revenue | 1 |
| line-1 | line-1-0247-0366-s002607 | station | reverse | revenue | 1 |
| line-1 | line-1-0292-0424-s000934 | station | forward | revenue | 1 |
| line-1 | line-1-0292-0424-s000934 | station | reverse | revenue | 1 |
| line-1 | line-1-0318-0457-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0270-0428-s004130 | station | reverse | revenue | 2 |
| line-2 | line-2-0292-0424-s003657 | station | forward | revenue | 1 |
| line-2 | line-2-0292-0424-s003657 | station | reverse | revenue | 1 |
| line-2 | line-2-0404-0404-s001251 | station | forward | revenue | 1 |
| line-2 | line-2-0404-0404-s001251 | station | reverse | revenue | 1 |
| line-2 | line-2-0462-0393-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0277-0363-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0311-0363-s000680 | station | forward | revenue | 1 |
| line-3 | line-3-0311-0363-s000680 | station | reverse | revenue | 1 |
| line-3 | line-3-0375-0363-s001960 | station | reverse | revenue | 2 |
| line-4 | line-4-0404-0404-s000000 | station | forward | revenue | 2 |
| line-4 | line-4-0413-0462-s001235 | station | forward | revenue | 1 |
| line-4 | line-4-0413-0462-s001235 | station | reverse | revenue | 1 |
| line-4 | line-4-0489-0487-s002962 | station | reverse | revenue | 2 |
| line-5 | line-5-0239-0263-s003112 | station | reverse | revenue | 2 |
| line-5 | line-5-0311-0291-s001440 | station | forward | revenue | 1 |
| line-5 | line-5-0311-0291-s001440 | station | reverse | revenue | 1 |
| line-5 | line-5-0311-0363-s000000 | station | forward | revenue | 2 |
| line-6 | line-6-0189-0411-s001533 | station | forward | revenue | 1 |
| line-6 | line-6-0189-0411-s001533 | station | reverse | revenue | 1 |
| line-6 | line-6-0237-0486-s003430 | station | reverse | revenue | 2 |
| line-6 | line-6-0247-0366-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0318-0457-s000000 | depot | — | revenue | 3 |
| line-1 | line-1-0318-0457-s000000 | depot | — | spare | 1 |
| line-1 | line-1-0318-0457-s000000 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0270-0428-s004130 | depot | — | revenue | 4 |
| line-2 | line-2-0270-0428-s004130 | depot | — | spare | 1 |
| line-2 | line-2-0270-0428-s004130 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0277-0363-s000000 | depot | — | revenue | 2 |
| line-3 | line-3-0277-0363-s000000 | depot | — | spare | 1 |
| line-3 | line-3-0277-0363-s000000 | depot | — | cold_reserve | 1 |
| line-4 | line-4-0404-0404-s000000 | depot | — | revenue | 3 |
| line-4 | line-4-0404-0404-s000000 | depot | — | spare | 1 |
| line-4 | line-4-0404-0404-s000000 | depot | — | cold_reserve | 1 |
| line-5 | line-5-0311-0363-s000000 | depot | — | revenue | 3 |
| line-5 | line-5-0311-0363-s000000 | depot | — | spare | 1 |
| line-5 | line-5-0311-0363-s000000 | depot | — | cold_reserve | 1 |
| line-6 | line-6-0247-0366-s000000 | depot | — | revenue | 3 |
| line-6 | line-6-0247-0366-s000000 | depot | — | spare | 1 |
| line-6 | line-6-0247-0366-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/sumbawanga-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **70 trainsets at 20 stations**; largest initial station queue **6**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **58 revenue, 6 spare, 6 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **40 positions**; **30 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **14 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0318-0457-s000000 | forward | revenue | 2 | pending |
| line-1 | line-1-0292-0424-s000934 | forward | revenue | 2 | pending |
| line-1 | line-1-0292-0424-s000934 | reverse | revenue | 2 | pending |
| line-1 | line-1-0247-0366-s002607 | forward | revenue | 2 | pending |
| line-1 | line-1-0247-0366-s002607 | reverse | revenue | 2 | pending |
| line-1 | line-1-0215-0324-s003771 | reverse | revenue | 1 | pending |
| line-1 | line-1-0215-0324-s003771 | reverse | spare | 1 | pending |
| line-1 | line-1-0318-0457-s000000 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0462-0393-s000000 | forward | revenue | 2 | pending |
| line-2 | line-2-0404-0404-s001251 | forward | revenue | 2 | pending |
| line-2 | line-2-0404-0404-s001251 | reverse | revenue | 2 | pending |
| line-2 | line-2-0292-0424-s003657 | forward | revenue | 2 | pending |
| line-2 | line-2-0292-0424-s003657 | reverse | revenue | 2 | pending |
| line-2 | line-2-0270-0428-s004130 | reverse | revenue | 2 | pending |
| line-2 | line-2-0462-0393-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0404-0404-s001251 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0277-0363-s000000 | forward | revenue | 2 | pending |
| line-3 | line-3-0311-0363-s000680 | forward | revenue | 2 | pending |
| line-3 | line-3-0311-0363-s000680 | reverse | revenue | 2 | pending |
| line-3 | line-3-0375-0363-s001960 | reverse | revenue | 2 | pending |
| line-3 | line-3-0277-0363-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0311-0363-s000680 | forward | cold_reserve | 1 | pending |
| line-4 | line-4-0404-0404-s000000 | forward | revenue | 3 | pending |
| line-4 | line-4-0413-0462-s001235 | forward | revenue | 2 | pending |
| line-4 | line-4-0413-0462-s001235 | reverse | revenue | 2 | pending |
| line-4 | line-4-0489-0487-s002962 | reverse | revenue | 2 | pending |
| line-4 | line-4-0413-0462-s001235 | forward | spare | 1 | pending |
| line-4 | line-4-0413-0462-s001235 | reverse | cold_reserve | 1 | pending |
| line-5 | line-5-0311-0363-s000000 | forward | revenue | 3 | pending |
| line-5 | line-5-0311-0291-s001440 | forward | revenue | 2 | pending |
| line-5 | line-5-0311-0291-s001440 | reverse | revenue | 2 | pending |
| line-5 | line-5-0239-0263-s003112 | reverse | revenue | 2 | pending |
| line-5 | line-5-0311-0291-s001440 | forward | spare | 1 | pending |
| line-5 | line-5-0311-0291-s001440 | reverse | cold_reserve | 1 | pending |
| line-6 | line-6-0247-0366-s000000 | forward | revenue | 3 | pending |
| line-6 | line-6-0189-0411-s001533 | forward | revenue | 2 | pending |
| line-6 | line-6-0189-0411-s001533 | reverse | revenue | 2 | pending |
| line-6 | line-6-0237-0486-s003430 | reverse | revenue | 2 | pending |
| line-6 | line-6-0189-0411-s001533 | forward | spare | 1 | pending |
| line-6 | line-6-0189-0411-s001533 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**20 trainsets exceed the reference platform envelope**, requiring **980.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0215-0324-s003771 | 2 | 2 | 0 | 0.0 |
| line-1-0247-0366-s002607 | 4 | 4 | 0 | 0.0 |
| line-1-0292-0424-s000934 | 4 | 4 | 0 | 0.0 |
| line-1-0318-0457-s000000 | 3 | 2 | 1 | 49.0 |
| line-2-0270-0428-s004130 | 2 | 2 | 0 | 0.0 |
| line-2-0292-0424-s003657 | 4 | 4 | 0 | 0.0 |
| line-2-0404-0404-s001251 | 5 | 4 | 1 | 49.0 |
| line-2-0462-0393-s000000 | 3 | 2 | 1 | 49.0 |
| line-3-0277-0363-s000000 | 3 | 2 | 1 | 49.0 |
| line-3-0311-0363-s000680 | 5 | 4 | 1 | 49.0 |
| line-3-0375-0363-s001960 | 2 | 2 | 0 | 0.0 |
| line-4-0404-0404-s000000 | 3 | 2 | 1 | 49.0 |
| line-4-0413-0462-s001235 | 6 | 2 | 4 | 196.0 |
| line-4-0489-0487-s002962 | 2 | 2 | 0 | 0.0 |
| line-5-0239-0263-s003112 | 2 | 2 | 0 | 0.0 |
| line-5-0311-0291-s001440 | 6 | 2 | 4 | 196.0 |
| line-5-0311-0363-s000000 | 3 | 2 | 1 | 49.0 |
| line-6-0189-0411-s001533 | 6 | 2 | 4 | 196.0 |
| line-6-0237-0486-s003430 | 2 | 2 | 0 | 0.0 |
| line-6-0247-0366-s000000 | 3 | 2 | 1 | 49.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Tanzania/Sumbawanga/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
