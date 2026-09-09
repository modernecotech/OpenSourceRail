# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **120 trainsets at 20 stations**; largest initial station queue **9**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0976-0042-s000000 | forward | 4 | pending |
| line-1 | line-1-0939-0161-s003005 | forward | 4 | pending |
| line-1 | line-1-0939-0161-s003005 | reverse | 4 | pending |
| line-1 | line-1-0828-0332-s007603 | forward | 4 | pending |
| line-1 | line-1-0828-0332-s007603 | reverse | 3 | pending |
| line-1 | line-1-0773-0380-s009217 | forward | 3 | pending |
| line-1 | line-1-0773-0380-s009217 | reverse | 3 | pending |
| line-1 | line-1-0709-0472-s012226 | forward | 3 | pending |
| line-1 | line-1-0709-0472-s012226 | reverse | 3 | pending |
| line-1 | line-1-0605-0531-s015102 | forward | 3 | pending |
| line-1 | line-1-0605-0531-s015102 | reverse | 3 | pending |
| line-1 | line-1-0633-0647-s018258 | forward | 3 | pending |
| line-1 | line-1-0633-0647-s018258 | reverse | 3 | pending |
| line-1 | line-1-0619-0784-s021399 | reverse | 3 | pending |
| line-2 | line-2-0617-0977-s000000 | forward | 5 | pending |
| line-2 | line-2-0687-0838-s004487 | forward | 5 | pending |
| line-2 | line-2-0687-0838-s004487 | reverse | 4 | pending |
| line-2 | line-2-0700-0707-s007491 | forward | 4 | pending |
| line-2 | line-2-0700-0707-s007491 | reverse | 4 | pending |
| line-2 | line-2-0767-0585-s010498 | forward | 4 | pending |
| line-2 | line-2-0767-0585-s010498 | reverse | 4 | pending |
| line-2 | line-2-0834-0468-s013509 | forward | 4 | pending |
| line-2 | line-2-0834-0468-s013509 | reverse | 4 | pending |
| line-2 | line-2-1038-0227-s020031 | reverse | 4 | pending |
| line-3 | line-3-0961-0680-s000000 | forward | 4 | pending |
| line-3 | line-3-0845-0596-s003016 | forward | 4 | pending |
| line-3 | line-3-0845-0596-s003016 | reverse | 3 | pending |
| line-3 | line-3-0715-0547-s006022 | forward | 3 | pending |
| line-3 | line-3-0715-0547-s006022 | reverse | 3 | pending |
| line-3 | line-3-0605-0531-s008489 | forward | 3 | pending |
| line-3 | line-3-0605-0531-s008489 | reverse | 3 | pending |
| line-3 | line-3-0487-0584-s012023 | forward | 3 | pending |
| line-3 | line-3-0487-0584-s012023 | reverse | 3 | pending |
| line-3 | line-3-0356-0613-s015276 | reverse | 3 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Saudi Arabia/Najran/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
