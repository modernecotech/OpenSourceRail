# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **84 trainsets at 14 stations**; largest initial station queue **12**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0462-0834-s000000 | forward | 3 | pending |
| line-1 | line-1-0480-0727-s003012 | forward | 3 | pending |
| line-1 | line-1-0480-0727-s003012 | reverse | 3 | pending |
| line-1 | line-1-0432-0620-s006014 | forward | 3 | pending |
| line-1 | line-1-0432-0620-s006014 | reverse | 3 | pending |
| line-1 | line-1-0481-0553-s007866 | forward | 3 | pending |
| line-1 | line-1-0481-0553-s007866 | reverse | 3 | pending |
| line-1 | line-1-0570-0514-s010019 | forward | 2 | pending |
| line-1 | line-1-0570-0514-s010019 | reverse | 2 | pending |
| line-1 | line-1-0641-0492-s012147 | reverse | 2 | pending |
| line-2 | line-2-0510-0774-s000000 | forward | 6 | pending |
| line-2 | line-2-0546-0660-s003008 | forward | 6 | pending |
| line-2 | line-2-0546-0660-s003008 | reverse | 6 | pending |
| line-2 | line-2-0640-0584-s006014 | forward | 6 | pending |
| line-2 | line-2-0640-0584-s006014 | reverse | 6 | pending |
| line-2 | line-2-0913-0374-s016951 | reverse | 6 | pending |
| line-3 | line-3-0680-0673-s000000 | forward | 4 | pending |
| line-3 | line-3-0581-0615-s003012 | forward | 4 | pending |
| line-3 | line-3-0581-0615-s003012 | reverse | 4 | pending |
| line-3 | line-3-0481-0553-s006701 | forward | 3 | pending |
| line-3 | line-3-0481-0553-s006701 | reverse | 3 | pending |
| line-3 | line-3-0403-0652-s009737 | reverse | 3 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Palestine/Gaza-City/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
