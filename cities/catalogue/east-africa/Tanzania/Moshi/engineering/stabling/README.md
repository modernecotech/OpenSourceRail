# Station and depot overnight allocation

Plan: **28 trainsets at stations + 45 at depots = 73 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at declared depots.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot station | Stabling positions required | Usable slot length m | Workshop bays |
|---|---:|---:|---:|
| line-1-0486-0250-s015261 | 45 | 2,205.0 | 11 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0261-0745-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0367-0569-s004854 | station | forward | revenue | 1 |
| line-1 | line-1-0367-0569-s004854 | station | reverse | revenue | 1 |
| line-1 | line-1-0377-0380-s010443 | station | forward | revenue | 1 |
| line-1 | line-1-0377-0380-s010443 | station | reverse | revenue | 1 |
| line-1 | line-1-0403-0442-s007855 | station | forward | revenue | 1 |
| line-1 | line-1-0403-0442-s007855 | station | reverse | revenue | 1 |
| line-1 | line-1-0440-0322-s012848 | station | forward | revenue | 1 |
| line-1 | line-1-0440-0322-s012848 | station | reverse | revenue | 1 |
| line-1 | line-1-0486-0250-s015261 | station | reverse | revenue | 2 |
| line-2 | line-2-0154-0290-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0268-0362-s003099 | station | forward | revenue | 1 |
| line-2 | line-2-0268-0362-s003099 | station | reverse | revenue | 1 |
| line-2 | line-2-0377-0380-s005528 | station | forward | revenue | 1 |
| line-2 | line-2-0377-0380-s005528 | station | reverse | revenue | 1 |
| line-2 | line-2-0470-0406-s008091 | station | forward | revenue | 1 |
| line-2 | line-2-0470-0406-s008091 | station | reverse | revenue | 1 |
| line-2 | line-2-0574-0367-s011067 | station | reverse | revenue | 2 |
| line-3 | line-3-0286-0309-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0334-0635-s009753 | station | reverse | revenue | 2 |
| line-3 | line-3-0377-0380-s003422 | station | forward | revenue | 1 |
| line-3 | line-3-0377-0380-s003422 | station | reverse | revenue | 1 |
| line-1 | line-1-0486-0250-s015261 | depot | — | revenue | 16 |
| line-1 | line-1-0486-0250-s015261 | depot | — | spare | 2 |
| line-1 | line-1-0486-0250-s015261 | depot | — | cold_reserve | 1 |
| line-2 | line-1-0486-0250-s015261 | depot | — | revenue | 10 |
| line-2 | line-1-0486-0250-s015261 | depot | — | spare | 2 |
| line-2 | line-1-0486-0250-s015261 | depot | — | cold_reserve | 1 |
| line-3 | line-1-0486-0250-s015261 | depot | — | revenue | 11 |
| line-3 | line-1-0486-0250-s015261 | depot | — | spare | 1 |
| line-3 | line-1-0486-0250-s015261 | depot | — | cold_reserve | 1 |

Interline access to the assigned depot must be detailed for: line-2 (13 trains), line-3 (13 trains).

Native hybrid candidate unavailable: interline depot access is absent from the native track graph.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **73 trainsets at 14 stations**; largest initial station queue **10**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **65 revenue, 5 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **28 positions**; **45 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **13 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0261-0745-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0367-0569-s004854 | forward | revenue | 3 | pending |
| line-1 | line-1-0367-0569-s004854 | reverse | revenue | 3 | pending |
| line-1 | line-1-0403-0442-s007855 | forward | revenue | 3 | pending |
| line-1 | line-1-0403-0442-s007855 | reverse | revenue | 3 | pending |
| line-1 | line-1-0377-0380-s010443 | forward | revenue | 3 | pending |
| line-1 | line-1-0377-0380-s010443 | reverse | revenue | 3 | pending |
| line-1 | line-1-0440-0322-s012848 | forward | revenue | 3 | pending |
| line-1 | line-1-0440-0322-s012848 | reverse | revenue | 2 | pending |
| line-1 | line-1-0486-0250-s015261 | reverse | revenue | 2 | pending |
| line-1 | line-1-0440-0322-s012848 | reverse | spare | 1 | pending |
| line-1 | line-1-0486-0250-s015261 | reverse | spare | 1 | pending |
| line-1 | line-1-0261-0745-s000000 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0154-0290-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0268-0362-s003099 | forward | revenue | 3 | pending |
| line-2 | line-2-0268-0362-s003099 | reverse | revenue | 3 | pending |
| line-2 | line-2-0377-0380-s005528 | forward | revenue | 3 | pending |
| line-2 | line-2-0377-0380-s005528 | reverse | revenue | 2 | pending |
| line-2 | line-2-0470-0406-s008091 | forward | revenue | 2 | pending |
| line-2 | line-2-0470-0406-s008091 | reverse | revenue | 2 | pending |
| line-2 | line-2-0574-0367-s011067 | reverse | revenue | 2 | pending |
| line-2 | line-2-0377-0380-s005528 | reverse | spare | 1 | pending |
| line-2 | line-2-0470-0406-s008091 | forward | spare | 1 | pending |
| line-2 | line-2-0470-0406-s008091 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0286-0309-s000000 | forward | revenue | 5 | pending |
| line-3 | line-3-0377-0380-s003422 | forward | revenue | 4 | pending |
| line-3 | line-3-0377-0380-s003422 | reverse | revenue | 4 | pending |
| line-3 | line-3-0334-0635-s009753 | reverse | revenue | 4 | pending |
| line-3 | line-3-0377-0380-s003422 | forward | spare | 1 | pending |
| line-3 | line-3-0377-0380-s003422 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**39 trainsets exceed the reference platform envelope**, requiring **1,911.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0261-0745-s000000 | 4 | 2 | 2 | 98.0 |
| line-1-0367-0569-s004854 | 6 | 2 | 4 | 196.0 |
| line-1-0377-0380-s010443 | 6 | 4 | 2 | 98.0 |
| line-1-0403-0442-s007855 | 6 | 2 | 4 | 196.0 |
| line-1-0440-0322-s012848 | 6 | 2 | 4 | 196.0 |
| line-1-0486-0250-s015261 | 3 | 2 | 1 | 49.0 |
| line-2-0154-0290-s000000 | 3 | 2 | 1 | 49.0 |
| line-2-0268-0362-s003099 | 6 | 2 | 4 | 196.0 |
| line-2-0377-0380-s005528 | 6 | 4 | 2 | 98.0 |
| line-2-0470-0406-s008091 | 6 | 2 | 4 | 196.0 |
| line-2-0574-0367-s011067 | 2 | 2 | 0 | 0.0 |
| line-3-0286-0309-s000000 | 5 | 2 | 3 | 147.0 |
| line-3-0334-0635-s009753 | 4 | 2 | 2 | 98.0 |
| line-3-0377-0380-s003422 | 10 | 4 | 6 | 294.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Tanzania/Moshi/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
