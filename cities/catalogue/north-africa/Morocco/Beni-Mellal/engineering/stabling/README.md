# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **40 trainsets at stations + 42 at depots = 82 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0164-0517-s000000 | line-1 | declared-depot | 9 | 441.0 | 3 |
| line-2-0027-0511-s009671 | line-2 | declared-depot | 11 | 539.0 | 3 |
| line-3-0421-0361-s000000 | line-3 | declared-depot | 11 | 539.0 | 3 |
| line-4-0298-0415-s000000 | line-4 | declared-depot | 5 | 245.0 | 2 |
| line-5-0337-0316-s000000 | line-5 | declared-depot | 6 | 294.0 | 2 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0164-0517-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0248-0453-s002386 | station | forward | revenue | 1 |
| line-1 | line-1-0248-0453-s002386 | station | reverse | revenue | 1 |
| line-1 | line-1-0298-0415-s003783 | station | forward | revenue | 1 |
| line-1 | line-1-0298-0415-s003783 | station | reverse | revenue | 1 |
| line-1 | line-1-0340-0382-s004955 | station | forward | revenue | 1 |
| line-1 | line-1-0340-0382-s004955 | station | reverse | revenue | 1 |
| line-1 | line-1-0419-0322-s007207 | station | forward | revenue | 1 |
| line-1 | line-1-0419-0322-s007207 | station | reverse | revenue | 1 |
| line-1 | line-1-0466-0286-s008528 | station | reverse | revenue | 2 |
| line-2 | line-2-0027-0511-s009671 | station | reverse | revenue | 2 |
| line-2 | line-2-0208-0416-s004935 | station | forward | revenue | 1 |
| line-2 | line-2-0208-0416-s004935 | station | reverse | revenue | 1 |
| line-2 | line-2-0272-0366-s003123 | station | forward | revenue | 1 |
| line-2 | line-2-0272-0366-s003123 | station | reverse | revenue | 1 |
| line-2 | line-2-0337-0316-s001292 | station | forward | revenue | 1 |
| line-2 | line-2-0337-0316-s001292 | station | reverse | revenue | 1 |
| line-2 | line-2-0383-0281-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0045-0480-s008825 | station | reverse | revenue | 2 |
| line-3 | line-3-0208-0416-s004716 | station | forward | revenue | 1 |
| line-3 | line-3-0208-0416-s004716 | station | reverse | revenue | 1 |
| line-3 | line-3-0340-0382-s001794 | station | forward | revenue | 1 |
| line-3 | line-3-0340-0382-s001794 | station | reverse | revenue | 1 |
| line-3 | line-3-0421-0361-s000000 | station | forward | revenue | 2 |
| line-4 | line-4-0298-0415-s000000 | station | forward | revenue | 2 |
| line-4 | line-4-0406-0431-s002569 | station | reverse | revenue | 2 |
| line-5 | line-5-0337-0316-s000000 | station | forward | revenue | 2 |
| line-5 | line-5-0379-0230-s002085 | station | forward | revenue | 1 |
| line-5 | line-5-0379-0230-s002085 | station | reverse | revenue | 1 |
| line-5 | line-5-0465-0195-s004094 | station | reverse | revenue | 2 |
| line-1 | line-1-0164-0517-s000000 | depot | — | revenue | 7 |
| line-1 | line-1-0164-0517-s000000 | depot | — | spare | 1 |
| line-1 | line-1-0164-0517-s000000 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0027-0511-s009671 | depot | — | revenue | 9 |
| line-2 | line-2-0027-0511-s009671 | depot | — | spare | 1 |
| line-2 | line-2-0027-0511-s009671 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0421-0361-s000000 | depot | — | revenue | 9 |
| line-3 | line-3-0421-0361-s000000 | depot | — | spare | 1 |
| line-3 | line-3-0421-0361-s000000 | depot | — | cold_reserve | 1 |
| line-4 | line-4-0298-0415-s000000 | depot | — | revenue | 3 |
| line-4 | line-4-0298-0415-s000000 | depot | — | spare | 1 |
| line-4 | line-4-0298-0415-s000000 | depot | — | cold_reserve | 1 |
| line-5 | line-5-0337-0316-s000000 | depot | — | revenue | 4 |
| line-5 | line-5-0337-0316-s000000 | depot | — | spare | 1 |
| line-5 | line-5-0337-0316-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/beni-mellal-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **82 trainsets at 20 stations**; largest initial station queue **6**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **72 revenue, 5 spare, 5 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **40 positions**; **42 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **18 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0164-0517-s000000 | forward | revenue | 2 | pending |
| line-1 | line-1-0248-0453-s002386 | forward | revenue | 2 | pending |
| line-1 | line-1-0248-0453-s002386 | reverse | revenue | 2 | pending |
| line-1 | line-1-0298-0415-s003783 | forward | revenue | 2 | pending |
| line-1 | line-1-0298-0415-s003783 | reverse | revenue | 2 | pending |
| line-1 | line-1-0340-0382-s004955 | forward | revenue | 2 | pending |
| line-1 | line-1-0340-0382-s004955 | reverse | revenue | 2 | pending |
| line-1 | line-1-0419-0322-s007207 | forward | revenue | 2 | pending |
| line-1 | line-1-0419-0322-s007207 | reverse | revenue | 2 | pending |
| line-1 | line-1-0466-0286-s008528 | reverse | revenue | 1 | pending |
| line-1 | line-1-0466-0286-s008528 | reverse | spare | 1 | pending |
| line-1 | line-1-0164-0517-s000000 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0383-0281-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0337-0316-s001292 | forward | revenue | 3 | pending |
| line-2 | line-2-0337-0316-s001292 | reverse | revenue | 3 | pending |
| line-2 | line-2-0272-0366-s003123 | forward | revenue | 2 | pending |
| line-2 | line-2-0272-0366-s003123 | reverse | revenue | 2 | pending |
| line-2 | line-2-0208-0416-s004935 | forward | revenue | 2 | pending |
| line-2 | line-2-0208-0416-s004935 | reverse | revenue | 2 | pending |
| line-2 | line-2-0027-0511-s009671 | reverse | revenue | 2 | pending |
| line-2 | line-2-0272-0366-s003123 | forward | spare | 1 | pending |
| line-2 | line-2-0272-0366-s003123 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-0421-0361-s000000 | forward | revenue | 3 | pending |
| line-3 | line-3-0340-0382-s001794 | forward | revenue | 3 | pending |
| line-3 | line-3-0340-0382-s001794 | reverse | revenue | 3 | pending |
| line-3 | line-3-0208-0416-s004716 | forward | revenue | 3 | pending |
| line-3 | line-3-0208-0416-s004716 | reverse | revenue | 3 | pending |
| line-3 | line-3-0045-0480-s008825 | reverse | revenue | 2 | pending |
| line-3 | line-3-0045-0480-s008825 | reverse | spare | 1 | pending |
| line-3 | line-3-0421-0361-s000000 | forward | cold_reserve | 1 | pending |
| line-4 | line-4-0298-0415-s000000 | forward | revenue | 4 | pending |
| line-4 | line-4-0406-0431-s002569 | reverse | revenue | 3 | pending |
| line-4 | line-4-0406-0431-s002569 | reverse | spare | 1 | pending |
| line-4 | line-4-0298-0415-s000000 | forward | cold_reserve | 1 | pending |
| line-5 | line-5-0337-0316-s000000 | forward | revenue | 3 | pending |
| line-5 | line-5-0379-0230-s002085 | forward | revenue | 3 | pending |
| line-5 | line-5-0379-0230-s002085 | reverse | revenue | 2 | pending |
| line-5 | line-5-0465-0195-s004094 | reverse | revenue | 2 | pending |
| line-5 | line-5-0379-0230-s002085 | reverse | spare | 1 | pending |
| line-5 | line-5-0465-0195-s004094 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**30 trainsets exceed the reference platform envelope**, requiring **1,470.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0164-0517-s000000 | 3 | 2 | 1 | 49.0 |
| line-1-0248-0453-s002386 | 4 | 2 | 2 | 98.0 |
| line-1-0298-0415-s003783 | 4 | 4 | 0 | 0.0 |
| line-1-0340-0382-s004955 | 4 | 4 | 0 | 0.0 |
| line-1-0419-0322-s007207 | 4 | 2 | 2 | 98.0 |
| line-1-0466-0286-s008528 | 2 | 2 | 0 | 0.0 |
| line-2-0027-0511-s009671 | 2 | 2 | 0 | 0.0 |
| line-2-0208-0416-s004935 | 4 | 4 | 0 | 0.0 |
| line-2-0272-0366-s003123 | 6 | 2 | 4 | 196.0 |
| line-2-0337-0316-s001292 | 6 | 4 | 2 | 98.0 |
| line-2-0383-0281-s000000 | 3 | 2 | 1 | 49.0 |
| line-3-0045-0480-s008825 | 3 | 2 | 1 | 49.0 |
| line-3-0208-0416-s004716 | 6 | 4 | 2 | 98.0 |
| line-3-0340-0382-s001794 | 6 | 4 | 2 | 98.0 |
| line-3-0421-0361-s000000 | 4 | 2 | 2 | 98.0 |
| line-4-0298-0415-s000000 | 5 | 2 | 3 | 147.0 |
| line-4-0406-0431-s002569 | 4 | 2 | 2 | 98.0 |
| line-5-0337-0316-s000000 | 3 | 2 | 1 | 49.0 |
| line-5-0379-0230-s002085 | 6 | 2 | 4 | 196.0 |
| line-5-0465-0195-s004094 | 3 | 2 | 1 | 49.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/north-africa/Morocco/Beni-Mellal/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
