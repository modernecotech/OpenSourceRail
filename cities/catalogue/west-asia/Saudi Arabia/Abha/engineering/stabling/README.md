# Station and depot overnight allocation

Plan: **40 trainsets at stations + 86 at depots = 126 total**. Two revenue trainsets per selected station support coordinated morning starts; the remaining revenue trains and reserves stay at declared depots.

Allocation check: **PASS**. Depot stabling positions are planning requirements, separate from workshop bays. Physical release remains open.

| Depot station | Stabling positions required | Usable slot length m | Workshop bays |
|---|---:|---:|---:|
| line-2-0558-0087-s023346 | 86 | 5,117.0 | 19 |

| Line | Location | Type | Direction | Role | Trainsets |
|---|---|---|---|---|---:|
| line-1 | line-1-0460-0278-s020919 | station | reverse | revenue | 2 |
| line-1 | line-1-0536-0441-s016027 | station | forward | revenue | 1 |
| line-1 | line-1-0536-0441-s016027 | station | reverse | revenue | 1 |
| line-1 | line-1-0558-1011-s000000 | station | forward | revenue | 2 |
| line-1 | line-1-0562-0562-s012256 | station | forward | revenue | 1 |
| line-1 | line-1-0562-0562-s012256 | station | reverse | revenue | 1 |
| line-1 | line-1-0576-0638-s010005 | station | forward | revenue | 1 |
| line-1 | line-1-0576-0638-s010005 | station | reverse | revenue | 1 |
| line-1 | line-1-0586-0490-s014149 | station | forward | revenue | 1 |
| line-1 | line-1-0586-0490-s014149 | station | reverse | revenue | 1 |
| line-1 | line-1-0618-0758-s007000 | station | forward | revenue | 1 |
| line-1 | line-1-0618-0758-s007000 | station | reverse | revenue | 1 |
| line-2 | line-2-0558-0087-s023346 | station | reverse | revenue | 2 |
| line-2 | line-2-0604-0297-s017075 | station | forward | revenue | 1 |
| line-2 | line-2-0604-0297-s017075 | station | reverse | revenue | 1 |
| line-2 | line-2-0696-0375-s014066 | station | forward | revenue | 1 |
| line-2 | line-2-0696-0375-s014066 | station | reverse | revenue | 1 |
| line-2 | line-2-0711-0550-s009419 | station | forward | revenue | 1 |
| line-2 | line-2-0711-0550-s009419 | station | reverse | revenue | 1 |
| line-2 | line-2-0730-0490-s011041 | station | forward | revenue | 1 |
| line-2 | line-2-0730-0490-s011041 | station | reverse | revenue | 1 |
| line-2 | line-2-0740-0671-s006414 | station | forward | revenue | 1 |
| line-2 | line-2-0740-0671-s006414 | station | reverse | revenue | 1 |
| line-2 | line-2-0771-0801-s003002 | station | forward | revenue | 1 |
| line-2 | line-2-0771-0801-s003002 | station | reverse | revenue | 1 |
| line-2 | line-2-0841-0891-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0374-0402-s014819 | station | reverse | revenue | 2 |
| line-3 | line-3-0406-0611-s010123 | station | forward | revenue | 1 |
| line-3 | line-3-0406-0611-s010123 | station | reverse | revenue | 1 |
| line-3 | line-3-0466-0862-s003499 | station | forward | revenue | 1 |
| line-3 | line-3-0466-0862-s003499 | station | reverse | revenue | 1 |
| line-3 | line-3-0476-1027-s000000 | station | forward | revenue | 2 |
| line-3 | line-3-0481-0718-s007017 | station | forward | revenue | 1 |
| line-3 | line-3-0481-0718-s007017 | station | reverse | revenue | 1 |
| line-1 | line-2-0558-0087-s023346 | depot | — | revenue | 27 |
| line-1 | line-2-0558-0087-s023346 | depot | — | spare | 4 |
| line-1 | line-2-0558-0087-s023346 | depot | — | cold_reserve | 1 |
| line-2 | line-2-0558-0087-s023346 | depot | — | revenue | 27 |
| line-2 | line-2-0558-0087-s023346 | depot | — | spare | 4 |
| line-2 | line-2-0558-0087-s023346 | depot | — | cold_reserve | 1 |
| line-3 | line-2-0558-0087-s023346 | depot | — | revenue | 19 |
| line-3 | line-2-0558-0087-s023346 | depot | — | spare | 2 |
| line-3 | line-2-0558-0087-s023346 | depot | — | cold_reserve | 1 |

Interline access to the assigned depot must be detailed for: line-1 (32 trains), line-3 (22 trains).

## Station-only native benchmark

The runnable scenario below tests station holding and restart behaviour. It does not yet execute the station/depot allocation above or depot yard movements. Its station overflow is a diagnostic result, not the overnight design allocation.

Operating allocation: **126 trainsets at 20 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **113 revenue, 10 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

