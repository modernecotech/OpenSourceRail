# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **76 trainsets at 15 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0565-0491-s000000 | forward | 4 | pending |
| line-1 | line-1-0499-0419-s003000 | forward | 4 | pending |
| line-1 | line-1-0499-0419-s003000 | reverse | 3 | pending |
| line-1 | line-1-0453-0393-s004609 | forward | 3 | pending |
| line-1 | line-1-0453-0393-s004609 | reverse | 3 | pending |
| line-1 | line-1-0386-0374-s006745 | forward | 3 | pending |
| line-1 | line-1-0386-0374-s006745 | reverse | 3 | pending |
| line-1 | line-1-0297-0166-s012218 | reverse | 3 | pending |
| line-2 | line-2-0404-0455-s000000 | forward | 3 | pending |
| line-2 | line-2-0386-0374-s002060 | forward | 3 | pending |
| line-2 | line-2-0386-0374-s002060 | reverse | 3 | pending |
| line-2 | line-2-0471-0361-s004610 | forward | 3 | pending |
| line-2 | line-2-0471-0361-s004610 | reverse | 2 | pending |
| line-2 | line-2-0557-0335-s006890 | forward | 2 | pending |
| line-2 | line-2-0557-0335-s006890 | reverse | 2 | pending |
| line-2 | line-2-0638-0268-s009152 | reverse | 2 | pending |
| line-3 | line-3-0536-0748-s000000 | forward | 4 | pending |
| line-3 | line-3-0428-0477-s006804 | forward | 4 | pending |
| line-3 | line-3-0428-0477-s006804 | reverse | 4 | pending |
| line-3 | line-3-0386-0374-s010437 | forward | 4 | pending |
| line-3 | line-3-0386-0374-s010437 | reverse | 4 | pending |
| line-3 | line-3-0412-0273-s012672 | forward | 4 | pending |
| line-3 | line-3-0412-0273-s012672 | reverse | 3 | pending |
| line-3 | line-3-0420-0164-s014918 | reverse | 3 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Uganda/Fort-Portal/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
