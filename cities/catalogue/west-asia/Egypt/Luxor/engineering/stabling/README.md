# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **111 trainsets at 17 stations**; largest initial station queue **10**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0268-0383-s000000 | forward | 4 | pending |
| line-1 | line-1-0405-0484-s004702 | forward | 4 | pending |
| line-1 | line-1-0405-0484-s004702 | reverse | 4 | pending |
| line-1 | line-1-0471-0539-s006674 | forward | 4 | pending |
| line-1 | line-1-0471-0539-s006674 | reverse | 4 | pending |
| line-1 | line-1-0548-0547-s008986 | forward | 3 | pending |
| line-1 | line-1-0548-0547-s008986 | reverse | 3 | pending |
| line-1 | line-1-0712-0526-s013238 | reverse | 3 | pending |
| line-2 | line-2-0954-0093-s000000 | forward | 5 | pending |
| line-2 | line-2-0588-0433-s011050 | forward | 5 | pending |
| line-2 | line-2-0588-0433-s011050 | reverse | 5 | pending |
| line-2 | line-2-0548-0547-s013850 | forward | 5 | pending |
| line-2 | line-2-0548-0547-s013850 | reverse | 5 | pending |
| line-2 | line-2-0497-0579-s015672 | forward | 5 | pending |
| line-2 | line-2-0497-0579-s015672 | reverse | 4 | pending |
| line-2 | line-2-0411-0665-s018221 | forward | 4 | pending |
| line-2 | line-2-0411-0665-s018221 | reverse | 4 | pending |
| line-2 | line-2-0324-0669-s020767 | reverse | 4 | pending |
| line-3 | line-3-0621-0862-s000000 | forward | 4 | pending |
| line-3 | line-3-0589-0631-s006957 | forward | 4 | pending |
| line-3 | line-3-0589-0631-s006957 | reverse | 4 | pending |
| line-3 | line-3-0548-0547-s009220 | forward | 4 | pending |
| line-3 | line-3-0548-0547-s009220 | reverse | 4 | pending |
| line-3 | line-3-0490-0478-s011104 | forward | 4 | pending |
| line-3 | line-3-0490-0478-s011104 | reverse | 3 | pending |
| line-3 | line-3-0414-0479-s012992 | forward | 3 | pending |
| line-3 | line-3-0414-0479-s012992 | reverse | 3 | pending |
| line-3 | line-3-0300-0398-s016658 | reverse | 3 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Egypt/Luxor/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
