# Station and depot overnight allocation

The adopted full-fleet line-depot requirement is in [line-depot scope](../line-depots/README.md). The hybrid allocation below is a retained operating diagnostic; station berths do not reduce the adopted depot storage requirement.

Plan: **42 trainsets at stations + 182 at depots = 224 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at storage on their own line.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot/storage station | Line | Site basis | Stabling positions required | Usable slot length m | Workshop bays |
|---|---|---|---:|---:|---:|
| line-1-0215-0272-s026362 | line-1 | declared-depot | 62 | 3,689.0 | 11 |
| line-2-0980-0761-s000000 | line-2 | declared-depot | 60 | 3,570.0 | 11 |
| line-3-0198-0413-s000000 | line-3 | declared-depot | 60 | 3,570.0 | 10 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0215-0272-s026362 | station | reverse | revenue | 2 |
| line-1 | line-1-0434-0460-s019897 | station | forward | revenue | 1 |
| line-1 | line-1-0434-0460-s019897 | station | reverse | revenue | 1 |
| line-1 | line-1-0547-0554-s016589 | station | forward | revenue | 1 |
| line-1 | line-1-0547-0554-s016589 | station | reverse | revenue | 1 |
| line-1 | line-1-0591-0592-s015253 | station | forward | revenue | 1 |
| line-1 | line-1-0591-0592-s015253 | station | reverse | revenue | 1 |
| line-1 | line-1-0694-0679-s012227 | station | forward | revenue | 1 |
| line-1 | line-1-0694-0679-s012227 | station | reverse | revenue | 1 |
| line-1 | line-1-0798-0767-s009148 | station | forward | revenue | 1 |
| line-1 | line-1-0798-0767-s009148 | station | reverse | revenue | 1 |
| line-1 | line-1-0902-0838-s006139 | station | forward | revenue | 1 |
| line-1 | line-1-0902-0838-s006139 | station | reverse | revenue | 1 |
| line-1 | line-1-1093-0994-s000000 | station | forward | revenue | 2 |
| line-2 | line-2-0284-0038-s023420 | station | reverse | revenue | 2 |
| line-2 | line-2-0512-0291-s016108 | station | forward | revenue | 1 |
| line-2 | line-2-0512-0291-s016108 | station | reverse | revenue | 1 |
| line-2 | line-2-0580-0375-s013688 | station | forward | revenue | 1 |
| line-2 | line-2-0580-0375-s013688 | station | reverse | revenue | 1 |
| line-2 | line-2-0665-0478-s010678 | station | forward | revenue | 1 |
| line-2 | line-2-0665-0478-s010678 | station | reverse | revenue | 1 |
| line-2 | line-2-0749-0581-s007676 | station | forward | revenue | 1 |
| line-2 | line-2-0749-0581-s007676 | station | reverse | revenue | 1 |
| line-2 | line-2-0834-0685-s004658 | station | forward | revenue | 1 |
| line-2 | line-2-0834-0685-s004658 | station | reverse | revenue | 1 |
| line-2 | line-2-0980-0761-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0198-0413-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0316-0479-s003024 | station | forward | revenue | 1 |
| line-3 | line-3-0316-0479-s003024 | station | reverse | revenue | 1 |
| line-3 | line-3-0424-0558-s006049 | station | forward | revenue | 1 |
| line-3 | line-3-0424-0558-s006049 | station | reverse | revenue | 1 |
| line-3 | line-3-0532-0638-s009071 | station | forward | revenue | 1 |
| line-3 | line-3-0532-0638-s009071 | station | reverse | revenue | 1 |
| line-3 | line-3-0641-0718-s012078 | station | forward | revenue | 1 |
| line-3 | line-3-0641-0718-s012078 | station | reverse | revenue | 1 |
| line-3 | line-3-1002-1014-s023891 | station | reverse | revenue | 2 |
| line-1 | line-1-0215-0272-s026362 | depot | — | revenue | 54 |
| line-1 | line-1-0215-0272-s026362 | depot | — | spare | 7 |
| line-1 | line-1-0215-0272-s026362 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0980-0761-s000000 | depot | — | revenue | 53 |
| line-2 | line-2-0980-0761-s000000 | depot | — | spare | 6 |
| line-2 | line-2-0980-0761-s000000 | depot | — | cold_reserve | 1 |
| line-3 | line-3-0198-0413-s000000 | depot | — | revenue | 53 |
| line-3 | line-3-0198-0413-s000000 | depot | — | spare | 6 |
| line-3 | line-3-0198-0413-s000000 | depot | — | cold_reserve | 1 |

