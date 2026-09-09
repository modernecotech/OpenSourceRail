# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **73 trainsets at 14 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0573-0322-s000000 | forward | 4 | pending |
| line-1 | line-1-0562-0431-s003002 | forward | 3 | pending |
| line-1 | line-1-0562-0431-s003002 | reverse | 3 | pending |
| line-1 | line-1-0540-0547-s006450 | forward | 3 | pending |
| line-1 | line-1-0540-0547-s006450 | reverse | 3 | pending |
| line-1 | line-1-0421-0590-s009941 | forward | 3 | pending |
| line-1 | line-1-0421-0590-s009941 | reverse | 3 | pending |
| line-1 | line-1-0346-0631-s012083 | forward | 3 | pending |
| line-1 | line-1-0346-0631-s012083 | reverse | 3 | pending |
| line-1 | line-1-0261-0658-s014237 | reverse | 3 | pending |
| line-2 | line-2-0602-0522-s000000 | forward | 4 | pending |
| line-2 | line-2-0540-0547-s002105 | forward | 4 | pending |
| line-2 | line-2-0540-0547-s002105 | reverse | 4 | pending |
| line-2 | line-2-0447-0518-s004850 | forward | 4 | pending |
| line-2 | line-2-0447-0518-s004850 | reverse | 4 | pending |
| line-2 | line-2-0224-0478-s010935 | reverse | 4 | pending |
| line-3 | line-3-0518-0259-s000000 | forward | 3 | pending |
| line-3 | line-3-0477-0391-s003027 | forward | 3 | pending |
| line-3 | line-3-0477-0391-s003027 | reverse | 3 | pending |
| line-3 | line-3-0398-0465-s005428 | forward | 3 | pending |
| line-3 | line-3-0398-0465-s005428 | reverse | 3 | pending |
| line-3 | line-3-0312-0495-s007805 | reverse | 3 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-africa/Cameroon/Garoua/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
