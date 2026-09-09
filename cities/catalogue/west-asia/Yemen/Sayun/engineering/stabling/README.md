# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **54 trainsets at 11 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0273-0600-s000000 | forward | 4 | pending |
| line-1 | line-1-0327-0472-s003007 | forward | 4 | pending |
| line-1 | line-1-0327-0472-s003007 | reverse | 4 | pending |
| line-1 | line-1-0375-0375-s005392 | forward | 4 | pending |
| line-1 | line-1-0375-0375-s005392 | reverse | 4 | pending |
| line-1 | line-1-0363-0292-s008120 | forward | 3 | pending |
| line-1 | line-1-0363-0292-s008120 | reverse | 3 | pending |
| line-1 | line-1-0491-0047-s014174 | reverse | 3 | pending |
| line-2 | line-2-0465-0310-s000000 | forward | 4 | pending |
| line-2 | line-2-0375-0375-s002425 | forward | 3 | pending |
| line-2 | line-2-0375-0375-s002425 | reverse | 3 | pending |
| line-2 | line-2-0283-0307-s005366 | reverse | 3 | pending |
| line-3 | line-3-0454-0403-s000000 | forward | 3 | pending |
| line-3 | line-3-0375-0375-s002107 | forward | 3 | pending |
| line-3 | line-3-0375-0375-s002107 | reverse | 3 | pending |
| line-3 | line-3-0258-0373-s004861 | reverse | 3 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Yemen/Sayun/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
