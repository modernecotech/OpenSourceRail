# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **46 trainsets at 11 stations**; largest initial station queue **6**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0558-0329-s000000 | forward | 4 | pending |
| line-1 | line-1-0447-0347-s003008 | forward | 3 | pending |
| line-1 | line-1-0447-0347-s003008 | reverse | 3 | pending |
| line-1 | line-1-0377-0372-s004935 | forward | 3 | pending |
| line-1 | line-1-0377-0372-s004935 | reverse | 3 | pending |
| line-1 | line-1-0341-0544-s008892 | reverse | 3 | pending |
| line-2 | line-2-0302-0386-s000000 | forward | 3 | pending |
| line-2 | line-2-0377-0372-s001673 | forward | 3 | pending |
| line-2 | line-2-0377-0372-s001673 | reverse | 3 | pending |
| line-2 | line-2-0413-0308-s003686 | forward | 2 | pending |
| line-2 | line-2-0413-0308-s003686 | reverse | 2 | pending |
| line-2 | line-2-0494-0268-s005704 | reverse | 2 | pending |
| line-3 | line-3-0310-0321-s000000 | forward | 3 | pending |
| line-3 | line-3-0377-0372-s002060 | forward | 3 | pending |
| line-3 | line-3-0377-0372-s002060 | reverse | 3 | pending |
| line-3 | line-3-0463-0383-s004176 | reverse | 3 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/north-africa/Morocco/Khouribga/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
