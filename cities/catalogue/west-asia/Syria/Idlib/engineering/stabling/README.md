# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **67 trainsets at 11 stations**; largest initial station queue **9**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0116-0683-s000000 | forward | 5 | pending |
| line-1 | line-1-0322-0465-s007014 | forward | 5 | pending |
| line-1 | line-1-0322-0465-s007014 | reverse | 4 | pending |
| line-1 | line-1-0373-0378-s009327 | forward | 4 | pending |
| line-1 | line-1-0373-0378-s009327 | reverse | 4 | pending |
| line-1 | line-1-0461-0291-s012357 | reverse | 4 | pending |
| line-2 | line-2-0321-0322-s000000 | forward | 5 | pending |
| line-2 | line-2-0373-0378-s002122 | forward | 5 | pending |
| line-2 | line-2-0373-0378-s002122 | reverse | 4 | pending |
| line-2 | line-2-0690-0365-s008858 | reverse | 4 | pending |
| line-3 | line-3-0232-0739-s000000 | forward | 4 | pending |
| line-3 | line-3-0381-0471-s007008 | forward | 4 | pending |
| line-3 | line-3-0381-0471-s007008 | reverse | 4 | pending |
| line-3 | line-3-0373-0378-s009232 | forward | 4 | pending |
| line-3 | line-3-0373-0378-s009232 | reverse | 4 | pending |
| line-3 | line-3-0325-0361-s010737 | reverse | 3 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Syria/Idlib/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
