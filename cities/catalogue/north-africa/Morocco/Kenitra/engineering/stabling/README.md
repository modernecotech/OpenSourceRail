# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **130 trainsets at 23 stations**; largest initial station queue **10**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0603-0820-s000000 | forward | 3 | pending |
| line-1 | line-1-0573-0701-s003022 | forward | 3 | pending |
| line-1 | line-1-0573-0701-s003022 | reverse | 3 | pending |
| line-1 | line-1-0555-0614-s005084 | forward | 3 | pending |
| line-1 | line-1-0555-0614-s005084 | reverse | 3 | pending |
| line-1 | line-1-0556-0544-s007028 | forward | 3 | pending |
| line-1 | line-1-0556-0544-s007028 | reverse | 3 | pending |
| line-1 | line-1-0503-0478-s009052 | forward | 2 | pending |
| line-1 | line-1-0503-0478-s009052 | reverse | 2 | pending |
| line-1 | line-1-0522-0385-s011103 | forward | 2 | pending |
| line-1 | line-1-0522-0385-s011103 | reverse | 2 | pending |
| line-1 | line-1-0492-0306-s013315 | forward | 2 | pending |
| line-1 | line-1-0492-0306-s013315 | reverse | 2 | pending |
| line-1 | line-1-0519-0208-s015515 | forward | 2 | pending |
| line-1 | line-1-0519-0208-s015515 | reverse | 2 | pending |
| line-1 | line-1-0516-0125-s017716 | reverse | 2 | pending |
| line-2 | line-2-0724-0790-s000000 | forward | 4 | pending |
| line-2 | line-2-0644-0685-s003012 | forward | 4 | pending |
| line-2 | line-2-0644-0685-s003012 | reverse | 4 | pending |
| line-2 | line-2-0588-0577-s006030 | forward | 4 | pending |
| line-2 | line-2-0588-0577-s006030 | reverse | 3 | pending |
| line-2 | line-2-0556-0544-s007896 | forward | 3 | pending |
| line-2 | line-2-0556-0544-s007896 | reverse | 3 | pending |
| line-2 | line-2-0619-0503-s009959 | forward | 3 | pending |
| line-2 | line-2-0619-0503-s009959 | reverse | 3 | pending |
| line-2 | line-2-0618-0407-s012037 | forward | 3 | pending |
| line-2 | line-2-0618-0407-s012037 | reverse | 3 | pending |
| line-2 | line-2-0598-0252-s016608 | forward | 3 | pending |
| line-2 | line-2-0598-0252-s016608 | reverse | 3 | pending |
| line-2 | line-2-0605-0103-s021169 | reverse | 3 | pending |
| line-3 | line-3-0754-0339-s000000 | forward | 5 | pending |
| line-3 | line-3-0686-0455-s003767 | forward | 5 | pending |
| line-3 | line-3-0686-0455-s003767 | reverse | 5 | pending |
| line-3 | line-3-0567-0494-s006777 | forward | 5 | pending |
| line-3 | line-3-0567-0494-s006777 | reverse | 5 | pending |
| line-3 | line-3-0556-0544-s008013 | forward | 4 | pending |
| line-3 | line-3-0556-0544-s008013 | reverse | 4 | pending |
| line-3 | line-3-0509-0586-s009778 | forward | 4 | pending |
| line-3 | line-3-0509-0586-s009778 | reverse | 4 | pending |
| line-3 | line-3-0249-1022-s021180 | reverse | 4 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/north-africa/Morocco/Kenitra/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
