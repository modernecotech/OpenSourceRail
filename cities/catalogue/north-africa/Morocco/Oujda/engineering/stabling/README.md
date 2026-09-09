# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **81 trainsets at 18 stations**; largest initial station queue **7**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0481-0306-s000000 | forward | 3 | pending |
| line-1 | line-1-0480-0430-s003024 | forward | 3 | pending |
| line-1 | line-1-0480-0430-s003024 | reverse | 3 | pending |
| line-1 | line-1-0505-0497-s005124 | forward | 3 | pending |
| line-1 | line-1-0505-0497-s005124 | reverse | 3 | pending |
| line-1 | line-1-0553-0553-s007210 | forward | 3 | pending |
| line-1 | line-1-0553-0553-s007210 | reverse | 3 | pending |
| line-1 | line-1-0551-0646-s009281 | forward | 3 | pending |
| line-1 | line-1-0551-0646-s009281 | reverse | 2 | pending |
| line-1 | line-1-0583-0785-s012962 | reverse | 2 | pending |
| line-2 | line-2-0321-0576-s000000 | forward | 3 | pending |
| line-2 | line-2-0413-0595-s003006 | forward | 3 | pending |
| line-2 | line-2-0413-0595-s003006 | reverse | 3 | pending |
| line-2 | line-2-0477-0567-s004919 | forward | 2 | pending |
| line-2 | line-2-0477-0567-s004919 | reverse | 2 | pending |
| line-2 | line-2-0553-0553-s006817 | forward | 2 | pending |
| line-2 | line-2-0553-0553-s006817 | reverse | 2 | pending |
| line-2 | line-2-0604-0553-s008825 | forward | 2 | pending |
| line-2 | line-2-0604-0553-s008825 | reverse | 2 | pending |
| line-2 | line-2-0661-0612-s010820 | forward | 2 | pending |
| line-2 | line-2-0661-0612-s010820 | reverse | 2 | pending |
| line-2 | line-2-0732-0616-s012835 | reverse | 2 | pending |
| line-3 | line-3-0345-0481-s000000 | forward | 4 | pending |
| line-3 | line-3-0457-0503-s003007 | forward | 4 | pending |
| line-3 | line-3-0457-0503-s003007 | reverse | 3 | pending |
| line-3 | line-3-0553-0553-s005802 | forward | 3 | pending |
| line-3 | line-3-0553-0553-s005802 | reverse | 3 | pending |
| line-3 | line-3-0589-0448-s008349 | forward | 3 | pending |
| line-3 | line-3-0589-0448-s008349 | reverse | 3 | pending |
| line-3 | line-3-0692-0360-s011703 | reverse | 3 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/north-africa/Morocco/Oujda/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
