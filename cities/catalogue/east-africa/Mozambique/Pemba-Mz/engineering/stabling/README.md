# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **69 trainsets at 14 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0316-0192-s000000 | forward | 3 | pending |
| line-1 | line-1-0329-0290-s003025 | forward | 3 | pending |
| line-1 | line-1-0329-0290-s003025 | reverse | 3 | pending |
| line-1 | line-1-0378-0382-s005450 | forward | 3 | pending |
| line-1 | line-1-0378-0382-s005450 | reverse | 3 | pending |
| line-1 | line-1-0414-0486-s008304 | forward | 3 | pending |
| line-1 | line-1-0414-0486-s008304 | reverse | 3 | pending |
| line-1 | line-1-0349-0574-s011167 | forward | 3 | pending |
| line-1 | line-1-0349-0574-s011167 | reverse | 3 | pending |
| line-1 | line-1-0354-0699-s014020 | reverse | 2 | pending |
| line-2 | line-2-0634-0455-s000000 | forward | 3 | pending |
| line-2 | line-2-0510-0460-s003013 | forward | 3 | pending |
| line-2 | line-2-0510-0460-s003013 | reverse | 3 | pending |
| line-2 | line-2-0440-0520-s005404 | forward | 3 | pending |
| line-2 | line-2-0440-0520-s005404 | reverse | 3 | pending |
| line-2 | line-2-0365-0597-s007781 | reverse | 2 | pending |
| line-3 | line-3-0353-0455-s000000 | forward | 4 | pending |
| line-3 | line-3-0378-0382-s002377 | forward | 4 | pending |
| line-3 | line-3-0378-0382-s002377 | reverse | 4 | pending |
| line-3 | line-3-0483-0436-s005131 | forward | 4 | pending |
| line-3 | line-3-0483-0436-s005131 | reverse | 4 | pending |
| line-3 | line-3-0645-0634-s010614 | reverse | 3 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Mozambique/Pemba-Mz/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
