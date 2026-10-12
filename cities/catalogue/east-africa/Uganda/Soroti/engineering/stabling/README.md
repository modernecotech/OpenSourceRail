# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **20 trainsets at stations + 10 at depots = 30 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0333-0345-s005758 | line-1 | declared-depot | 7 | 343.0 | 3 |
| line-2-0377-0360-s000000 | line-2 | declared-depot | 3 | 147.0 | 2 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0223-0404-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0333-0345-s005758 | station | reverse | revenue | 2 |
| line-1 | line-1-0349-0399-s003262 | station | forward | revenue | 1 |
| line-1 | line-1-0349-0399-s003262 | station | reverse | revenue | 1 |
| line-1 | line-1-0369-0382-s004353 | station | forward | revenue | 1 |
| line-1 | line-1-0369-0382-s004353 | station | reverse | revenue | 1 |
| line-1 | line-1-0372-0377-s004478 | station | forward | revenue | 1 |
| line-1 | line-1-0372-0377-s004478 | station | reverse | revenue | 1 |
| line-2 | line-2-0313-0432-s002102 | station | reverse | revenue | 2 |
| line-2 | line-2-0349-0399-s001109 | station | forward | revenue | 1 |
| line-2 | line-2-0349-0399-s001109 | station | reverse | revenue | 1 |
| line-2 | line-2-0369-0382-s000556 | station | forward | revenue | 1 |
| line-2 | line-2-0369-0382-s000556 | station | reverse | revenue | 1 |
| line-2 | line-2-0372-0377-s000431 | station | forward | revenue | 1 |
| line-2 | line-2-0372-0377-s000431 | station | reverse | revenue | 1 |
| line-2 | line-2-0377-0360-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0333-0345-s005758 | depot | — | revenue | 5 |
| line-1 | line-1-0333-0345-s005758 | depot | — | spare | 1 |
| line-1 | line-1-0333-0345-s005758 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0377-0360-s000000 | depot | — | revenue | 1 |
| line-2 | line-2-0377-0360-s000000 | depot | — | spare | 1 |
| line-2 | line-2-0377-0360-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/soroti-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **30 trainsets at 10 stations**; largest initial station queue **4**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **26 revenue, 2 spare, 2 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **20 positions**; **10 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **6 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0223-0404-s000000 | forward | revenue | 2 | pending |
| line-1 | line-1-0349-0399-s003262 | forward | revenue | 2 | pending |
| line-1 | line-1-0349-0399-s003262 | reverse | revenue | 2 | pending |
| line-1 | line-1-0369-0382-s004353 | forward | revenue | 2 | pending |
| line-1 | line-1-0369-0382-s004353 | reverse | revenue | 2 | pending |
| line-1 | line-1-0372-0377-s004478 | forward | revenue | 2 | pending |
| line-1 | line-1-0372-0377-s004478 | reverse | revenue | 2 | pending |
| line-1 | line-1-0333-0345-s005758 | reverse | revenue | 1 | pending |
| line-1 | line-1-0333-0345-s005758 | reverse | spare | 1 | pending |
| line-1 | line-1-0223-0404-s000000 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0377-0360-s000000 | forward | revenue | 2 | pending |
| line-2 | line-2-0372-0377-s000431 | forward | revenue | 2 | pending |
| line-2 | line-2-0372-0377-s000431 | reverse | revenue | 2 | pending |
| line-2 | line-2-0369-0382-s000556 | forward | revenue | 1 | pending |
| line-2 | line-2-0369-0382-s000556 | reverse | revenue | 1 | pending |
| line-2 | line-2-0349-0399-s001109 | forward | revenue | 1 | pending |
| line-2 | line-2-0349-0399-s001109 | reverse | revenue | 1 | pending |
| line-2 | line-2-0313-0432-s002102 | reverse | revenue | 1 | pending |
| line-2 | line-2-0369-0382-s000556 | forward | spare | 1 | pending |
| line-2 | line-2-0369-0382-s000556 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**1 trainsets exceed the reference platform envelope**, requiring **49.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0223-0404-s000000 | 3 | 2 | 1 | 49.0 |
| line-1-0333-0345-s005758 | 2 | 2 | 0 | 0.0 |
| line-1-0349-0399-s003262 | 4 | 4 | 0 | 0.0 |
| line-1-0369-0382-s004353 | 4 | 4 | 0 | 0.0 |
| line-1-0372-0377-s004478 | 4 | 4 | 0 | 0.0 |
| line-2-0313-0432-s002102 | 1 | 2 | 0 | 0.0 |
| line-2-0349-0399-s001109 | 2 | 4 | 0 | 0.0 |
| line-2-0369-0382-s000556 | 4 | 4 | 0 | 0.0 |
| line-2-0372-0377-s000431 | 4 | 4 | 0 | 0.0 |
| line-2-0377-0360-s000000 | 2 | 2 | 0 | 0.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Uganda/Soroti/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
