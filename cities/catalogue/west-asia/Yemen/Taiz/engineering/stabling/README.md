# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **94 trainsets at 17 stations**; largest initial station queue **10**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **84 revenue, 7 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0637-1074-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0637-0724-s007000 | forward | revenue | 3 | pending |
| line-1 | line-1-0637-0724-s007000 | reverse | revenue | 3 | pending |
| line-1 | line-1-0606-0590-s010007 | forward | revenue | 3 | pending |
| line-1 | line-1-0606-0590-s010007 | reverse | revenue | 3 | pending |
| line-1 | line-1-0556-0541-s012026 | forward | revenue | 3 | pending |
| line-1 | line-1-0556-0541-s012026 | reverse | revenue | 3 | pending |
| line-1 | line-1-0568-0466-s014071 | forward | revenue | 3 | pending |
| line-1 | line-1-0568-0466-s014071 | reverse | revenue | 3 | pending |
| line-1 | line-1-0536-0380-s016118 | forward | revenue | 3 | pending |
| line-1 | line-1-0536-0380-s016118 | reverse | revenue | 3 | pending |
| line-1 | line-1-0526-0296-s018154 | reverse | revenue | 3 | pending |
| line-1 | line-1-0637-1074-s000000 | forward | spare | 1 | pending |
| line-1 | line-1-0637-0724-s007000 | forward | spare | 1 | pending |
| line-1 | line-1-0637-0724-s007000 | reverse | spare | 1 | pending |
| line-1 | line-1-0606-0590-s010007 | forward | cold_reserve | 1 | pending |
| line-2 | line-2-0405-0445-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0487-0496-s002062 | forward | revenue | 2 | pending |
| line-2 | line-2-0487-0496-s002062 | reverse | revenue | 2 | pending |
| line-2 | line-2-0556-0541-s004124 | forward | revenue | 2 | pending |
| line-2 | line-2-0556-0541-s004124 | reverse | revenue | 2 | pending |
| line-2 | line-2-0530-0628-s006427 | forward | revenue | 2 | pending |
| line-2 | line-2-0530-0628-s006427 | reverse | revenue | 2 | pending |
| line-2 | line-2-0483-0717-s008749 | reverse | revenue | 2 | pending |
| line-2 | line-2-0487-0496-s002062 | forward | spare | 1 | pending |
| line-2 | line-2-0487-0496-s002062 | reverse | cold_reserve | 1 | pending |
| line-3 | line-3-1040-0281-s000000 | forward | revenue | 4 | pending |
| line-3 | line-3-0764-0463-s007028 | forward | revenue | 4 | pending |
| line-3 | line-3-0764-0463-s007028 | reverse | revenue | 4 | pending |
| line-3 | line-3-0653-0536-s010036 | forward | revenue | 4 | pending |
| line-3 | line-3-0653-0536-s010036 | reverse | revenue | 4 | pending |
| line-3 | line-3-0556-0541-s012228 | forward | revenue | 4 | pending |
| line-3 | line-3-0556-0541-s012228 | reverse | revenue | 4 | pending |
| line-3 | line-3-0425-0612-s015889 | reverse | revenue | 3 | pending |
| line-3 | line-3-0425-0612-s015889 | reverse | spare | 1 | pending |
| line-3 | line-3-1040-0281-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0764-0463-s007028 | forward | spare | 1 | pending |
| line-3 | line-3-0764-0463-s007028 | reverse | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**54 trainsets exceed the reference platform envelope**, requiring **3,213.0 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0526-0296-s018154 | 3 | 2 | 1 | 59.5 |
| line-1-0536-0380-s016118 | 6 | 2 | 4 | 238.0 |
| line-1-0556-0541-s012026 | 6 | 4 | 2 | 119.0 |
| line-1-0568-0466-s014071 | 6 | 2 | 4 | 238.0 |
| line-1-0606-0590-s010007 | 7 | 2 | 5 | 297.5 |
| line-1-0637-0724-s007000 | 8 | 2 | 6 | 357.0 |
| line-1-0637-1074-s000000 | 4 | 2 | 2 | 119.0 |
| line-2-0405-0445-s000000 | 3 | 2 | 1 | 59.5 |
| line-2-0483-0717-s008749 | 2 | 2 | 0 | 0.0 |
| line-2-0487-0496-s002062 | 6 | 2 | 4 | 238.0 |
| line-2-0530-0628-s006427 | 4 | 2 | 2 | 119.0 |
| line-2-0556-0541-s004124 | 4 | 4 | 0 | 0.0 |
| line-3-0425-0612-s015889 | 4 | 2 | 2 | 119.0 |
| line-3-0556-0541-s012228 | 8 | 4 | 4 | 238.0 |
| line-3-0653-0536-s010036 | 8 | 2 | 6 | 357.0 |
| line-3-0764-0463-s007028 | 10 | 2 | 8 | 476.0 |
| line-3-1040-0281-s000000 | 5 | 2 | 3 | 178.5 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Yemen/Taiz/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
