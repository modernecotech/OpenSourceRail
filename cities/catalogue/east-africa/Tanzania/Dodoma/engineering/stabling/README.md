# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **113 trainsets at 21 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0835-0580-s000000 | forward | 3 | pending |
| line-1 | line-1-0701-0622-s003512 | forward | 3 | pending |
| line-1 | line-1-0701-0622-s003512 | reverse | 3 | pending |
| line-1 | line-1-0624-0567-s006531 | forward | 3 | pending |
| line-1 | line-1-0624-0567-s006531 | reverse | 3 | pending |
| line-1 | line-1-0555-0560-s008153 | forward | 3 | pending |
| line-1 | line-1-0555-0560-s008153 | reverse | 3 | pending |
| line-1 | line-1-0500-0575-s009552 | forward | 3 | pending |
| line-1 | line-1-0500-0575-s009552 | reverse | 2 | pending |
| line-1 | line-1-0414-0524-s011852 | forward | 2 | pending |
| line-1 | line-1-0414-0524-s011852 | reverse | 2 | pending |
| line-1 | line-1-0301-0526-s014162 | forward | 2 | pending |
| line-1 | line-1-0301-0526-s014162 | reverse | 2 | pending |
| line-1 | line-1-0224-0492-s016470 | reverse | 2 | pending |
| line-2 | line-2-0769-0425-s000000 | forward | 4 | pending |
| line-2 | line-2-0687-0505-s003005 | forward | 3 | pending |
| line-2 | line-2-0687-0505-s003005 | reverse | 3 | pending |
| line-2 | line-2-0627-0525-s004621 | forward | 3 | pending |
| line-2 | line-2-0627-0525-s004621 | reverse | 3 | pending |
| line-2 | line-2-0555-0560-s006897 | forward | 3 | pending |
| line-2 | line-2-0555-0560-s006897 | reverse | 3 | pending |
| line-2 | line-2-0535-0639-s008775 | forward | 3 | pending |
| line-2 | line-2-0535-0639-s008775 | reverse | 3 | pending |
| line-2 | line-2-0580-0700-s010647 | forward | 3 | pending |
| line-2 | line-2-0580-0700-s010647 | reverse | 3 | pending |
| line-2 | line-2-0439-0983-s017586 | reverse | 3 | pending |
| line-3 | line-3-0288-0012-s000000 | forward | 4 | pending |
| line-3 | line-3-0464-0279-s007025 | forward | 4 | pending |
| line-3 | line-3-0464-0279-s007025 | reverse | 4 | pending |
| line-3 | line-3-0530-0415-s010468 | forward | 4 | pending |
| line-3 | line-3-0530-0415-s010468 | reverse | 4 | pending |
| line-3 | line-3-0555-0560-s014107 | forward | 4 | pending |
| line-3 | line-3-0555-0560-s014107 | reverse | 4 | pending |
| line-3 | line-3-0611-0626-s016128 | forward | 4 | pending |
| line-3 | line-3-0611-0626-s016128 | reverse | 4 | pending |
| line-3 | line-3-0646-0668-s018121 | reverse | 4 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Tanzania/Dodoma/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
