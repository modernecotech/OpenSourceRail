# Station and depot overnight allocation

Plan: **30 trainsets at stations + 62 at depots = 92 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at declared depots.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot station | Stabling positions required | Usable slot length m | Workshop bays |
|---|---:|---:|---:|
| line-3-0706-0540-s015716 | 62 | 3,038.0 | 14 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0146-0738-s014717 | station | reverse | revenue | 2 |
| line-1 | line-1-0293-0439-s006024 | station | forward | revenue | 1 |
| line-1 | line-1-0293-0439-s006024 | station | reverse | revenue | 1 |
| line-1 | line-1-0300-0511-s008190 | station | forward | revenue | 1 |
| line-1 | line-1-0300-0511-s008190 | station | reverse | revenue | 1 |
| line-1 | line-1-0353-0233-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0374-0377-s003627 | station | forward | revenue | 1 |
| line-1 | line-1-0374-0377-s003627 | station | reverse | revenue | 1 |
| line-2 | line-2-0374-0377-s009917 | station | forward | revenue | 1 |
| line-2 | line-2-0374-0377-s009917 | station | reverse | revenue | 1 |
| line-2 | line-2-0386-0502-s006944 | station | forward | revenue | 1 |
| line-2 | line-2-0386-0502-s006944 | station | reverse | revenue | 1 |
| line-2 | line-2-0420-0309-s012404 | station | forward | revenue | 1 |
| line-2 | line-2-0420-0309-s012404 | station | reverse | revenue | 1 |
| line-2 | line-2-0456-0751-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0459-0206-s014910 | station | reverse | revenue | 2 |
| line-3 | line-3-0281-0120-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0300-0310-s004563 | station | forward | revenue | 1 |
| line-3 | line-3-0300-0310-s004563 | station | reverse | revenue | 1 |
| line-3 | line-3-0374-0377-s007454 | station | forward | revenue | 1 |
| line-3 | line-3-0374-0377-s007454 | station | reverse | revenue | 1 |
| line-3 | line-3-0464-0441-s010028 | station | forward | revenue | 1 |
| line-3 | line-3-0464-0441-s010028 | station | reverse | revenue | 1 |
| line-3 | line-3-0706-0540-s015716 | station | reverse | revenue | 2 |
| line-1 | line-3-0706-0540-s015716 | depot | — | revenue | 18 |
| line-1 | line-3-0706-0540-s015716 | depot | — | spare | 2 |
| line-1 | line-3-0706-0540-s015716 | depot | — | cold_reserve | 1 |
| line-2 | line-3-0706-0540-s015716 | depot | — | revenue | 17 |
| line-2 | line-3-0706-0540-s015716 | depot | — | spare | 2 |
| line-2 | line-3-0706-0540-s015716 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0706-0540-s015716 | depot | — | revenue | 18 |
| line-3 | line-3-0706-0540-s015716 | depot | — | spare | 2 |
| line-3 | line-3-0706-0540-s015716 | depot | — | cold_reserve | 1 |

Interline access to the assigned depot must be detailed for: line-1 (21 trains), line-2 (20 trains).

## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **92 trainsets at 15 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **83 revenue, 6 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **30 positions**; **62 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **15 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0353-0233-s000000 | forward | revenue | 4 | pending |
| line-1 | line-1-0374-0377-s003627 | forward | revenue | 4 | pending |
| line-1 | line-1-0374-0377-s003627 | reverse | revenue | 4 | pending |
| line-1 | line-1-0293-0439-s006024 | forward | revenue | 4 | pending |
| line-1 | line-1-0293-0439-s006024 | reverse | revenue | 3 | pending |
| line-1 | line-1-0300-0511-s008190 | forward | revenue | 3 | pending |
| line-1 | line-1-0300-0511-s008190 | reverse | revenue | 3 | pending |
| line-1 | line-1-0146-0738-s014717 | reverse | revenue | 3 | pending |
| line-1 | line-1-0293-0439-s006024 | reverse | spare | 1 | pending |
| line-1 | line-1-0300-0511-s008190 | forward | spare | 1 | pending |
| line-1 | line-1-0300-0511-s008190 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0456-0751-s000000 | forward | revenue | 4 | pending |
| line-2 | line-2-0386-0502-s006944 | forward | revenue | 4 | pending |
| line-2 | line-2-0386-0502-s006944 | reverse | revenue | 4 | pending |
| line-2 | line-2-0374-0377-s009917 | forward | revenue | 3 | pending |
| line-2 | line-2-0374-0377-s009917 | reverse | revenue | 3 | pending |
| line-2 | line-2-0420-0309-s012404 | forward | revenue | 3 | pending |
| line-2 | line-2-0420-0309-s012404 | reverse | revenue | 3 | pending |
| line-2 | line-2-0459-0206-s014910 | reverse | revenue | 3 | pending |
| line-2 | line-2-0374-0377-s009917 | forward | spare | 1 | pending |
| line-2 | line-2-0374-0377-s009917 | reverse | spare | 1 | pending |
| line-2 | line-2-0420-0309-s012404 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0281-0120-s000000 | forward | revenue | 4 | pending |
| line-3 | line-3-0300-0310-s004563 | forward | revenue | 4 | pending |
| line-3 | line-3-0300-0310-s004563 | reverse | revenue | 4 | pending |
| line-3 | line-3-0374-0377-s007454 | forward | revenue | 4 | pending |
| line-3 | line-3-0374-0377-s007454 | reverse | revenue | 3 | pending |
| line-3 | line-3-0464-0441-s010028 | forward | revenue | 3 | pending |
| line-3 | line-3-0464-0441-s010028 | reverse | revenue | 3 | pending |
| line-3 | line-3-0706-0540-s015716 | reverse | revenue | 3 | pending |
| line-3 | line-3-0374-0377-s007454 | reverse | spare | 1 | pending |
| line-3 | line-3-0464-0441-s010028 | forward | spare | 1 | pending |
| line-3 | line-3-0464-0441-s010028 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**56 trainsets exceed the reference platform envelope**, requiring **2,744.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0146-0738-s014717 | 3 | 2 | 1 | 49.0 |
| line-1-0293-0439-s006024 | 8 | 2 | 6 | 294.0 |
| line-1-0300-0511-s008190 | 8 | 2 | 6 | 294.0 |
| line-1-0353-0233-s000000 | 4 | 2 | 2 | 98.0 |
| line-1-0374-0377-s003627 | 8 | 4 | 4 | 196.0 |
| line-2-0374-0377-s009917 | 8 | 4 | 4 | 196.0 |
| line-2-0386-0502-s006944 | 8 | 2 | 6 | 294.0 |
| line-2-0420-0309-s012404 | 7 | 2 | 5 | 245.0 |
| line-2-0456-0751-s000000 | 4 | 2 | 2 | 98.0 |
| line-2-0459-0206-s014910 | 3 | 2 | 1 | 49.0 |
| line-3-0281-0120-s000000 | 4 | 2 | 2 | 98.0 |
| line-3-0300-0310-s004563 | 8 | 2 | 6 | 294.0 |
| line-3-0374-0377-s007454 | 8 | 4 | 4 | 196.0 |
| line-3-0464-0441-s010028 | 8 | 2 | 6 | 294.0 |
| line-3-0706-0540-s015716 | 3 | 2 | 1 | 49.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Uganda/Lira/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
