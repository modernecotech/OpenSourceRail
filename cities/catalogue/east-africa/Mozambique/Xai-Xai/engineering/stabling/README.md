# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **47 trainsets at 11 stations**; largest initial station queue **6**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0580-0436-s000000 | forward | 3 | pending |
| line-1 | line-1-0449-0448-s003010 | forward | 3 | pending |
| line-1 | line-1-0449-0448-s003010 | reverse | 3 | pending |
| line-1 | line-1-0382-0394-s004936 | forward | 3 | pending |
| line-1 | line-1-0382-0394-s004936 | reverse | 2 | pending |
| line-1 | line-1-0398-0485-s007186 | forward | 2 | pending |
| line-1 | line-1-0398-0485-s007186 | reverse | 2 | pending |
| line-1 | line-1-0351-0573-s009443 | reverse | 2 | pending |
| line-2 | line-2-0455-0642-s000000 | forward | 3 | pending |
| line-2 | line-2-0400-0518-s003212 | forward | 3 | pending |
| line-2 | line-2-0400-0518-s003212 | reverse | 3 | pending |
| line-2 | line-2-0382-0394-s006805 | forward | 3 | pending |
| line-2 | line-2-0382-0394-s006805 | reverse | 3 | pending |
| line-2 | line-2-0325-0372-s008413 | reverse | 2 | pending |
| line-3 | line-3-0508-0509-s000000 | forward | 5 | pending |
| line-3 | line-3-0348-0616-s004370 | reverse | 5 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Mozambique/Xai-Xai/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
