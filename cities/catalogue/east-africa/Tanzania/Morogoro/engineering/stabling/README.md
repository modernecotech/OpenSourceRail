# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **36 trainsets at stations + 98 at depots = 134 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0392-0381-s015331 | line-1 | declared-depot | 35 | 2,082.5 | 7 |
| line-2-0869-0325-s000000 | line-2 | declared-depot | 35 | 2,082.5 | 7 |
| line-3-0885-0618-s000000 | line-3 | declared-depot | 28 | 1,666.0 | 6 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0392-0381-s015331 | station | reverse | revenue | 2 |
| line-1 | line-1-0393-0395-s015043 | station | forward | revenue | 1 |
| line-1 | line-1-0393-0395-s015043 | station | reverse | revenue | 1 |
| line-1 | line-1-0398-0499-s012922 | station | forward | revenue | 1 |
| line-1 | line-1-0398-0499-s012922 | station | reverse | revenue | 1 |
| line-1 | line-1-0400-1089-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0407-0674-s009335 | station | forward | revenue | 1 |
| line-1 | line-1-0407-0674-s009335 | station | reverse | revenue | 1 |
| line-1 | line-1-0415-0834-s006069 | station | forward | revenue | 1 |
| line-1 | line-1-0415-0834-s006069 | station | reverse | revenue | 1 |
| line-2 | line-2-0329-0733-s015141 | station | reverse | revenue | 2 |
| line-2 | line-2-0407-0674-s012986 | station | forward | revenue | 1 |
| line-2 | line-2-0407-0674-s012986 | station | reverse | revenue | 1 |
| line-2 | line-2-0520-0588-s009768 | station | forward | revenue | 1 |
| line-2 | line-2-0520-0588-s009768 | station | reverse | revenue | 1 |
| line-2 | line-2-0631-0506-s006746 | station | forward | revenue | 1 |
| line-2 | line-2-0631-0506-s006746 | station | reverse | revenue | 1 |
| line-2 | line-2-0686-0464-s005140 | station | forward | revenue | 1 |
| line-2 | line-2-0686-0464-s005140 | station | reverse | revenue | 1 |
| line-2 | line-2-0869-0325-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0357-0378-s012970 | station | reverse | revenue | 2 |
| line-3 | line-3-0393-0395-s012074 | station | forward | revenue | 1 |
| line-3 | line-3-0393-0395-s012074 | station | reverse | revenue | 1 |
| line-3 | line-3-0501-0445-s009418 | station | forward | revenue | 1 |
| line-3 | line-3-0501-0445-s009418 | station | reverse | revenue | 1 |
| line-3 | line-3-0631-0506-s006209 | station | forward | revenue | 1 |
| line-3 | line-3-0631-0506-s006209 | station | reverse | revenue | 1 |
| line-3 | line-3-0745-0559-s003394 | station | forward | revenue | 1 |
| line-3 | line-3-0745-0559-s003394 | station | reverse | revenue | 1 |
| line-3 | line-3-0885-0618-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0392-0381-s015331 | depot | — | revenue | 30 |
| line-1 | line-1-0392-0381-s015331 | depot | — | spare | 4 |
| line-1 | line-1-0392-0381-s015331 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0869-0325-s000000 | depot | — | revenue | 30 |
| line-2 | line-2-0869-0325-s000000 | depot | — | spare | 4 |
| line-2 | line-2-0869-0325-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0885-0618-s000000 | depot | — | revenue | 24 |
| line-3 | line-3-0885-0618-s000000 | depot | — | spare | 3 |
| line-3 | line-3-0885-0618-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/morogoro-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **134 trainsets at 18 stations**; largest initial station queue **10**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **120 revenue, 11 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **36 positions**; **98 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **18 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0400-1089-s000000 | forward | revenue | 5 | pending |
| line-1 | line-1-0415-0834-s006069 | forward | revenue | 5 | pending |
| line-1 | line-1-0415-0834-s006069 | reverse | revenue | 4 | pending |
| line-1 | line-1-0407-0674-s009335 | forward | revenue | 4 | pending |
| line-1 | line-1-0407-0674-s009335 | reverse | revenue | 4 | pending |
| line-1 | line-1-0398-0499-s012922 | forward | revenue | 4 | pending |
| line-1 | line-1-0398-0499-s012922 | reverse | revenue | 4 | pending |
| line-1 | line-1-0393-0395-s015043 | forward | revenue | 4 | pending |
| line-1 | line-1-0393-0395-s015043 | reverse | revenue | 4 | pending |
| line-1 | line-1-0392-0381-s015331 | reverse | revenue | 4 | pending |
| line-1 | line-1-0415-0834-s006069 | reverse | spare | 1 | pending |
| line-1 | line-1-0407-0674-s009335 | forward | spare | 1 | pending |
| line-1 | line-1-0407-0674-s009335 | reverse | spare | 1 | pending |
| line-1 | line-1-0398-0499-s012922 | forward | spare | 1 | pending |
| line-1 | line-1-0398-0499-s012922 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0869-0325-s000000 | forward | revenue | 5 | pending |
| line-2 | line-2-0686-0464-s005140 | forward | revenue | 5 | pending |
| line-2 | line-2-0686-0464-s005140 | reverse | revenue | 4 | pending |
| line-2 | line-2-0631-0506-s006746 | forward | revenue | 4 | pending |
| line-2 | line-2-0631-0506-s006746 | reverse | revenue | 4 | pending |
| line-2 | line-2-0520-0588-s009768 | forward | revenue | 4 | pending |
| line-2 | line-2-0520-0588-s009768 | reverse | revenue | 4 | pending |
| line-2 | line-2-0407-0674-s012986 | forward | revenue | 4 | pending |
| line-2 | line-2-0407-0674-s012986 | reverse | revenue | 4 | pending |
| line-2 | line-2-0329-0733-s015141 | reverse | revenue | 4 | pending |
| line-2 | line-2-0686-0464-s005140 | reverse | spare | 1 | pending |
| line-2 | line-2-0631-0506-s006746 | forward | spare | 1 | pending |
| line-2 | line-2-0631-0506-s006746 | reverse | spare | 1 | pending |
| line-2 | line-2-0520-0588-s009768 | forward | spare | 1 | pending |
| line-2 | line-2-0520-0588-s009768 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0885-0618-s000000 | forward | revenue | 4 | pending |
| line-3 | line-3-0745-0559-s003394 | forward | revenue | 4 | pending |
| line-3 | line-3-0745-0559-s003394 | reverse | revenue | 4 | pending |
| line-3 | line-3-0631-0506-s006209 | forward | revenue | 4 | pending |
| line-3 | line-3-0631-0506-s006209 | reverse | revenue | 4 | pending |
| line-3 | line-3-0501-0445-s009418 | forward | revenue | 4 | pending |
| line-3 | line-3-0501-0445-s009418 | reverse | revenue | 3 | pending |
| line-3 | line-3-0393-0395-s012074 | forward | revenue | 3 | pending |
| line-3 | line-3-0393-0395-s012074 | reverse | revenue | 3 | pending |
| line-3 | line-3-0357-0378-s012970 | reverse | revenue | 3 | pending |
| line-3 | line-3-0501-0445-s009418 | reverse | spare | 1 | pending |
| line-3 | line-3-0393-0395-s012074 | forward | spare | 1 | pending |
| line-3 | line-3-0393-0395-s012074 | reverse | spare | 1 | pending |
| line-3 | line-3-0357-0378-s012970 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**86 trainsets exceed the reference platform envelope**, requiring **5,117.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0392-0381-s015331 | 4 | 2 | 2 | 119.0 |
| line-1-0393-0395-s015043 | 8 | 4 | 4 | 238.0 |
| line-1-0398-0499-s012922 | 10 | 2 | 8 | 476.0 |
| line-1-0400-1089-s000000 | 5 | 2 | 3 | 178.5 |
| line-1-0407-0674-s009335 | 10 | 4 | 6 | 357.0 |
| line-1-0415-0834-s006069 | 10 | 2 | 8 | 476.0 |
| line-2-0329-0733-s015141 | 4 | 2 | 2 | 119.0 |
| line-2-0407-0674-s012986 | 8 | 4 | 4 | 238.0 |
| line-2-0520-0588-s009768 | 10 | 2 | 8 | 476.0 |
| line-2-0631-0506-s006746 | 10 | 4 | 6 | 357.0 |
| line-2-0686-0464-s005140 | 10 | 2 | 8 | 476.0 |
| line-2-0869-0325-s000000 | 5 | 2 | 3 | 178.5 |
| line-3-0357-0378-s012970 | 4 | 2 | 2 | 119.0 |
| line-3-0393-0395-s012074 | 8 | 4 | 4 | 238.0 |
| line-3-0501-0445-s009418 | 8 | 2 | 6 | 357.0 |
| line-3-0631-0506-s006209 | 8 | 4 | 4 | 238.0 |
| line-3-0745-0559-s003394 | 8 | 2 | 6 | 357.0 |
| line-3-0885-0618-s000000 | 4 | 2 | 2 | 119.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Tanzania/Morogoro/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
