# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **143 trainsets at 26 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

Fleet roles: **128 revenue, 12 spare, 3 cold reserve**. Reserves are held out of routine dispatch.

| Line | Station | Direction | Role | Initial trainsets | Verified track slots |
|---|---|---|---|---:|---|
| line-1 | line-1-0623-0933-s000000 | forward | revenue | 3 | pending |
| line-1 | line-1-0553-0712-s006129 | forward | revenue | 3 | pending |
| line-1 | line-1-0553-0712-s006129 | reverse | revenue | 3 | pending |
| line-1 | line-1-0546-0616-s009139 | forward | revenue | 3 | pending |
| line-1 | line-1-0546-0616-s009139 | reverse | revenue | 3 | pending |
| line-1 | line-1-0549-0538-s011245 | forward | revenue | 3 | pending |
| line-1 | line-1-0549-0538-s011245 | reverse | revenue | 3 | pending |
| line-1 | line-1-0573-0455-s013215 | forward | revenue | 3 | pending |
| line-1 | line-1-0573-0455-s013215 | reverse | revenue | 3 | pending |
| line-1 | line-1-0561-0364-s015162 | forward | revenue | 3 | pending |
| line-1 | line-1-0561-0364-s015162 | reverse | revenue | 3 | pending |
| line-1 | line-1-0516-0245-s018213 | forward | revenue | 2 | pending |
| line-1 | line-1-0516-0245-s018213 | reverse | revenue | 2 | pending |
| line-1 | line-1-0502-0134-s020743 | forward | revenue | 2 | pending |
| line-1 | line-1-0502-0134-s020743 | reverse | revenue | 2 | pending |
| line-1 | line-1-0496-0025-s023254 | reverse | revenue | 2 | pending |
| line-1 | line-1-0516-0245-s018213 | forward | spare | 1 | pending |
| line-1 | line-1-0516-0245-s018213 | reverse | spare | 1 | pending |
| line-1 | line-1-0502-0134-s020743 | forward | spare | 1 | pending |
| line-1 | line-1-0502-0134-s020743 | reverse | spare | 1 | pending |
| line-1 | line-1-0496-0025-s023254 | reverse | cold_reserve | 1 | pending |
| line-2 | line-2-0024-0798-s000000 | forward | revenue | 3 | pending |
| line-2 | line-2-0310-0661-s007001 | forward | revenue | 3 | pending |
| line-2 | line-2-0310-0661-s007001 | reverse | revenue | 3 | pending |
| line-2 | line-2-0433-0595-s010008 | forward | revenue | 3 | pending |
| line-2 | line-2-0433-0595-s010008 | reverse | revenue | 3 | pending |
| line-2 | line-2-0492-0531-s011917 | forward | revenue | 3 | pending |
| line-2 | line-2-0492-0531-s011917 | reverse | revenue | 3 | pending |
| line-2 | line-2-0549-0538-s013842 | forward | revenue | 3 | pending |
| line-2 | line-2-0549-0538-s013842 | reverse | revenue | 3 | pending |
| line-2 | line-2-0616-0514-s016037 | forward | revenue | 3 | pending |
| line-2 | line-2-0616-0514-s016037 | reverse | revenue | 3 | pending |
| line-2 | line-2-0684-0417-s019058 | forward | revenue | 3 | pending |
| line-2 | line-2-0684-0417-s019058 | reverse | revenue | 2 | pending |
| line-2 | line-2-0768-0410-s021092 | forward | revenue | 2 | pending |
| line-2 | line-2-0768-0410-s021092 | reverse | revenue | 2 | pending |
| line-2 | line-2-0846-0375-s023122 | reverse | revenue | 2 | pending |
| line-2 | line-2-0684-0417-s019058 | reverse | spare | 1 | pending |
| line-2 | line-2-0768-0410-s021092 | forward | spare | 1 | pending |
| line-2 | line-2-0768-0410-s021092 | reverse | spare | 1 | pending |
| line-2 | line-2-0846-0375-s023122 | reverse | spare | 1 | pending |
| line-2 | line-2-0024-0798-s000000 | forward | cold_reserve | 1 | pending |
| line-3 | line-3-0463-0113-s000000 | forward | revenue | 3 | pending |
| line-3 | line-3-0467-0251-s003009 | forward | revenue | 3 | pending |
| line-3 | line-3-0467-0251-s003009 | reverse | revenue | 3 | pending |
| line-3 | line-3-0509-0366-s006009 | forward | revenue | 3 | pending |
| line-3 | line-3-0509-0366-s006009 | reverse | revenue | 3 | pending |
| line-3 | line-3-0504-0476-s009011 | forward | revenue | 3 | pending |
| line-3 | line-3-0504-0476-s009011 | reverse | revenue | 3 | pending |
| line-3 | line-3-0549-0538-s010961 | forward | revenue | 3 | pending |
| line-3 | line-3-0549-0538-s010961 | reverse | revenue | 3 | pending |
| line-3 | line-3-0488-0614-s013362 | forward | revenue | 3 | pending |
| line-3 | line-3-0488-0614-s013362 | reverse | revenue | 3 | pending |
| line-3 | line-3-0484-0723-s015758 | forward | revenue | 3 | pending |
| line-3 | line-3-0484-0723-s015758 | reverse | revenue | 3 | pending |
| line-3 | line-3-0450-0945-s021359 | reverse | revenue | 2 | pending |
| line-3 | line-3-0450-0945-s021359 | reverse | spare | 1 | pending |
| line-3 | line-3-0463-0113-s000000 | forward | spare | 1 | pending |
| line-3 | line-3-0467-0251-s003009 | forward | spare | 1 | pending |
| line-3 | line-3-0467-0251-s003009 | reverse | spare | 1 | pending |
| line-3 | line-3-0509-0366-s006009 | forward | cold_reserve | 1 | pending |

