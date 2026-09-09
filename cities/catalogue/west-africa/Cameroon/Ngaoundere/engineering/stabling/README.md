# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **64 trainsets at 15 stations**; largest initial station queue **6**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0329-0548-s000000 | forward | 3 | pending |
| line-1 | line-1-0400-0539-s003024 | forward | 3 | pending |
| line-1 | line-1-0400-0539-s003024 | reverse | 3 | pending |
| line-1 | line-1-0513-0509-s006033 | forward | 2 | pending |
| line-1 | line-1-0513-0509-s006033 | reverse | 2 | pending |
| line-1 | line-1-0546-0550-s007434 | forward | 2 | pending |
| line-1 | line-1-0546-0550-s007434 | reverse | 2 | pending |
| line-1 | line-1-0602-0533-s009039 | forward | 2 | pending |
| line-1 | line-1-0602-0533-s009039 | reverse | 2 | pending |
| line-1 | line-1-0675-0553-s010949 | forward | 2 | pending |
| line-1 | line-1-0675-0553-s010949 | reverse | 2 | pending |
| line-1 | line-1-0717-0503-s012880 | reverse | 2 | pending |
| line-2 | line-2-0451-0387-s000000 | forward | 4 | pending |
| line-2 | line-2-0512-0450-s003010 | forward | 3 | pending |
| line-2 | line-2-0512-0450-s003010 | reverse | 3 | pending |
| line-2 | line-2-0546-0550-s005998 | forward | 3 | pending |
| line-2 | line-2-0546-0550-s005998 | reverse | 3 | pending |
| line-2 | line-2-0604-0647-s008649 | reverse | 3 | pending |
| line-3 | line-3-0591-0365-s000000 | forward | 3 | pending |
| line-3 | line-3-0591-0499-s003004 | forward | 3 | pending |
| line-3 | line-3-0591-0499-s003004 | reverse | 3 | pending |
| line-3 | line-3-0546-0550-s004530 | forward | 3 | pending |
| line-3 | line-3-0546-0550-s004530 | reverse | 3 | pending |
| line-3 | line-3-0428-0586-s007849 | reverse | 3 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-africa/Cameroon/Ngaoundere/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
