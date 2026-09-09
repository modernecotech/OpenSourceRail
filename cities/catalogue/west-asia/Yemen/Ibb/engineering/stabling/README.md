# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **106 trainsets at 17 stations**; largest initial station queue **10**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0398-0570-s000000 | forward | 4 | pending |
| line-1 | line-1-0491-0549-s002690 | forward | 3 | pending |
| line-1 | line-1-0491-0549-s002690 | reverse | 3 | pending |
| line-1 | line-1-0553-0551-s004791 | forward | 3 | pending |
| line-1 | line-1-0553-0551-s004791 | reverse | 3 | pending |
| line-1 | line-1-0618-0564-s006756 | forward | 3 | pending |
| line-1 | line-1-0618-0564-s006756 | reverse | 3 | pending |
| line-1 | line-1-0654-0488-s008708 | forward | 3 | pending |
| line-1 | line-1-0654-0488-s008708 | reverse | 3 | pending |
| line-1 | line-1-0806-0339-s014618 | reverse | 3 | pending |
| line-2 | line-2-0772-0532-s000000 | forward | 5 | pending |
| line-2 | line-2-0646-0515-s003006 | forward | 5 | pending |
| line-2 | line-2-0646-0515-s003006 | reverse | 5 | pending |
| line-2 | line-2-0553-0551-s006198 | forward | 5 | pending |
| line-2 | line-2-0553-0551-s006198 | reverse | 5 | pending |
| line-2 | line-2-0538-0456-s009039 | forward | 5 | pending |
| line-2 | line-2-0538-0456-s009039 | reverse | 4 | pending |
| line-2 | line-2-0429-0379-s012541 | forward | 4 | pending |
| line-2 | line-2-0429-0379-s012541 | reverse | 4 | pending |
| line-2 | line-2-0113-0058-s021649 | reverse | 4 | pending |
| line-3 | line-3-0903-0571-s000000 | forward | 4 | pending |
| line-3 | line-3-0678-0597-s004831 | forward | 4 | pending |
| line-3 | line-3-0678-0597-s004831 | reverse | 4 | pending |
| line-3 | line-3-0553-0551-s008371 | forward | 4 | pending |
| line-3 | line-3-0553-0551-s008371 | reverse | 4 | pending |
| line-3 | line-3-0491-0620-s011000 | forward | 3 | pending |
| line-3 | line-3-0491-0620-s011000 | reverse | 3 | pending |
| line-3 | line-3-0379-0667-s013629 | reverse | 3 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Yemen/Ibb/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
