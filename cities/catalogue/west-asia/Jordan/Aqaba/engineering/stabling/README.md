# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **71 trainsets at 16 stations**; largest initial station queue **6**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0240-0026-s000000 | forward | 3 | pending |
| line-1 | line-1-0237-0149-s003017 | forward | 3 | pending |
| line-1 | line-1-0237-0149-s003017 | reverse | 3 | pending |
| line-1 | line-1-0306-0271-s006029 | forward | 3 | pending |
| line-1 | line-1-0306-0271-s006029 | reverse | 3 | pending |
| line-1 | line-1-0357-0354-s008689 | forward | 3 | pending |
| line-1 | line-1-0357-0354-s008689 | reverse | 3 | pending |
| line-1 | line-1-0278-0474-s012056 | forward | 3 | pending |
| line-1 | line-1-0278-0474-s012056 | reverse | 3 | pending |
| line-1 | line-1-0215-0575-s014954 | reverse | 3 | pending |
| line-2 | line-2-0425-0361-s000000 | forward | 3 | pending |
| line-2 | line-2-0357-0354-s002017 | forward | 3 | pending |
| line-2 | line-2-0357-0354-s002017 | reverse | 3 | pending |
| line-2 | line-2-0281-0384-s004013 | forward | 3 | pending |
| line-2 | line-2-0281-0384-s004013 | reverse | 2 | pending |
| line-2 | line-2-0243-0451-s006022 | forward | 2 | pending |
| line-2 | line-2-0243-0451-s006022 | reverse | 2 | pending |
| line-2 | line-2-0099-0457-s009643 | reverse | 2 | pending |
| line-3 | line-3-0371-0432-s000000 | forward | 3 | pending |
| line-3 | line-3-0357-0354-s002188 | forward | 3 | pending |
| line-3 | line-3-0357-0354-s002188 | reverse | 3 | pending |
| line-3 | line-3-0327-0255-s004627 | forward | 3 | pending |
| line-3 | line-3-0327-0255-s004627 | reverse | 3 | pending |
| line-3 | line-3-0296-0117-s007644 | forward | 2 | pending |
| line-3 | line-3-0296-0117-s007644 | reverse | 2 | pending |
| line-3 | line-3-0289-0034-s010023 | reverse | 2 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Jordan/Aqaba/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