Two-train station-capacity check: **FAIL**. Selected stations provide **40 positions**; **86 fleet positions** exceed station-only provision. The initial allocation exceeds the limit at **20 stations**. Four-berth reference platforms do not override the two-train provision.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0558-1011-s000000 | forward | revenue | 4 | pending |
| line-1 | line-1-0618-0758-s007000 | forward | revenue | 4 | pending |
| line-1 | line-1-0618-0758-s007000 | reverse | revenue | 4 | pending |
| line-1 | line-1-0576-0638-s010005 | forward | revenue | 4 | pending |
| line-1 | line-1-0576-0638-s010005 | reverse | revenue | 4 | pending |
| line-1 | line-1-0562-0562-s012256 | forward | revenue | 3 | pending |
| line-1 | line-1-0562-0562-s012256 | reverse | revenue | 3 | pending |
| line-1 | line-1-0586-0490-s014149 | forward | revenue | 3 | pending |
| line-1 | line-1-0586-0490-s014149 | reverse | revenue | 3 | pending |
| line-1 | line-1-0536-0441-s016027 | forward | revenue | 3 | pending |
| line-1 | line-1-0536-0441-s016027 | reverse | revenue | 3 | pending |
| line-1 | line-1-0460-0278-s020919 | reverse | revenue | 3 | pending |
| line-1 | line-1-0562-0562-s012256 | forward | spare | 1 | pending |
| line-1 | line-1-0562-0562-s012256 | reverse | spare | 1 | pending |
| line-1 | line-1-0586-0490-s014149 | forward | spare | 1 | pending |
| line-1 | line-1-0586-0490-s014149 | reverse | spare | 1 | pending |
| line-1 | line-1-0536-0441-s016027 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0841-0891-s000000 | forward | revenue | 4 | pending |
| line-2 | line-2-0771-0801-s003002 | forward | revenue | 3 | pending |
| line-2 | line-2-0771-0801-s003002 | reverse | revenue | 3 | pending |
| line-2 | line-2-0740-0671-s006414 | forward | revenue | 3 | pending |
| line-2 | line-2-0740-0671-s006414 | reverse | revenue | 3 | pending |
| line-2 | line-2-0711-0550-s009419 | forward | revenue | 3 | pending |
| line-2 | line-2-0711-0550-s009419 | reverse | revenue | 3 | pending |
| line-2 | line-2-0730-0490-s011041 | forward | revenue | 3 | pending |
| line-2 | line-2-0730-0490-s011041 | reverse | revenue | 3 | pending |
| line-2 | line-2-0696-0375-s014066 | forward | revenue | 3 | pending |
| line-2 | line-2-0696-0375-s014066 | reverse | revenue | 3 | pending |
| line-2 | line-2-0604-0297-s017075 | forward | revenue | 3 | pending |
| line-2 | line-2-0604-0297-s017075 | reverse | revenue | 3 | pending |
| line-2 | line-2-0558-0087-s023346 | reverse | revenue | 3 | pending |
| line-2 | line-2-0771-0801-s003002 | forward | spare | 1 | pending |
| line-2 | line-2-0771-0801-s003002 | reverse | spare | 1 | pending |
| line-2 | line-2-0740-0671-s006414 | forward | spare | 1 | pending |
| line-2 | line-2-0740-0671-s006414 | reverse | spare | 1 | pending |
| line-2 | line-2-0711-0550-s009419 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0476-1027-s000000 | forward | revenue | 4 | pending |
| line-3 | line-3-0466-0862-s003499 | forward | revenue | 4 | pending |
| line-3 | line-3-0466-0862-s003499 | reverse | revenue | 4 | pending |
| line-3 | line-3-0481-0718-s007017 | forward | revenue | 4 | pending |
| line-3 | line-3-0481-0718-s007017 | reverse | revenue | 4 | pending |
| line-3 | line-3-0406-0611-s010123 | forward | revenue | 3 | pending |
| line-3 | line-3-0406-0611-s010123 | reverse | revenue | 3 | pending |
| line-3 | line-3-0374-0402-s014819 | reverse | revenue | 3 | pending |
| line-3 | line-3-0406-0611-s010123 | forward | spare | 1 | pending |
| line-3 | line-3-0406-0611-s010123 | reverse | spare | 1 | pending |
| line-3 | line-3-0374-0402-s014819 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**86 trainsets exceed the reference platform envelope**, requiring **5,117.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0460-0278-s020919 | 3 | 2 | 1 | 59.5 |
| line-1-0536-0441-s016027 | 7 | 2 | 5 | 297.5 |
| line-1-0558-1011-s000000 | 4 | 2 | 2 | 119.0 |
| line-1-0562-0562-s012256 | 8 | 2 | 6 | 357.0 |
| line-1-0576-0638-s010005 | 8 | 2 | 6 | 357.0 |
| line-1-0586-0490-s014149 | 8 | 2 | 6 | 357.0 |
| line-1-0618-0758-s007000 | 8 | 2 | 6 | 357.0 |
| line-2-0558-0087-s023346 | 3 | 2 | 1 | 59.5 |
| line-2-0604-0297-s017075 | 6 | 2 | 4 | 238.0 |
| line-2-0696-0375-s014066 | 6 | 2 | 4 | 238.0 |
| line-2-0711-0550-s009419 | 7 | 2 | 5 | 297.5 |
| line-2-0730-0490-s011041 | 6 | 2 | 4 | 238.0 |
| line-2-0740-0671-s006414 | 8 | 2 | 6 | 357.0 |
| line-2-0771-0801-s003002 | 8 | 2 | 6 | 357.0 |
| line-2-0841-0891-s000000 | 4 | 2 | 2 | 119.0 |
| line-3-0374-0402-s014819 | 4 | 2 | 2 | 119.0 |
| line-3-0406-0611-s010123 | 8 | 2 | 6 | 357.0 |
| line-3-0466-0862-s003499 | 8 | 2 | 6 | 357.0 |
| line-3-0476-1027-s000000 | 4 | 2 | 2 | 119.0 |
| line-3-0481-0718-s007017 | 8 | 2 | 6 | 357.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Saudi Arabia/Abha/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
