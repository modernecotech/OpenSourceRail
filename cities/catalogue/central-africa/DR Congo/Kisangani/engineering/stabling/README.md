# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **50 trainsets at 17 stations**; largest initial station queue **6**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0541-0230-s000000 | forward | 3 | pending |
| line-1 | line-1-0624-0501-s007023 | forward | 3 | pending |
| line-1 | line-1-0624-0501-s007023 | reverse | 3 | pending |
| line-1 | line-1-0723-0698-s012278 | forward | 3 | pending |
| line-1 | line-1-0723-0698-s012278 | reverse | 3 | pending |
| line-1 | line-1-0717-0760-s013679 | forward | 3 | pending |
| line-1 | line-1-0717-0760-s013679 | reverse | 3 | pending |
| line-1 | line-1-0798-0802-s016188 | forward | 3 | pending |
| line-1 | line-1-0798-0802-s016188 | reverse | 3 | pending |
| line-1 | line-1-0841-0806-s018323 | forward | 3 | pending |
| line-1 | line-1-0841-0806-s018323 | reverse | 3 | pending |
| line-1 | line-1-0866-0940-s021343 | forward | 2 | pending |
| line-1 | line-1-0866-0940-s021343 | reverse | 2 | pending |
| line-1 | line-1-0931-1133-s025786 | reverse | 2 | pending |
| line-2 | line-2-0794-0628-s000000 | forward | 1 | pending |
| line-2 | line-2-0794-0628-s000000 | reverse | 1 | pending |
| line-2 | line-2-0775-0702-s001902 | reverse | 1 | pending |
| line-2 | line-2-0717-0760-s003798 | forward | 1 | pending |
| line-2 | line-2-0697-0843-s006015 | forward | 1 | pending |
| line-2 | line-2-0703-0867-s009030 | forward | 1 | pending |
| line-2 | line-2-0703-0867-s009030 | reverse | 1 | pending |
| line-2 | line-2-0795-0819-s011675 | reverse | 1 | pending |
| line-2 | line-2-0845-0820-s015185 | reverse | 1 | pending |
| line-2 | line-2-0838-0749-s018029 | forward | 1 | pending |
| line-2 | line-2-0811-0668-s020134 | forward | 1 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/central-africa/DR Congo/Kisangani/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
