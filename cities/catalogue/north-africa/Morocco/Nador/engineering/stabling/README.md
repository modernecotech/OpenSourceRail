# Station and depot overnight allocation

Plan: **30 trainsets at stations + 42 at depots = 72 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0440-0045-s009996 | line-1 | storage-at-existing-powered-service-point | 11 | 539.0 | 0 |
| line-2-0479-0445-s015368 | line-2 | declared-depot | 20 | 980.0 | 11 |
| line-3-0313-0282-s008983 | line-3 | storage-at-existing-powered-service-point | 11 | 539.0 | 0 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0328-0422-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0376-0367-s002017 | station | forward | revenue | 1 |
| line-1 | line-1-0376-0367-s002017 | station | reverse | revenue | 1 |
| line-1 | line-1-0392-0292-s004013 | station | forward | revenue | 1 |
| line-1 | line-1-0392-0292-s004013 | station | reverse | revenue | 1 |
| line-1 | line-1-0431-0209-s005996 | station | forward | revenue | 1 |
| line-1 | line-1-0431-0209-s005996 | station | reverse | revenue | 1 |
| line-1 | line-1-0440-0045-s009996 | station | reverse | revenue | 2 |
| line-2 | line-2-0034-0117-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0243-0279-s007024 | station | forward | revenue | 1 |
| line-2 | line-2-0243-0279-s007024 | station | reverse | revenue | 1 |
| line-2 | line-2-0327-0360-s010037 | station | forward | revenue | 1 |
| line-2 | line-2-0327-0360-s010037 | station | reverse | revenue | 1 |
| line-2 | line-2-0376-0367-s011599 | station | forward | revenue | 1 |
| line-2 | line-2-0376-0367-s011599 | station | reverse | revenue | 1 |
| line-2 | line-2-0429-0390-s013050 | station | forward | revenue | 1 |
| line-2 | line-2-0429-0390-s013050 | station | reverse | revenue | 1 |
| line-2 | line-2-0479-0445-s015368 | station | reverse | revenue | 2 |
| line-3 | line-3-0313-0282-s008983 | station | reverse | revenue | 2 |
| line-3 | line-3-0376-0367-s006546 | station | forward | revenue | 1 |
| line-3 | line-3-0376-0367-s006546 | station | reverse | revenue | 1 |
| line-3 | line-3-0493-0392-s003016 | station | forward | revenue | 1 |
| line-3 | line-3-0493-0392-s003016 | station | reverse | revenue | 1 |
| line-3 | line-3-0619-0416-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0440-0045-s009996 | depot | — | revenue | 9 |
| line-1 | line-1-0440-0045-s009996 | depot | — | spare | 1 |
| line-1 | line-1-0440-0045-s009996 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0479-0445-s015368 | depot | — | revenue | 17 |
| line-2 | line-2-0479-0445-s015368 | depot | — | spare | 2 |
| line-2 | line-2-0479-0445-s015368 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0313-0282-s008983 | depot | — | revenue | 9 |
| line-3 | line-3-0313-0282-s008983 | depot | — | spare | 1 |
| line-3 | line-3-0313-0282-s008983 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/nador-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **72 trainsets at 15 stations**; largest initial station queue **7**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **65 revenue, 4 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **30 positions**; **42 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **14 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0328-0422-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0376-0367-s002017 | forward | revenue | 3 | pending |
| line-1 | line-1-0376-0367-s002017 | reverse | revenue | 3 | pending |
| line-1 | line-1-0392-0292-s004013 | forward | revenue | 2 | pending |
| line-1 | line-1-0392-0292-s004013 | reverse | revenue | 2 | pending |
| line-1 | line-1-0431-0209-s005996 | forward | revenue | 2 | pending |
| line-1 | line-1-0431-0209-s005996 | reverse | revenue | 2 | pending |
| line-1 | line-1-0440-0045-s009996 | reverse | revenue | 2 | pending |
| line-1 | line-1-0392-0292-s004013 | forward | spare | 1 | pending |
| line-1 | line-1-0392-0292-s004013 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0034-0117-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0243-0279-s007024 | forward | revenue | 3 | pending |
| line-2 | line-2-0243-0279-s007024 | reverse | revenue | 3 | pending |
| line-2 | line-2-0327-0360-s010037 | forward | revenue | 3 | pending |
| line-2 | line-2-0327-0360-s010037 | reverse | revenue | 3 | pending |
| line-2 | line-2-0376-0367-s011599 | forward | revenue | 3 | pending |
| line-2 | line-2-0376-0367-s011599 | reverse | revenue | 3 | pending |
| line-2 | line-2-0429-0390-s013050 | forward | revenue | 3 | pending |
| line-2 | line-2-0429-0390-s013050 | reverse | revenue | 3 | pending |
| line-2 | line-2-0479-0445-s015368 | reverse | revenue | 2 | pending |
| line-2 | line-2-0479-0445-s015368 | reverse | spare | 1 | pending |
| line-2 | line-2-0034-0117-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0243-0279-s007024 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0619-0416-s000000 | forward | revenue | 3 | pending |
| line-3 | line-3-0493-0392-s003016 | forward | revenue | 3 | pending |
| line-3 | line-3-0493-0392-s003016 | reverse | revenue | 3 | pending |
| line-3 | line-3-0376-0367-s006546 | forward | revenue | 3 | pending |
| line-3 | line-3-0376-0367-s006546 | reverse | revenue | 3 | pending |
| line-3 | line-3-0313-0282-s008983 | reverse | revenue | 2 | pending |
| line-3 | line-3-0313-0282-s008983 | reverse | spare | 1 | pending |
| line-3 | line-3-0619-0416-s000000 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**36 trainsets exceed the reference platform envelope**, requiring **1,764.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0328-0422-s000000 | 3 | 2 | 1 | 49.0 |
| line-1-0376-0367-s002017 | 6 | 4 | 2 | 98.0 |
| line-1-0392-0292-s004013 | 6 | 2 | 4 | 196.0 |
| line-1-0431-0209-s005996 | 4 | 2 | 2 | 98.0 |
| line-1-0440-0045-s009996 | 2 | 2 | 0 | 0.0 |
| line-2-0034-0117-s000000 | 4 | 2 | 2 | 98.0 |
| line-2-0243-0279-s007024 | 7 | 2 | 5 | 245.0 |
| line-2-0327-0360-s010037 | 6 | 2 | 4 | 196.0 |
| line-2-0376-0367-s011599 | 6 | 4 | 2 | 98.0 |
| line-2-0429-0390-s013050 | 6 | 2 | 4 | 196.0 |
| line-2-0479-0445-s015368 | 3 | 2 | 1 | 49.0 |
| line-3-0313-0282-s008983 | 3 | 2 | 1 | 49.0 |
| line-3-0376-0367-s006546 | 6 | 4 | 2 | 98.0 |
| line-3-0493-0392-s003016 | 6 | 2 | 4 | 196.0 |
| line-3-0619-0416-s000000 | 4 | 2 | 2 | 98.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/north-africa/Morocco/Nador/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