Native hybrid candidate: `build/engineering/stabling/khamis-mushait-hybrid.toml`; generation only, operating validation pending.


## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **224 trainsets at 21 stations**; largest initial station queue **15**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **202 revenue, 19 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **42 positions**; **182 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **21 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-1093-0994-s000000 | forward | revenue | 5 | pending |
| line-1 | line-1-0902-0838-s006139 | forward | revenue | 5 | pending |
| line-1 | line-1-0902-0838-s006139 | reverse | revenue | 5 | pending |
| line-1 | line-1-0798-0767-s009148 | forward | revenue | 5 | pending |
| line-1 | line-1-0798-0767-s009148 | reverse | revenue | 5 | pending |
| line-1 | line-1-0694-0679-s012227 | forward | revenue | 5 | pending |
| line-1 | line-1-0694-0679-s012227 | reverse | revenue | 5 | pending |
| line-1 | line-1-0591-0592-s015253 | forward | revenue | 5 | pending |
| line-1 | line-1-0591-0592-s015253 | reverse | revenue | 5 | pending |
| line-1 | line-1-0547-0554-s016589 | forward | revenue | 5 | pending |
| line-1 | line-1-0547-0554-s016589 | reverse | revenue | 5 | pending |
| line-1 | line-1-0434-0460-s019897 | forward | revenue | 5 | pending |
| line-1 | line-1-0434-0460-s019897 | reverse | revenue | 5 | pending |
| line-1 | line-1-0215-0272-s026362 | reverse | revenue | 5 | pending |
| line-1 | line-1-1093-0994-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0902-0838-s006139 | forward | spare | 1 | pending |
| line-1 | line-1-0902-0838-s006139 | reverse | spare | 1 | pending |
| line-1 | line-1-0798-0767-s009148 | forward | spare | 1 | pending |
| line-1 | line-1-0798-0767-s009148 | reverse | spare | 1 | pending |
| line-1 | line-1-0694-0679-s012227 | forward | spare | 1 | pending |
| line-1 | line-1-0694-0679-s012227 | reverse | spare | 1 | pending |
| line-1 | line-1-0591-0592-s015253 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0980-0761-s000000 | forward | revenue | 6 | pending |
| line-2 | line-2-0834-0685-s004658 | forward | revenue | 6 | pending |
| line-2 | line-2-0834-0685-s004658 | reverse | revenue | 6 | pending |
| line-2 | line-2-0749-0581-s007676 | forward | revenue | 6 | pending |
| line-2 | line-2-0749-0581-s007676 | reverse | revenue | 6 | pending |
| line-2 | line-2-0665-0478-s010678 | forward | revenue | 6 | pending |
| line-2 | line-2-0665-0478-s010678 | reverse | revenue | 6 | pending |
| line-2 | line-2-0580-0375-s013688 | forward | revenue | 5 | pending |
| line-2 | line-2-0580-0375-s013688 | reverse | revenue | 5 | pending |
| line-2 | line-2-0512-0291-s016108 | forward | revenue | 5 | pending |
| line-2 | line-2-0512-0291-s016108 | reverse | revenue | 5 | pending |
| line-2 | line-2-0284-0038-s023420 | reverse | revenue | 5 | pending |
| line-2 | line-2-0580-0375-s013688 | forward | spare | 1 | pending |
| line-2 | line-2-0580-0375-s013688 | reverse | spare | 1 | pending |
| line-2 | line-2-0512-0291-s016108 | forward | spare | 1 | pending |
| line-2 | line-2-0512-0291-s016108 | reverse | spare | 1 | pending |
| line-2 | line-2-0284-0038-s023420 | reverse | spare | 1 | pending |
| line-2 | line-2-0980-0761-s000000 | forward | spare | 1 | pending |
| line-2 | line-2-0834-0685-s004658 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0198-0413-s000000 | forward | revenue | 7 | pending |
| line-3 | line-3-0316-0479-s003024 | forward | revenue | 7 | pending |
| line-3 | line-3-0316-0479-s003024 | reverse | revenue | 7 | pending |
| line-3 | line-3-0424-0558-s006049 | forward | revenue | 7 | pending |
| line-3 | line-3-0424-0558-s006049 | reverse | revenue | 7 | pending |
| line-3 | line-3-0532-0638-s009071 | forward | revenue | 6 | pending |
| line-3 | line-3-0532-0638-s009071 | reverse | revenue | 6 | pending |
| line-3 | line-3-0641-0718-s012078 | forward | revenue | 6 | pending |
| line-3 | line-3-0641-0718-s012078 | reverse | revenue | 6 | pending |
| line-3 | line-3-1002-1014-s023891 | reverse | revenue | 6 | pending |
| line-3 | line-3-0532-0638-s009071 | forward | spare | 1 | pending |
| line-3 | line-3-0532-0638-s009071 | reverse | spare | 1 | pending |
| line-3 | line-3-0641-0718-s012078 | forward | spare | 1 | pending |
| line-3 | line-3-0641-0718-s012078 | reverse | spare | 1 | pending |
| line-3 | line-3-1002-1014-s023891 | reverse | spare | 1 | pending |
| line-3 | line-3-0198-0413-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0316-0479-s003024 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**182 trainsets exceed the reference platform envelope**, requiring **10,829.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0215-0272-s026362 | 5 | 2 | 3 | 178.5 |
| line-1-0434-0460-s019897 | 10 | 2 | 8 | 476.0 |
| line-1-0547-0554-s016589 | 10 | 2 | 8 | 476.0 |
| line-1-0591-0592-s015253 | 11 | 2 | 9 | 535.5 |
| line-1-0694-0679-s012227 | 12 | 2 | 10 | 595.0 |
| line-1-0798-0767-s009148 | 12 | 2 | 10 | 595.0 |
| line-1-0902-0838-s006139 | 12 | 2 | 10 | 595.0 |
| line-1-1093-0994-s000000 | 6 | 2 | 4 | 238.0 |
| line-2-0284-0038-s023420 | 6 | 2 | 4 | 238.0 |
| line-2-0512-0291-s016108 | 12 | 2 | 10 | 595.0 |
| line-2-0580-0375-s013688 | 12 | 2 | 10 | 595.0 |
| line-2-0665-0478-s010678 | 12 | 2 | 10 | 595.0 |
| line-2-0749-0581-s007676 | 12 | 2 | 10 | 595.0 |
| line-2-0834-0685-s004658 | 13 | 2 | 11 | 654.5 |
| line-2-0980-0761-s000000 | 7 | 2 | 5 | 297.5 |
| line-3-0198-0413-s000000 | 8 | 2 | 6 | 357.0 |
| line-3-0316-0479-s003024 | 15 | 2 | 13 | 773.5 |
| line-3-0424-0558-s006049 | 14 | 2 | 12 | 714.0 |
| line-3-0532-0638-s009071 | 14 | 2 | 12 | 714.0 |
| line-3-0641-0718-s012078 | 14 | 2 | 12 | 714.0 |
| line-3-1002-1014-s023891 | 7 | 2 | 5 | 297.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.
- Distributed/hybrid candidate outputs do not replace the full-fleet depot requirement or qualify actual yard, access, charging or launch capacity.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Saudi Arabia/Khamis-Mushait/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
