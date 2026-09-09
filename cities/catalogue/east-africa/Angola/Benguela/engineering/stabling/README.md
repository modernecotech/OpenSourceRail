# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **110 trainsets at 17 stations**; largest initial station queue **10**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0065-1050-s000000 | forward | 4 | pending |
| line-1 | line-1-0313-0830-s007005 | forward | 4 | pending |
| line-1 | line-1-0313-0830-s007005 | reverse | 4 | pending |
| line-1 | line-1-0402-0716-s010022 | forward | 4 | pending |
| line-1 | line-1-0402-0716-s010022 | reverse | 4 | pending |
| line-1 | line-1-0498-0606-s013041 | forward | 4 | pending |
| line-1 | line-1-0498-0606-s013041 | reverse | 4 | pending |
| line-1 | line-1-0557-0557-s014731 | forward | 4 | pending |
| line-1 | line-1-0557-0557-s014731 | reverse | 4 | pending |
| line-1 | line-1-0668-0523-s017657 | forward | 4 | pending |
| line-1 | line-1-0668-0523-s017657 | reverse | 4 | pending |
| line-1 | line-1-0800-0524-s021320 | reverse | 3 | pending |
| line-2 | line-2-0447-0786-s000000 | forward | 4 | pending |
| line-2 | line-2-0510-0661-s003022 | forward | 4 | pending |
| line-2 | line-2-0510-0661-s003022 | reverse | 4 | pending |
| line-2 | line-2-0557-0557-s005787 | forward | 4 | pending |
| line-2 | line-2-0557-0557-s005787 | reverse | 4 | pending |
| line-2 | line-2-0632-0473-s008650 | forward | 4 | pending |
| line-2 | line-2-0632-0473-s008650 | reverse | 3 | pending |
| line-2 | line-2-0722-0306-s012736 | forward | 3 | pending |
| line-2 | line-2-0722-0306-s012736 | reverse | 3 | pending |
| line-2 | line-2-0742-0111-s016813 | reverse | 3 | pending |
| line-3 | line-3-0555-0587-s000000 | forward | 5 | pending |
| line-3 | line-3-0621-0596-s003018 | forward | 5 | pending |
| line-3 | line-3-0621-0596-s003018 | reverse | 5 | pending |
| line-3 | line-3-0698-0709-s006038 | forward | 4 | pending |
| line-3 | line-3-0698-0709-s006038 | reverse | 4 | pending |
| line-3 | line-3-0901-0910-s012319 | reverse | 4 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Angola/Benguela/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
