# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **36 trainsets at stations + 98 at depots = 134 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0708-0757-s017765 | line-1 | declared-depot | 42 | 2,499.0 | 8 |
| line-2-0768-0539-s000000 | line-2 | declared-depot | 22 | 1,309.0 | 5 |
| line-3-0581-0072-s000000 | line-3 | declared-depot | 34 | 2,023.0 | 7 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0194-0142-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0406-0382-s007001 | station | forward | revenue | 1 |
| line-1 | line-1-0406-0382-s007001 | station | reverse | revenue | 1 |
| line-1 | line-1-0491-0487-s010017 | station | forward | revenue | 1 |
| line-1 | line-1-0491-0487-s010017 | station | reverse | revenue | 1 |
| line-1 | line-1-0565-0579-s012657 | station | forward | revenue | 1 |
| line-1 | line-1-0565-0579-s012657 | station | reverse | revenue | 1 |
| line-1 | line-1-0588-0608-s013486 | station | forward | revenue | 1 |
| line-1 | line-1-0588-0608-s013486 | station | reverse | revenue | 1 |
| line-1 | line-1-0708-0757-s017765 | station | reverse | revenue | 2 |
| line-2 | line-2-0313-0629-s009846 | station | reverse | revenue | 2 |
| line-2 | line-2-0439-0604-s007118 | station | forward | revenue | 1 |
| line-2 | line-2-0439-0604-s007118 | station | reverse | revenue | 1 |
| line-2 | line-2-0565-0579-s004391 | station | forward | revenue | 1 |
| line-2 | line-2-0565-0579-s004391 | station | reverse | revenue | 1 |
| line-2 | line-2-0588-0575-s003898 | station | forward | revenue | 1 |
| line-2 | line-2-0588-0575-s003898 | station | reverse | revenue | 1 |
| line-2 | line-2-0645-0563-s002659 | station | forward | revenue | 1 |
| line-2 | line-2-0645-0563-s002659 | station | reverse | revenue | 1 |
| line-2 | line-2-0768-0539-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0581-0072-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0586-0750-s014110 | station | reverse | revenue | 2 |
| line-3 | line-3-0588-0575-s010593 | station | forward | revenue | 1 |
| line-3 | line-3-0588-0575-s010593 | station | reverse | revenue | 1 |
| line-3 | line-3-0588-0608-s011253 | station | forward | revenue | 1 |
| line-3 | line-3-0588-0608-s011253 | station | reverse | revenue | 1 |
| line-3 | line-3-0589-0481-s008705 | station | forward | revenue | 1 |
| line-3 | line-3-0589-0481-s008705 | station | reverse | revenue | 1 |
| line-3 | line-3-0590-0387-s006817 | station | forward | revenue | 1 |
| line-3 | line-3-0590-0387-s006817 | station | reverse | revenue | 1 |
| line-1 | line-1-0708-0757-s017765 | depot | — | revenue | 37 |
| line-1 | line-1-0708-0757-s017765 | depot | — | spare | 4 |
| line-1 | line-1-0708-0757-s017765 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0768-0539-s000000 | depot | — | revenue | 18 |
| line-2 | line-2-0768-0539-s000000 | depot | — | spare | 3 |
| line-2 | line-2-0768-0539-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0581-0072-s000000 | depot | — | revenue | 29 |
| line-3 | line-3-0581-0072-s000000 | depot | — | spare | 4 |
| line-3 | line-3-0581-0072-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/hama-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **134 trainsets at 18 stations**; largest initial station queue **12**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **120 revenue, 11 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **36 positions**; **98 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **18 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0194-0142-s000000 | forward | revenue | 5 | pending |
| line-1 | line-1-0406-0382-s007001 | forward | revenue | 5 | pending |
| line-1 | line-1-0406-0382-s007001 | reverse | revenue | 5 | pending |
| line-1 | line-1-0491-0487-s010017 | forward | revenue | 5 | pending |
| line-1 | line-1-0491-0487-s010017 | reverse | revenue | 5 | pending |
| line-1 | line-1-0565-0579-s012657 | forward | revenue | 5 | pending |
| line-1 | line-1-0565-0579-s012657 | reverse | revenue | 5 | pending |
| line-1 | line-1-0588-0608-s013486 | forward | revenue | 5 | pending |
| line-1 | line-1-0588-0608-s013486 | reverse | revenue | 5 | pending |
| line-1 | line-1-0708-0757-s017765 | reverse | revenue | 4 | pending |
| line-1 | line-1-0708-0757-s017765 | reverse | spare | 1 | pending |
| line-1 | line-1-0194-0142-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0406-0382-s007001 | forward | spare | 1 | pending |
| line-1 | line-1-0406-0382-s007001 | reverse | spare | 1 | pending |
| line-1 | line-1-0491-0487-s010017 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0768-0539-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0645-0563-s002659 | forward | revenue | 3 | pending |
| line-2 | line-2-0645-0563-s002659 | reverse | revenue | 3 | pending |
| line-2 | line-2-0588-0575-s003898 | forward | revenue | 3 | pending |
| line-2 | line-2-0588-0575-s003898 | reverse | revenue | 3 | pending |
| line-2 | line-2-0565-0579-s004391 | forward | revenue | 3 | pending |
| line-2 | line-2-0565-0579-s004391 | reverse | revenue | 3 | pending |
| line-2 | line-2-0439-0604-s007118 | forward | revenue | 3 | pending |
| line-2 | line-2-0439-0604-s007118 | reverse | revenue | 3 | pending |
| line-2 | line-2-0313-0629-s009846 | reverse | revenue | 3 | pending |
| line-2 | line-2-0768-0539-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0645-0563-s002659 | forward | spare | 1 | pending |
| line-2 | line-2-0645-0563-s002659 | reverse | spare | 1 | pending |
| line-2 | line-2-0588-0575-s003898 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0581-0072-s000000 | forward | revenue | 5 | pending |
| line-3 | line-3-0590-0387-s006817 | forward | revenue | 4 | pending |
| line-3 | line-3-0590-0387-s006817 | reverse | revenue | 4 | pending |
| line-3 | line-3-0589-0481-s008705 | forward | revenue | 4 | pending |
| line-3 | line-3-0589-0481-s008705 | reverse | revenue | 4 | pending |
| line-3 | line-3-0588-0575-s010593 | forward | revenue | 4 | pending |
| line-3 | line-3-0588-0575-s010593 | reverse | revenue | 4 | pending |
| line-3 | line-3-0588-0608-s011253 | forward | revenue | 4 | pending |
| line-3 | line-3-0588-0608-s011253 | reverse | revenue | 4 | pending |
| line-3 | line-3-0586-0750-s014110 | reverse | revenue | 4 | pending |
| line-3 | line-3-0590-0387-s006817 | forward | spare | 1 | pending |
| line-3 | line-3-0590-0387-s006817 | reverse | spare | 1 | pending |
| line-3 | line-3-0589-0481-s008705 | forward | spare | 1 | pending |
| line-3 | line-3-0589-0481-s008705 | reverse | spare | 1 | pending |
| line-3 | line-3-0588-0575-s010593 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**86 trainsets exceed the reference platform envelope**, requiring **5,117.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0194-0142-s000000 | 6 | 2 | 4 | 238.0 |
| line-1-0406-0382-s007001 | 12 | 2 | 10 | 595.0 |
| line-1-0491-0487-s010017 | 11 | 2 | 9 | 535.5 |
| line-1-0565-0579-s012657 | 10 | 4 | 6 | 357.0 |
| line-1-0588-0608-s013486 | 10 | 4 | 6 | 357.0 |
| line-1-0708-0757-s017765 | 5 | 2 | 3 | 178.5 |
| line-2-0313-0629-s009846 | 3 | 2 | 1 | 59.5 |
| line-2-0439-0604-s007118 | 6 | 2 | 4 | 238.0 |
| line-2-0565-0579-s004391 | 6 | 4 | 2 | 119.0 |
| line-2-0588-0575-s003898 | 7 | 4 | 3 | 178.5 |
| line-2-0645-0563-s002659 | 8 | 2 | 6 | 357.0 |
| line-2-0768-0539-s000000 | 4 | 2 | 2 | 119.0 |
| line-3-0581-0072-s000000 | 5 | 2 | 3 | 178.5 |
| line-3-0586-0750-s014110 | 4 | 2 | 2 | 119.0 |
| line-3-0588-0575-s010593 | 9 | 4 | 5 | 297.5 |
| line-3-0588-0608-s011253 | 8 | 4 | 4 | 238.0 |
| line-3-0589-0481-s008705 | 10 | 2 | 8 | 476.0 |
| line-3-0590-0387-s006817 | 10 | 2 | 8 | 476.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Syria/Hama/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
