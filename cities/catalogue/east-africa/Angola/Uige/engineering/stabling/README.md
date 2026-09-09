# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **27 trainsets at 6 stations**; largest initial station queue **6**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0510-0252-s000000 | forward | 3 | pending |
| line-1 | line-1-0544-0356-s003018 | forward | 3 | pending |
| line-1 | line-1-0544-0356-s003018 | reverse | 3 | pending |
| line-1 | line-1-0484-0474-s006033 | forward | 3 | pending |
| line-1 | line-1-0484-0474-s006033 | reverse | 3 | pending |
| line-1 | line-1-0551-0546-s008251 | forward | 3 | pending |
| line-1 | line-1-0551-0546-s008251 | reverse | 3 | pending |
| line-1 | line-1-0605-0541-s010131 | forward | 2 | pending |
| line-1 | line-1-0605-0541-s010131 | reverse | 2 | pending |
| line-1 | line-1-0674-0519-s012025 | reverse | 2 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Angola/Uige/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