## Reference platform capacity comparison

**85 trainsets exceed the reference platform envelope**, requiring **5,057.5 m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.

| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |
|---|---:|---:|---:|---:|
| line-1-0496-0025-s023254 | 3 | 2 | 1 | 59.5 |
| line-1-0502-0134-s020743 | 6 | 2 | 4 | 238.0 |
| line-1-0516-0245-s018213 | 6 | 2 | 4 | 238.0 |
| line-1-0546-0616-s009139 | 6 | 2 | 4 | 238.0 |
| line-1-0549-0538-s011245 | 6 | 4 | 2 | 119.0 |
| line-1-0553-0712-s006129 | 6 | 2 | 4 | 238.0 |
| line-1-0561-0364-s015162 | 6 | 2 | 4 | 238.0 |
| line-1-0573-0455-s013215 | 6 | 2 | 4 | 238.0 |
| line-1-0623-0933-s000000 | 3 | 2 | 1 | 59.5 |
| line-2-0024-0798-s000000 | 4 | 2 | 2 | 119.0 |
| line-2-0310-0661-s007001 | 6 | 2 | 4 | 238.0 |
| line-2-0433-0595-s010008 | 6 | 2 | 4 | 238.0 |
| line-2-0492-0531-s011917 | 6 | 2 | 4 | 238.0 |
| line-2-0549-0538-s013842 | 6 | 4 | 2 | 119.0 |
| line-2-0616-0514-s016037 | 6 | 2 | 4 | 238.0 |
| line-2-0684-0417-s019058 | 6 | 2 | 4 | 238.0 |
| line-2-0768-0410-s021092 | 6 | 2 | 4 | 238.0 |
| line-2-0846-0375-s023122 | 3 | 2 | 1 | 59.5 |
| line-3-0450-0945-s021359 | 3 | 2 | 1 | 59.5 |
| line-3-0463-0113-s000000 | 4 | 2 | 2 | 119.0 |
| line-3-0467-0251-s003009 | 8 | 2 | 6 | 357.0 |
| line-3-0484-0723-s015758 | 6 | 2 | 4 | 238.0 |
| line-3-0488-0614-s013362 | 6 | 2 | 4 | 238.0 |
| line-3-0504-0476-s009011 | 6 | 2 | 4 | 238.0 |
| line-3-0509-0366-s006009 | 7 | 2 | 5 | 297.5 |
| line-3-0549-0538-s010961 | 6 | 4 | 2 | 119.0 |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Saudi Arabia/Al-Kharj/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
