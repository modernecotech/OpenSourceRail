# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **125 trainsets at 20 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0939-1100-s000000 | forward | 4 | pending |
| line-1 | line-1-0828-0834-s007008 | forward | 4 | pending |
| line-1 | line-1-0828-0834-s007008 | reverse | 4 | pending |
| line-1 | line-1-0734-0682-s010826 | forward | 4 | pending |
| line-1 | line-1-0734-0682-s010826 | reverse | 4 | pending |
| line-1 | line-1-0618-0605-s013831 | forward | 4 | pending |
| line-1 | line-1-0618-0605-s013831 | reverse | 4 | pending |
| line-1 | line-1-0566-0536-s015654 | forward | 4 | pending |
| line-1 | line-1-0566-0536-s015654 | reverse | 4 | pending |
| line-1 | line-1-0492-0498-s017758 | forward | 4 | pending |
| line-1 | line-1-0492-0498-s017758 | reverse | 4 | pending |
| line-1 | line-1-0475-0431-s019851 | forward | 3 | pending |
| line-1 | line-1-0475-0431-s019851 | reverse | 3 | pending |
| line-1 | line-1-0335-0312-s025733 | reverse | 3 | pending |
| line-2 | line-2-0876-0538-s000000 | forward | 4 | pending |
| line-2 | line-2-0753-0471-s003015 | forward | 4 | pending |
| line-2 | line-2-0753-0471-s003015 | reverse | 4 | pending |
| line-2 | line-2-0626-0417-s006026 | forward | 4 | pending |
| line-2 | line-2-0626-0417-s006026 | reverse | 4 | pending |
| line-2 | line-2-0544-0350-s009045 | forward | 4 | pending |
| line-2 | line-2-0544-0350-s009045 | reverse | 3 | pending |
| line-2 | line-2-0412-0236-s014522 | reverse | 3 | pending |
| line-3 | line-3-0354-0936-s000000 | forward | 4 | pending |
| line-3 | line-3-0460-0693-s007010 | forward | 4 | pending |
| line-3 | line-3-0460-0693-s007010 | reverse | 4 | pending |
| line-3 | line-3-0503-0610-s009026 | forward | 4 | pending |
| line-3 | line-3-0503-0610-s009026 | reverse | 4 | pending |
| line-3 | line-3-0566-0536-s011028 | forward | 4 | pending |
| line-3 | line-3-0566-0536-s011028 | reverse | 3 | pending |
| line-3 | line-3-0569-0468-s012462 | forward | 3 | pending |
| line-3 | line-3-0569-0468-s012462 | reverse | 3 | pending |
| line-3 | line-3-0588-0344-s015475 | forward | 3 | pending |
| line-3 | line-3-0588-0344-s015475 | reverse | 3 | pending |
| line-3 | line-3-0658-0201-s019239 | reverse | 3 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Saudi Arabia/Taif/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
