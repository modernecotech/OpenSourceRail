# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **104 trainsets at 22 stations**; largest initial station queue **6**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0491-0802-s000000 | forward | 3 | pending |
| line-1 | line-1-0546-0676-s003011 | forward | 3 | pending |
| line-1 | line-1-0546-0676-s003011 | reverse | 3 | pending |
| line-1 | line-1-0590-0549-s006026 | forward | 3 | pending |
| line-1 | line-1-0590-0549-s006026 | reverse | 3 | pending |
| line-1 | line-1-0554-0499-s007914 | forward | 3 | pending |
| line-1 | line-1-0554-0499-s007914 | reverse | 3 | pending |
| line-1 | line-1-0565-0395-s010975 | forward | 3 | pending |
| line-1 | line-1-0565-0395-s010975 | reverse | 3 | pending |
| line-1 | line-1-0525-0286-s013987 | forward | 3 | pending |
| line-1 | line-1-0525-0286-s013987 | reverse | 3 | pending |
| line-1 | line-1-0527-0190-s016406 | reverse | 3 | pending |
| line-2 | line-2-0654-0283-s000000 | forward | 3 | pending |
| line-2 | line-2-0643-0387-s003006 | forward | 3 | pending |
| line-2 | line-2-0643-0387-s003006 | reverse | 3 | pending |
| line-2 | line-2-0587-0440-s004970 | forward | 3 | pending |
| line-2 | line-2-0587-0440-s004970 | reverse | 3 | pending |
| line-2 | line-2-0554-0499-s006945 | forward | 3 | pending |
| line-2 | line-2-0554-0499-s006945 | reverse | 3 | pending |
| line-2 | line-2-0473-0537-s009049 | forward | 2 | pending |
| line-2 | line-2-0473-0537-s009049 | reverse | 2 | pending |
| line-2 | line-2-0418-0643-s011674 | forward | 2 | pending |
| line-2 | line-2-0418-0643-s011674 | reverse | 2 | pending |
| line-2 | line-2-0361-0731-s014321 | reverse | 2 | pending |
| line-3 | line-3-0476-0055-s000000 | forward | 3 | pending |
| line-3 | line-3-0498-0182-s003382 | forward | 3 | pending |
| line-3 | line-3-0498-0182-s003382 | reverse | 3 | pending |
| line-3 | line-3-0476-0294-s006395 | forward | 3 | pending |
| line-3 | line-3-0476-0294-s006395 | reverse | 3 | pending |
| line-3 | line-3-0485-0402-s009399 | forward | 3 | pending |
| line-3 | line-3-0485-0402-s009399 | reverse | 3 | pending |
| line-3 | line-3-0495-0477-s011207 | forward | 3 | pending |
| line-3 | line-3-0495-0477-s011207 | reverse | 3 | pending |
| line-3 | line-3-0554-0499-s012569 | forward | 2 | pending |
| line-3 | line-3-0554-0499-s012569 | reverse | 2 | pending |
| line-3 | line-3-0513-0559-s014219 | forward | 2 | pending |
| line-3 | line-3-0513-0559-s014219 | reverse | 2 | pending |
| line-3 | line-3-0421-0641-s017280 | reverse | 2 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Iraq/Ramadi/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
