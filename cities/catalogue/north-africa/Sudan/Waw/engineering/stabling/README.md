# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **41 trainsets at 9 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0239-0231-s000000 | forward | 3 | pending |
| line-1 | line-1-0300-0329-s003008 | forward | 3 | pending |
| line-1 | line-1-0300-0329-s003008 | reverse | 3 | pending |
| line-1 | line-1-0370-0371-s004995 | forward | 3 | pending |
| line-1 | line-1-0370-0371-s004995 | reverse | 3 | pending |
| line-1 | line-1-0486-0395-s008146 | reverse | 2 | pending |
| line-2 | line-2-0075-0290-s000000 | forward | 4 | pending |
| line-2 | line-2-0243-0354-s004359 | forward | 4 | pending |
| line-2 | line-2-0243-0354-s004359 | reverse | 4 | pending |
| line-2 | line-2-0376-0351-s007885 | reverse | 4 | pending |
| line-3 | line-3-0368-0370-s000000 | forward | 4 | pending |
| line-3 | line-3-0301-0309-s002238 | reverse | 4 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/north-africa/Sudan/Waw/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
