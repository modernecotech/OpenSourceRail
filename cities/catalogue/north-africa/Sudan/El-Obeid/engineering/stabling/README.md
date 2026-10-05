# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **32 trainsets at stations + 89 at depots = 121 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0431-0673-s000000 | line-1 | declared-depot | 32 | 1,904.0 | 6 |
| line-2-0933-0407-s013771 | line-2 | declared-depot | 33 | 1,963.5 | 7 |
| line-3-0999-0567-s000000 | line-3 | declared-depot | 24 | 1,428.0 | 5 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0431-0673-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0574-0655-s003009 | station | forward | revenue | 1 |
| line-1 | line-1-0574-0655-s003009 | station | reverse | revenue | 1 |
| line-1 | line-1-0717-0637-s006018 | station | forward | revenue | 1 |
| line-1 | line-1-0717-0637-s006018 | station | reverse | revenue | 1 |
| line-1 | line-1-0938-0541-s011764 | station | forward | revenue | 1 |
| line-1 | line-1-0938-0541-s011764 | station | reverse | revenue | 1 |
| line-1 | line-1-1002-0556-s013383 | station | reverse | revenue | 2 |
| line-2 | line-2-0437-0770-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0543-0689-s003002 | station | forward | revenue | 1 |
| line-2 | line-2-0543-0689-s003002 | station | reverse | revenue | 1 |
| line-2 | line-2-0651-0607-s006005 | station | forward | revenue | 1 |
| line-2 | line-2-0651-0607-s006005 | station | reverse | revenue | 1 |
| line-2 | line-2-0719-0555-s007937 | station | forward | revenue | 1 |
| line-2 | line-2-0719-0555-s007937 | station | reverse | revenue | 1 |
| line-2 | line-2-0789-0501-s009889 | station | forward | revenue | 1 |
| line-2 | line-2-0789-0501-s009889 | station | reverse | revenue | 1 |
| line-2 | line-2-0933-0407-s013771 | station | reverse | revenue | 2 |
| line-3 | line-3-0578-0800-s011015 | station | reverse | revenue | 2 |
| line-3 | line-3-0659-0759-s009020 | station | forward | revenue | 1 |
| line-3 | line-3-0659-0759-s009020 | station | reverse | revenue | 1 |
| line-3 | line-3-0740-0718-s007002 | station | forward | revenue | 1 |
| line-3 | line-3-0740-0718-s007002 | station | reverse | revenue | 1 |
| line-3 | line-3-0881-0646-s003492 | station | forward | revenue | 1 |
| line-3 | line-3-0881-0646-s003492 | station | reverse | revenue | 1 |
| line-3 | line-3-0999-0567-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0431-0673-s000000 | depot | — | revenue | 28 |
| line-1 | line-1-0431-0673-s000000 | depot | — | spare | 3 |
| line-1 | line-1-0431-0673-s000000 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0933-0407-s013771 | depot | — | revenue | 28 |
| line-2 | line-2-0933-0407-s013771 | depot | — | spare | 4 |
| line-2 | line-2-0933-0407-s013771 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0999-0567-s000000 | depot | — | revenue | 20 |
| line-3 | line-3-0999-0567-s000000 | depot | — | spare | 3 |
| line-3 | line-3-0999-0567-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/el-obeid-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **121 trainsets at 16 stations**; largest initial station queue **11**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **108 revenue, 10 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **32 positions**; **89 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **16 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0431-0673-s000000 | forward | revenue | 5 | pending |
| line-1 | line-1-0574-0655-s003009 | forward | revenue | 5 | pending |
| line-1 | line-1-0574-0655-s003009 | reverse | revenue | 5 | pending |
| line-1 | line-1-0717-0637-s006018 | forward | revenue | 5 | pending |
| line-1 | line-1-0717-0637-s006018 | reverse | revenue | 5 | pending |
| line-1 | line-1-0938-0541-s011764 | forward | revenue | 5 | pending |
| line-1 | line-1-0938-0541-s011764 | reverse | revenue | 4 | pending |
| line-1 | line-1-1002-0556-s013383 | reverse | revenue | 4 | pending |
| line-1 | line-1-0938-0541-s011764 | reverse | spare | 1 | pending |
| line-1 | line-1-1002-0556-s013383 | reverse | spare | 1 | pending |
| line-1 | line-1-0431-0673-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0574-0655-s003009 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0437-0770-s000000 | forward | revenue | 4 | pending |
| line-2 | line-2-0543-0689-s003002 | forward | revenue | 4 | pending |
| line-2 | line-2-0543-0689-s003002 | reverse | revenue | 4 | pending |
| line-2 | line-2-0651-0607-s006005 | forward | revenue | 4 | pending |
| line-2 | line-2-0651-0607-s006005 | reverse | revenue | 4 | pending |
| line-2 | line-2-0719-0555-s007937 | forward | revenue | 4 | pending |
| line-2 | line-2-0719-0555-s007937 | reverse | revenue | 4 | pending |
| line-2 | line-2-0789-0501-s009889 | forward | revenue | 4 | pending |
| line-2 | line-2-0789-0501-s009889 | reverse | revenue | 4 | pending |
| line-2 | line-2-0933-0407-s013771 | reverse | revenue | 4 | pending |
| line-2 | line-2-0437-0770-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0543-0689-s003002 | forward | spare | 1 | pending |
| line-2 | line-2-0543-0689-s003002 | reverse | spare | 1 | pending |
| line-2 | line-2-0651-0607-s006005 | forward | spare | 1 | pending |
| line-2 | line-2-0651-0607-s006005 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0999-0567-s000000 | forward | revenue | 4 | pending |
| line-3 | line-3-0881-0646-s003492 | forward | revenue | 4 | pending |
| line-3 | line-3-0881-0646-s003492 | reverse | revenue | 4 | pending |
| line-3 | line-3-0740-0718-s007002 | forward | revenue | 4 | pending |
| line-3 | line-3-0740-0718-s007002 | reverse | revenue | 4 | pending |
| line-3 | line-3-0659-0759-s009020 | forward | revenue | 4 | pending |
| line-3 | line-3-0659-0759-s009020 | reverse | revenue | 3 | pending |
| line-3 | line-3-0578-0800-s011015 | reverse | revenue | 3 | pending |
| line-3 | line-3-0659-0759-s009020 | reverse | spare | 1 | pending |
| line-3 | line-3-0578-0800-s011015 | reverse | spare | 1 | pending |
| line-3 | line-3-0999-0567-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0881-0646-s003492 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**89 trainsets exceed the reference platform envelope**, requiring **5,295.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0431-0673-s000000 | 6 | 2 | 4 | 238.0 |
| line-1-0574-0655-s003009 | 11 | 2 | 9 | 535.5 |
| line-1-0717-0637-s006018 | 10 | 2 | 8 | 476.0 |
| line-1-0938-0541-s011764 | 10 | 2 | 8 | 476.0 |
| line-1-1002-0556-s013383 | 5 | 2 | 3 | 178.5 |
| line-2-0437-0770-s000000 | 5 | 2 | 3 | 178.5 |
| line-2-0543-0689-s003002 | 10 | 2 | 8 | 476.0 |
| line-2-0651-0607-s006005 | 10 | 2 | 8 | 476.0 |
| line-2-0719-0555-s007937 | 8 | 2 | 6 | 357.0 |
| line-2-0789-0501-s009889 | 8 | 2 | 6 | 357.0 |
| line-2-0933-0407-s013771 | 4 | 2 | 2 | 119.0 |
| line-3-0578-0800-s011015 | 4 | 2 | 2 | 119.0 |
| line-3-0659-0759-s009020 | 8 | 2 | 6 | 357.0 |
| line-3-0740-0718-s007002 | 8 | 2 | 6 | 357.0 |
| line-3-0881-0646-s003492 | 9 | 2 | 7 | 416.5 |
| line-3-0999-0567-s000000 | 5 | 2 | 3 | 178.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/north-africa/Sudan/El-Obeid/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
