# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **30 trainsets at stations + 83 at depots = 113 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0051-0779-s016646 | line-1 | declared-depot | 41 | 2,439.5 | 8 |
| line-2-0693-0212-s000000 | line-2 | declared-depot | 24 | 1,428.0 | 5 |
| line-3-0771-0652-s000000 | line-3 | declared-depot | 18 | 1,071.0 | 4 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0051-0779-s016646 | station | reverse | revenue | 2 |
| line-1 | line-1-0555-0679-s004946 | station | forward | revenue | 1 |
| line-1 | line-1-0555-0679-s004946 | station | reverse | revenue | 1 |
| line-1 | line-1-0644-0660-s003009 | station | forward | revenue | 1 |
| line-1 | line-1-0644-0660-s003009 | station | reverse | revenue | 1 |
| line-1 | line-1-0752-0637-s000658 | station | forward | revenue | 1 |
| line-1 | line-1-0752-0637-s000658 | station | reverse | revenue | 1 |
| line-1 | line-1-0782-0630-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0550-0694-s011018 | station | reverse | revenue | 2 |
| line-2 | line-2-0555-0679-s010676 | station | forward | revenue | 1 |
| line-2 | line-2-0555-0679-s010676 | station | reverse | revenue | 1 |
| line-2 | line-2-0603-0524-s007155 | station | forward | revenue | 1 |
| line-2 | line-2-0603-0524-s007155 | station | reverse | revenue | 1 |
| line-2 | line-2-0652-0372-s003674 | station | forward | revenue | 1 |
| line-2 | line-2-0652-0372-s003674 | station | reverse | revenue | 1 |
| line-2 | line-2-0693-0212-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0482-0431-s008138 | station | reverse | revenue | 2 |
| line-3 | line-3-0603-0524-s004760 | station | forward | revenue | 1 |
| line-3 | line-3-0603-0524-s004760 | station | reverse | revenue | 1 |
| line-3 | line-3-0664-0570-s003018 | station | forward | revenue | 1 |
| line-3 | line-3-0664-0570-s003018 | station | reverse | revenue | 1 |
| line-3 | line-3-0752-0637-s000539 | station | forward | revenue | 1 |
| line-3 | line-3-0752-0637-s000539 | station | reverse | revenue | 1 |
| line-3 | line-3-0771-0652-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0051-0779-s016646 | depot | — | revenue | 36 |
| line-1 | line-1-0051-0779-s016646 | depot | — | spare | 4 |
| line-1 | line-1-0051-0779-s016646 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0693-0212-s000000 | depot | — | revenue | 20 |
| line-2 | line-2-0693-0212-s000000 | depot | — | spare | 3 |
| line-2 | line-2-0693-0212-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0771-0652-s000000 | depot | — | revenue | 15 |
| line-3 | line-3-0771-0652-s000000 | depot | — | spare | 2 |
| line-3 | line-3-0771-0652-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/kumba-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **113 trainsets at 15 stations**; largest initial station queue **14**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **101 revenue, 9 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **30 positions**; **83 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **15 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0782-0630-s000000 | forward | revenue | 6 | pending |
| line-1 | line-1-0752-0637-s000658 | forward | revenue | 6 | pending |
| line-1 | line-1-0752-0637-s000658 | reverse | revenue | 6 | pending |
| line-1 | line-1-0644-0660-s003009 | forward | revenue | 6 | pending |
| line-1 | line-1-0644-0660-s003009 | reverse | revenue | 6 | pending |
| line-1 | line-1-0555-0679-s004946 | forward | revenue | 6 | pending |
| line-1 | line-1-0555-0679-s004946 | reverse | revenue | 5 | pending |
| line-1 | line-1-0051-0779-s016646 | reverse | revenue | 5 | pending |
| line-1 | line-1-0555-0679-s004946 | reverse | spare | 1 | pending |
| line-1 | line-1-0051-0779-s016646 | reverse | spare | 1 | pending |
| line-1 | line-1-0782-0630-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0752-0637-s000658 | forward | spare | 1 | pending |
| line-1 | line-1-0752-0637-s000658 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0693-0212-s000000 | forward | revenue | 4 | pending |
| line-2 | line-2-0652-0372-s003674 | forward | revenue | 4 | pending |
| line-2 | line-2-0652-0372-s003674 | reverse | revenue | 4 | pending |
| line-2 | line-2-0603-0524-s007155 | forward | revenue | 4 | pending |
| line-2 | line-2-0603-0524-s007155 | reverse | revenue | 4 | pending |
| line-2 | line-2-0555-0679-s010676 | forward | revenue | 4 | pending |
| line-2 | line-2-0555-0679-s010676 | reverse | revenue | 3 | pending |
| line-2 | line-2-0550-0694-s011018 | reverse | revenue | 3 | pending |
| line-2 | line-2-0555-0679-s010676 | reverse | spare | 1 | pending |
| line-2 | line-2-0550-0694-s011018 | reverse | spare | 1 | pending |
| line-2 | line-2-0693-0212-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0652-0372-s003674 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0771-0652-s000000 | forward | revenue | 4 | pending |
| line-3 | line-3-0752-0637-s000539 | forward | revenue | 3 | pending |
| line-3 | line-3-0752-0637-s000539 | reverse | revenue | 3 | pending |
| line-3 | line-3-0664-0570-s003018 | forward | revenue | 3 | pending |
| line-3 | line-3-0664-0570-s003018 | reverse | revenue | 3 | pending |
| line-3 | line-3-0603-0524-s004760 | forward | revenue | 3 | pending |
| line-3 | line-3-0603-0524-s004760 | reverse | revenue | 3 | pending |
| line-3 | line-3-0482-0431-s008138 | reverse | revenue | 3 | pending |
| line-3 | line-3-0752-0637-s000539 | forward | spare | 1 | pending |
| line-3 | line-3-0752-0637-s000539 | reverse | spare | 1 | pending |
| line-3 | line-3-0664-0570-s003018 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**71 trainsets exceed the reference platform envelope**, requiring **4,224.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0051-0779-s016646 | 6 | 2 | 4 | 238.0 |
| line-1-0555-0679-s004946 | 12 | 4 | 8 | 476.0 |
| line-1-0644-0660-s003009 | 12 | 2 | 10 | 595.0 |
| line-1-0752-0637-s000658 | 14 | 4 | 10 | 595.0 |
| line-1-0782-0630-s000000 | 7 | 2 | 5 | 297.5 |
| line-2-0550-0694-s011018 | 4 | 2 | 2 | 119.0 |
| line-2-0555-0679-s010676 | 8 | 4 | 4 | 238.0 |
| line-2-0603-0524-s007155 | 8 | 4 | 4 | 238.0 |
| line-2-0652-0372-s003674 | 9 | 2 | 7 | 416.5 |
| line-2-0693-0212-s000000 | 5 | 2 | 3 | 178.5 |
| line-3-0482-0431-s008138 | 3 | 2 | 1 | 59.5 |
| line-3-0603-0524-s004760 | 6 | 4 | 2 | 119.0 |
| line-3-0664-0570-s003018 | 7 | 2 | 5 | 297.5 |
| line-3-0752-0637-s000539 | 8 | 4 | 4 | 238.0 |
| line-3-0771-0652-s000000 | 4 | 2 | 2 | 119.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-africa/Cameroon/Kumba/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
