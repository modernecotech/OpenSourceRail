# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **143 trainsets at 26 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0623-0933-s000000 | forward | 3 | pending |
| line-1 | line-1-0553-0712-s006129 | forward | 3 | pending |
| line-1 | line-1-0553-0712-s006129 | reverse | 3 | pending |
| line-1 | line-1-0546-0616-s009139 | forward | 3 | pending |
| line-1 | line-1-0546-0616-s009139 | reverse | 3 | pending |
| line-1 | line-1-0549-0538-s011245 | forward | 3 | pending |
| line-1 | line-1-0549-0538-s011245 | reverse | 3 | pending |
| line-1 | line-1-0573-0455-s013215 | forward | 3 | pending |
| line-1 | line-1-0573-0455-s013215 | reverse | 3 | pending |
| line-1 | line-1-0561-0364-s015162 | forward | 3 | pending |
| line-1 | line-1-0561-0364-s015162 | reverse | 3 | pending |
| line-1 | line-1-0516-0245-s018213 | forward | 3 | pending |
| line-1 | line-1-0516-0245-s018213 | reverse | 3 | pending |
| line-1 | line-1-0502-0134-s020743 | forward | 3 | pending |
| line-1 | line-1-0502-0134-s020743 | reverse | 3 | pending |
| line-1 | line-1-0496-0025-s023254 | reverse | 3 | pending |
| line-2 | line-2-0024-0798-s000000 | forward | 4 | pending |
| line-2 | line-2-0310-0661-s007001 | forward | 3 | pending |
| line-2 | line-2-0310-0661-s007001 | reverse | 3 | pending |
| line-2 | line-2-0433-0595-s010008 | forward | 3 | pending |
| line-2 | line-2-0433-0595-s010008 | reverse | 3 | pending |
| line-2 | line-2-0492-0531-s011917 | forward | 3 | pending |
| line-2 | line-2-0492-0531-s011917 | reverse | 3 | pending |
| line-2 | line-2-0549-0538-s013842 | forward | 3 | pending |
| line-2 | line-2-0549-0538-s013842 | reverse | 3 | pending |
| line-2 | line-2-0616-0514-s016037 | forward | 3 | pending |
| line-2 | line-2-0616-0514-s016037 | reverse | 3 | pending |
| line-2 | line-2-0684-0417-s019058 | forward | 3 | pending |
| line-2 | line-2-0684-0417-s019058 | reverse | 3 | pending |
| line-2 | line-2-0768-0410-s021092 | forward | 3 | pending |
| line-2 | line-2-0768-0410-s021092 | reverse | 3 | pending |
| line-2 | line-2-0846-0375-s023122 | reverse | 3 | pending |
| line-3 | line-3-0463-0113-s000000 | forward | 4 | pending |
| line-3 | line-3-0467-0251-s003009 | forward | 4 | pending |
| line-3 | line-3-0467-0251-s003009 | reverse | 4 | pending |
| line-3 | line-3-0509-0366-s006009 | forward | 4 | pending |
| line-3 | line-3-0509-0366-s006009 | reverse | 3 | pending |
| line-3 | line-3-0504-0476-s009011 | forward | 3 | pending |
| line-3 | line-3-0504-0476-s009011 | reverse | 3 | pending |
| line-3 | line-3-0549-0538-s010961 | forward | 3 | pending |
| line-3 | line-3-0549-0538-s010961 | reverse | 3 | pending |
| line-3 | line-3-0488-0614-s013362 | forward | 3 | pending |
| line-3 | line-3-0488-0614-s013362 | reverse | 3 | pending |
| line-3 | line-3-0484-0723-s015758 | forward | 3 | pending |
| line-3 | line-3-0484-0723-s015758 | reverse | 3 | pending |
| line-3 | line-3-0450-0945-s021359 | reverse | 3 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Saudi Arabia/Al-Kharj/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
