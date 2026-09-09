# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **130 trainsets at 22 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0325-0925-s000000 | forward | 4 | pending |
| line-1 | line-1-0420-0849-s003025 | forward | 4 | pending |
| line-1 | line-1-0420-0849-s003025 | reverse | 4 | pending |
| line-1 | line-1-0394-0764-s006028 | forward | 4 | pending |
| line-1 | line-1-0394-0764-s006028 | reverse | 3 | pending |
| line-1 | line-1-0462-0658-s009029 | forward | 3 | pending |
| line-1 | line-1-0462-0658-s009029 | reverse | 3 | pending |
| line-1 | line-1-0544-0577-s011949 | forward | 3 | pending |
| line-1 | line-1-0544-0577-s011949 | reverse | 3 | pending |
| line-1 | line-1-0606-0527-s014584 | forward | 3 | pending |
| line-1 | line-1-0606-0527-s014584 | reverse | 3 | pending |
| line-1 | line-1-0642-0400-s018281 | reverse | 3 | pending |
| line-2 | line-2-0309-0394-s000000 | forward | 4 | pending |
| line-2 | line-2-0406-0459-s003020 | forward | 4 | pending |
| line-2 | line-2-0406-0459-s003020 | reverse | 4 | pending |
| line-2 | line-2-0479-0571-s006039 | forward | 4 | pending |
| line-2 | line-2-0479-0571-s006039 | reverse | 4 | pending |
| line-2 | line-2-0544-0577-s008540 | forward | 4 | pending |
| line-2 | line-2-0544-0577-s008540 | reverse | 4 | pending |
| line-2 | line-2-0565-0637-s010426 | forward | 3 | pending |
| line-2 | line-2-0565-0637-s010426 | reverse | 3 | pending |
| line-2 | line-2-0626-0700-s012308 | forward | 3 | pending |
| line-2 | line-2-0626-0700-s012308 | reverse | 3 | pending |
| line-2 | line-2-0710-0848-s016063 | forward | 3 | pending |
| line-2 | line-2-0710-0848-s016063 | reverse | 3 | pending |
| line-2 | line-2-0859-1060-s023646 | reverse | 3 | pending |
| line-3 | line-3-0764-0574-s000000 | forward | 4 | pending |
| line-3 | line-3-0644-0598-s003011 | forward | 4 | pending |
| line-3 | line-3-0644-0598-s003011 | reverse | 4 | pending |
| line-3 | line-3-0544-0577-s005469 | forward | 4 | pending |
| line-3 | line-3-0544-0577-s005469 | reverse | 4 | pending |
| line-3 | line-3-0426-0662-s009053 | forward | 3 | pending |
| line-3 | line-3-0426-0662-s009053 | reverse | 3 | pending |
| line-3 | line-3-0341-0799-s012632 | forward | 3 | pending |
| line-3 | line-3-0341-0799-s012632 | reverse | 3 | pending |
| line-3 | line-3-0223-0834-s015632 | forward | 3 | pending |
| line-3 | line-3-0223-0834-s015632 | reverse | 3 | pending |
| line-3 | line-3-0104-0927-s019448 | reverse | 3 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/central-africa/DR Congo/Bukavu/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
