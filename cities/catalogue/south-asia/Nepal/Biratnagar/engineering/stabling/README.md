# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **67 trainsets at 14 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0632-0366-s000000 | forward | 3 | pending |
| line-1 | line-1-0490-0366-s003327 | forward | 3 | pending |
| line-1 | line-1-0490-0366-s003327 | reverse | 3 | pending |
| line-1 | line-1-0371-0378-s006019 | forward | 3 | pending |
| line-1 | line-1-0371-0378-s006019 | reverse | 3 | pending |
| line-1 | line-1-0271-0362-s008476 | forward | 3 | pending |
| line-1 | line-1-0271-0362-s008476 | reverse | 3 | pending |
| line-1 | line-1-0171-0406-s010935 | forward | 3 | pending |
| line-1 | line-1-0171-0406-s010935 | reverse | 3 | pending |
| line-1 | line-1-0059-0424-s013390 | reverse | 2 | pending |
| line-2 | line-2-0547-0484-s000000 | forward | 3 | pending |
| line-2 | line-2-0423-0421-s003025 | forward | 3 | pending |
| line-2 | line-2-0423-0421-s003025 | reverse | 3 | pending |
| line-2 | line-2-0371-0378-s004800 | forward | 3 | pending |
| line-2 | line-2-0371-0378-s004800 | reverse | 3 | pending |
| line-2 | line-2-0339-0471-s007474 | reverse | 2 | pending |
| line-3 | line-3-0439-0080-s000000 | forward | 4 | pending |
| line-3 | line-3-0374-0313-s006167 | forward | 4 | pending |
| line-3 | line-3-0374-0313-s006167 | reverse | 4 | pending |
| line-3 | line-3-0371-0378-s007558 | forward | 3 | pending |
| line-3 | line-3-0371-0378-s007558 | reverse | 3 | pending |
| line-3 | line-3-0242-0424-s010965 | reverse | 3 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/south-asia/Nepal/Biratnagar/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
