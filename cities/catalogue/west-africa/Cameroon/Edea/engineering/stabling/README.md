# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **20 trainsets at stations + 16 at depots = 36 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0442-0432-s007420 | line-1 | declared-depot | 8 | 392.0 | 3 |
| line-2-0362-0212-s000000 | line-2 | declared-depot | 8 | 392.0 | 3 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0355-0117-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0362-0212-s002310 | station | forward | revenue | 1 |
| line-1 | line-1-0362-0212-s002310 | station | reverse | revenue | 1 |
| line-1 | line-1-0388-0284-s003989 | station | forward | revenue | 1 |
| line-1 | line-1-0388-0284-s003989 | station | reverse | revenue | 1 |
| line-1 | line-1-0414-0353-s005596 | station | forward | revenue | 1 |
| line-1 | line-1-0414-0353-s005596 | station | reverse | revenue | 1 |
| line-1 | line-1-0442-0432-s007420 | station | reverse | revenue | 2 |
| line-2 | line-2-0234-0314-s003686 | station | forward | revenue | 1 |
| line-2 | line-2-0234-0314-s003686 | station | reverse | revenue | 1 |
| line-2 | line-2-0287-0237-s001707 | station | forward | revenue | 1 |
| line-2 | line-2-0287-0237-s001707 | station | reverse | revenue | 1 |
| line-2 | line-2-0288-0339-s005599 | station | forward | revenue | 1 |
| line-2 | line-2-0288-0339-s005599 | station | reverse | revenue | 1 |
| line-2 | line-2-0338-0387-s007346 | station | reverse | revenue | 2 |
| line-2 | line-2-0362-0212-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0442-0432-s007420 | depot | — | revenue | 6 |
| line-1 | line-1-0442-0432-s007420 | depot | — | spare | 1 |
| line-1 | line-1-0442-0432-s007420 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0362-0212-s000000 | depot | — | revenue | 6 |
| line-2 | line-2-0362-0212-s000000 | depot | — | spare | 1 |
| line-2 | line-2-0362-0212-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/edea-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **36 trainsets at 10 stations**; largest initial station queue **5**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **32 revenue, 2 spare, 2 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **20 positions**; **16 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **8 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0355-0117-s000000 | forward | revenue | 2 | pending |
| line-1 | line-1-0362-0212-s002310 | forward | revenue | 2 | pending |
| line-1 | line-1-0362-0212-s002310 | reverse | revenue | 2 | pending |
| line-1 | line-1-0388-0284-s003989 | forward | revenue | 2 | pending |
| line-1 | line-1-0388-0284-s003989 | reverse | revenue | 2 | pending |
| line-1 | line-1-0414-0353-s005596 | forward | revenue | 2 | pending |
| line-1 | line-1-0414-0353-s005596 | reverse | revenue | 2 | pending |
| line-1 | line-1-0442-0432-s007420 | reverse | revenue | 2 | pending |
| line-1 | line-1-0355-0117-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0362-0212-s002310 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0362-0212-s000000 | forward | revenue | 2 | pending |
| line-2 | line-2-0287-0237-s001707 | forward | revenue | 2 | pending |
| line-2 | line-2-0287-0237-s001707 | reverse | revenue | 2 | pending |
| line-2 | line-2-0234-0314-s003686 | forward | revenue | 2 | pending |
| line-2 | line-2-0234-0314-s003686 | reverse | revenue | 2 | pending |
| line-2 | line-2-0288-0339-s005599 | forward | revenue | 2 | pending |
| line-2 | line-2-0288-0339-s005599 | reverse | revenue | 2 | pending |
| line-2 | line-2-0338-0387-s007346 | reverse | revenue | 2 | pending |
| line-2 | line-2-0362-0212-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0287-0237-s001707 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**14 trainsets exceed the reference platform envelope**, requiring **686.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0355-0117-s000000 | 3 | 2 | 1 | 49.0 |
| line-1-0362-0212-s002310 | 5 | 4 | 1 | 49.0 |
| line-1-0388-0284-s003989 | 4 | 2 | 2 | 98.0 |
| line-1-0414-0353-s005596 | 4 | 2 | 2 | 98.0 |
| line-1-0442-0432-s007420 | 2 | 2 | 0 | 0.0 |
| line-2-0234-0314-s003686 | 4 | 2 | 2 | 98.0 |
| line-2-0287-0237-s001707 | 5 | 2 | 3 | 147.0 |
| line-2-0288-0339-s005599 | 4 | 2 | 2 | 98.0 |
| line-2-0338-0387-s007346 | 2 | 2 | 0 | 0.0 |
| line-2-0362-0212-s000000 | 3 | 2 | 1 | 49.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-africa/Cameroon/Edea/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
