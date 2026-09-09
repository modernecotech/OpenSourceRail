# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **153 trainsets at 20 stations**; largest initial station queue **12**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0216-0447-s000000 | forward | 4 | pending |
| line-1 | line-1-0365-0547-s003867 | forward | 4 | pending |
| line-1 | line-1-0365-0547-s003867 | reverse | 4 | pending |
| line-1 | line-1-0463-0507-s006869 | forward | 4 | pending |
| line-1 | line-1-0463-0507-s006869 | reverse | 4 | pending |
| line-1 | line-1-0544-0557-s010230 | forward | 4 | pending |
| line-1 | line-1-0544-0557-s010230 | reverse | 4 | pending |
| line-1 | line-1-0575-0629-s012881 | forward | 4 | pending |
| line-1 | line-1-0575-0629-s012881 | reverse | 4 | pending |
| line-1 | line-1-0690-0685-s015888 | forward | 4 | pending |
| line-1 | line-1-0690-0685-s015888 | reverse | 3 | pending |
| line-1 | line-1-0799-0721-s018734 | reverse | 3 | pending |
| line-2 | line-2-0674-0383-s000000 | forward | 4 | pending |
| line-2 | line-2-0571-0465-s003009 | forward | 4 | pending |
| line-2 | line-2-0571-0465-s003009 | reverse | 4 | pending |
| line-2 | line-2-0544-0557-s005202 | forward | 4 | pending |
| line-2 | line-2-0544-0557-s005202 | reverse | 4 | pending |
| line-2 | line-2-0480-0610-s007128 | forward | 4 | pending |
| line-2 | line-2-0480-0610-s007128 | reverse | 4 | pending |
| line-2 | line-2-0514-0687-s009044 | forward | 4 | pending |
| line-2 | line-2-0514-0687-s009044 | reverse | 4 | pending |
| line-2 | line-2-0458-0842-s014542 | forward | 4 | pending |
| line-2 | line-2-0458-0842-s014542 | reverse | 4 | pending |
| line-2 | line-2-0418-1069-s020043 | reverse | 3 | pending |
| line-3 | line-3-0919-0713-s000000 | forward | 6 | pending |
| line-3 | line-3-0665-0604-s006517 | forward | 6 | pending |
| line-3 | line-3-0665-0604-s006517 | reverse | 6 | pending |
| line-3 | line-3-0544-0557-s010056 | forward | 6 | pending |
| line-3 | line-3-0544-0557-s010056 | reverse | 6 | pending |
| line-3 | line-3-0494-0476-s012532 | forward | 6 | pending |
| line-3 | line-3-0494-0476-s012532 | reverse | 6 | pending |
| line-3 | line-3-0397-0394-s016032 | forward | 6 | pending |
| line-3 | line-3-0397-0394-s016032 | reverse | 6 | pending |
| line-3 | line-3-0085-0118-s025108 | reverse | 6 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Tanzania/Arusha/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
