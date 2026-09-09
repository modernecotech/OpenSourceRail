# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **129 trainsets at 20 stations**; largest initial station queue **10**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-1054-1032-s000000 | forward | 4 | pending |
| line-1 | line-1-0648-0679-s011501 | forward | 4 | pending |
| line-1 | line-1-0648-0679-s011501 | reverse | 4 | pending |
| line-1 | line-1-0595-0608-s013459 | forward | 4 | pending |
| line-1 | line-1-0595-0608-s013459 | reverse | 4 | pending |
| line-1 | line-1-0542-0536-s015406 | forward | 4 | pending |
| line-1 | line-1-0542-0536-s015406 | reverse | 4 | pending |
| line-1 | line-1-0466-0499-s017523 | forward | 4 | pending |
| line-1 | line-1-0466-0499-s017523 | reverse | 4 | pending |
| line-1 | line-1-0450-0427-s019422 | forward | 4 | pending |
| line-1 | line-1-0450-0427-s019422 | reverse | 4 | pending |
| line-1 | line-1-0435-0322-s022001 | forward | 4 | pending |
| line-1 | line-1-0435-0322-s022001 | reverse | 3 | pending |
| line-1 | line-1-0409-0232-s024595 | reverse | 3 | pending |
| line-2 | line-2-0676-0236-s000000 | forward | 4 | pending |
| line-2 | line-2-0593-0345-s003008 | forward | 3 | pending |
| line-2 | line-2-0593-0345-s003008 | reverse | 3 | pending |
| line-2 | line-2-0565-0483-s006017 | forward | 3 | pending |
| line-2 | line-2-0565-0483-s006017 | reverse | 3 | pending |
| line-2 | line-2-0542-0536-s007378 | forward | 3 | pending |
| line-2 | line-2-0542-0536-s007378 | reverse | 3 | pending |
| line-2 | line-2-0494-0573-s009035 | forward | 3 | pending |
| line-2 | line-2-0494-0573-s009035 | reverse | 3 | pending |
| line-2 | line-2-0304-0616-s013369 | forward | 3 | pending |
| line-2 | line-2-0304-0616-s013369 | reverse | 3 | pending |
| line-2 | line-2-0124-0683-s017690 | reverse | 3 | pending |
| line-3 | line-3-0202-0517-s000000 | forward | 5 | pending |
| line-3 | line-3-0383-0485-s005145 | forward | 5 | pending |
| line-3 | line-3-0383-0485-s005145 | reverse | 5 | pending |
| line-3 | line-3-0378-0384-s008161 | forward | 5 | pending |
| line-3 | line-3-0378-0384-s008161 | reverse | 5 | pending |
| line-3 | line-3-0439-0285-s011186 | forward | 5 | pending |
| line-3 | line-3-0439-0285-s011186 | reverse | 4 | pending |
| line-3 | line-3-0608-0185-s018294 | reverse | 4 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Egypt/Suez/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
