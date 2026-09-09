# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **92 trainsets at 15 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0353-0233-s000000 | forward | 4 | pending |
| line-1 | line-1-0374-0377-s003627 | forward | 4 | pending |
| line-1 | line-1-0374-0377-s003627 | reverse | 4 | pending |
| line-1 | line-1-0293-0439-s006024 | forward | 4 | pending |
| line-1 | line-1-0293-0439-s006024 | reverse | 4 | pending |
| line-1 | line-1-0300-0511-s008190 | forward | 4 | pending |
| line-1 | line-1-0300-0511-s008190 | reverse | 4 | pending |
| line-1 | line-1-0146-0738-s014717 | reverse | 3 | pending |
| line-2 | line-2-0456-0751-s000000 | forward | 4 | pending |
| line-2 | line-2-0386-0502-s006944 | forward | 4 | pending |
| line-2 | line-2-0386-0502-s006944 | reverse | 4 | pending |
| line-2 | line-2-0374-0377-s009917 | forward | 4 | pending |
| line-2 | line-2-0374-0377-s009917 | reverse | 4 | pending |
| line-2 | line-2-0420-0309-s012404 | forward | 4 | pending |
| line-2 | line-2-0420-0309-s012404 | reverse | 3 | pending |
| line-2 | line-2-0459-0206-s014910 | reverse | 3 | pending |
| line-3 | line-3-0281-0120-s000000 | forward | 4 | pending |
| line-3 | line-3-0300-0310-s004563 | forward | 4 | pending |
| line-3 | line-3-0300-0310-s004563 | reverse | 4 | pending |
| line-3 | line-3-0374-0377-s007454 | forward | 4 | pending |
| line-3 | line-3-0374-0377-s007454 | reverse | 4 | pending |
| line-3 | line-3-0464-0441-s010028 | forward | 4 | pending |
| line-3 | line-3-0464-0441-s010028 | reverse | 4 | pending |
| line-3 | line-3-0706-0540-s015716 | reverse | 3 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Uganda/Lira/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
