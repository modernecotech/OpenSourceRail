# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **81 trainsets at 17 stations**; largest initial station queue **7**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0533-0436-s000000 | forward | 3 | pending |
| line-1 | line-1-0450-0376-s003020 | forward | 3 | pending |
| line-1 | line-1-0450-0376-s003020 | reverse | 3 | pending |
| line-1 | line-1-0375-0385-s005026 | forward | 3 | pending |
| line-1 | line-1-0375-0385-s005026 | reverse | 3 | pending |
| line-1 | line-1-0279-0441-s008217 | forward | 3 | pending |
| line-1 | line-1-0279-0441-s008217 | reverse | 3 | pending |
| line-1 | line-1-0182-0512-s011235 | forward | 3 | pending |
| line-1 | line-1-0182-0512-s011235 | reverse | 3 | pending |
| line-1 | line-1-0069-0563-s014494 | reverse | 3 | pending |
| line-2 | line-2-0450-0518-s000000 | forward | 3 | pending |
| line-2 | line-2-0394-0437-s003017 | forward | 3 | pending |
| line-2 | line-2-0394-0437-s003017 | reverse | 3 | pending |
| line-2 | line-2-0375-0385-s004254 | forward | 3 | pending |
| line-2 | line-2-0375-0385-s004254 | reverse | 3 | pending |
| line-2 | line-2-0389-0203-s008176 | forward | 2 | pending |
| line-2 | line-2-0389-0203-s008176 | reverse | 2 | pending |
| line-2 | line-2-0387-0109-s010150 | forward | 2 | pending |
| line-2 | line-2-0387-0109-s010150 | reverse | 2 | pending |
| line-2 | line-2-0394-0018-s012111 | reverse | 2 | pending |
| line-3 | line-3-0258-0500-s000000 | forward | 4 | pending |
| line-3 | line-3-0360-0442-s003000 | forward | 4 | pending |
| line-3 | line-3-0360-0442-s003000 | reverse | 3 | pending |
| line-3 | line-3-0375-0385-s004376 | forward | 3 | pending |
| line-3 | line-3-0375-0385-s004376 | reverse | 3 | pending |
| line-3 | line-3-0502-0457-s007676 | forward | 3 | pending |
| line-3 | line-3-0502-0457-s007676 | reverse | 3 | pending |
| line-3 | line-3-0685-0451-s012362 | reverse | 3 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Mozambique/Nacala/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
