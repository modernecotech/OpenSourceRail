# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **112 trainsets at 21 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0448-0937-s000000 | forward | 3 | pending |
| line-1 | line-1-0534-0829-s003001 | forward | 3 | pending |
| line-1 | line-1-0534-0829-s003001 | reverse | 3 | pending |
| line-1 | line-1-0571-0700-s006008 | forward | 3 | pending |
| line-1 | line-1-0571-0700-s006008 | reverse | 3 | pending |
| line-1 | line-1-0554-0539-s009494 | forward | 3 | pending |
| line-1 | line-1-0554-0539-s009494 | reverse | 3 | pending |
| line-1 | line-1-0624-0504-s012032 | forward | 3 | pending |
| line-1 | line-1-0624-0504-s012032 | reverse | 3 | pending |
| line-1 | line-1-0696-0396-s015721 | forward | 3 | pending |
| line-1 | line-1-0696-0396-s015721 | reverse | 3 | pending |
| line-1 | line-1-0673-0306-s017777 | forward | 3 | pending |
| line-1 | line-1-0673-0306-s017777 | reverse | 3 | pending |
| line-1 | line-1-0733-0298-s019814 | reverse | 2 | pending |
| line-2 | line-2-0609-0917-s000000 | forward | 4 | pending |
| line-2 | line-2-0626-0680-s006415 | forward | 4 | pending |
| line-2 | line-2-0626-0680-s006415 | reverse | 4 | pending |
| line-2 | line-2-0604-0598-s008460 | forward | 4 | pending |
| line-2 | line-2-0604-0598-s008460 | reverse | 4 | pending |
| line-2 | line-2-0554-0539-s010503 | forward | 3 | pending |
| line-2 | line-2-0554-0539-s010503 | reverse | 3 | pending |
| line-2 | line-2-0565-0450-s012447 | forward | 3 | pending |
| line-2 | line-2-0565-0450-s012447 | reverse | 3 | pending |
| line-2 | line-2-0626-0346-s015449 | forward | 3 | pending |
| line-2 | line-2-0626-0346-s015449 | reverse | 3 | pending |
| line-2 | line-2-0671-0218-s019026 | forward | 3 | pending |
| line-2 | line-2-0671-0218-s019026 | reverse | 3 | pending |
| line-2 | line-2-0708-0058-s022608 | reverse | 3 | pending |
| line-3 | line-3-0451-0402-s000000 | forward | 3 | pending |
| line-3 | line-3-0506-0499-s003009 | forward | 3 | pending |
| line-3 | line-3-0506-0499-s003009 | reverse | 3 | pending |
| line-3 | line-3-0554-0539-s004613 | forward | 3 | pending |
| line-3 | line-3-0554-0539-s004613 | reverse | 3 | pending |
| line-3 | line-3-0582-0487-s006028 | forward | 3 | pending |
| line-3 | line-3-0582-0487-s006028 | reverse | 3 | pending |
| line-3 | line-3-0781-0464-s010598 | reverse | 3 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Tanzania/Mbeya/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
