# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **113 trainsets at 21 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0346-0781-s000000 | forward | 3 | pending |
| line-1 | line-1-0502-0681-s005071 | forward | 3 | pending |
| line-1 | line-1-0502-0681-s005071 | reverse | 3 | pending |
| line-1 | line-1-0505-0561-s008096 | forward | 3 | pending |
| line-1 | line-1-0505-0561-s008096 | reverse | 3 | pending |
| line-1 | line-1-0554-0535-s010247 | forward | 3 | pending |
| line-1 | line-1-0554-0535-s010247 | reverse | 3 | pending |
| line-1 | line-1-0597-0505-s012184 | forward | 3 | pending |
| line-1 | line-1-0597-0505-s012184 | reverse | 3 | pending |
| line-1 | line-1-0590-0415-s014120 | forward | 3 | pending |
| line-1 | line-1-0590-0415-s014120 | reverse | 3 | pending |
| line-1 | line-1-0635-0372-s015737 | forward | 3 | pending |
| line-1 | line-1-0635-0372-s015737 | reverse | 3 | pending |
| line-1 | line-1-0630-0303-s017338 | forward | 3 | pending |
| line-1 | line-1-0630-0303-s017338 | reverse | 3 | pending |
| line-1 | line-1-0616-0026-s023124 | reverse | 3 | pending |
| line-2 | line-2-0742-0821-s000000 | forward | 3 | pending |
| line-2 | line-2-0669-0699-s003085 | forward | 3 | pending |
| line-2 | line-2-0669-0699-s003085 | reverse | 3 | pending |
| line-2 | line-2-0595-0599-s006088 | forward | 3 | pending |
| line-2 | line-2-0595-0599-s006088 | reverse | 3 | pending |
| line-2 | line-2-0554-0535-s008313 | forward | 3 | pending |
| line-2 | line-2-0554-0535-s008313 | reverse | 3 | pending |
| line-2 | line-2-0507-0487-s010226 | forward | 3 | pending |
| line-2 | line-2-0507-0487-s010226 | reverse | 3 | pending |
| line-2 | line-2-0431-0455-s012139 | forward | 3 | pending |
| line-2 | line-2-0431-0455-s012139 | reverse | 3 | pending |
| line-2 | line-2-0244-0440-s016493 | reverse | 3 | pending |
| line-3 | line-3-0763-0381-s000000 | forward | 4 | pending |
| line-3 | line-3-0641-0431-s003016 | forward | 4 | pending |
| line-3 | line-3-0641-0431-s003016 | reverse | 4 | pending |
| line-3 | line-3-0592-0529-s006021 | forward | 4 | pending |
| line-3 | line-3-0592-0529-s006021 | reverse | 4 | pending |
| line-3 | line-3-0549-0637-s009040 | forward | 3 | pending |
| line-3 | line-3-0549-0637-s009040 | reverse | 3 | pending |
| line-3 | line-3-0464-0768-s013272 | reverse | 3 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/south-asia/Afghanistan/Kandahar/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
