# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **61 trainsets at 11 stations**; largest initial station queue **10**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0685-0401-s000000 | forward | 5 | pending |
| line-1 | line-1-0427-0424-s005898 | forward | 5 | pending |
| line-1 | line-1-0427-0424-s005898 | reverse | 5 | pending |
| line-1 | line-1-0376-0370-s007839 | forward | 5 | pending |
| line-1 | line-1-0376-0370-s007839 | reverse | 4 | pending |
| line-1 | line-1-0168-0334-s013573 | reverse | 4 | pending |
| line-2 | line-2-0349-0364-s000000 | forward | 4 | pending |
| line-2 | line-2-0356-0298-s002589 | forward | 3 | pending |
| line-2 | line-2-0356-0298-s002589 | reverse | 3 | pending |
| line-2 | line-2-0280-0235-s005188 | reverse | 3 | pending |
| line-3 | line-3-0401-0363-s000000 | forward | 4 | pending |
| line-3 | line-3-0387-0293-s002312 | forward | 4 | pending |
| line-3 | line-3-0387-0293-s002312 | reverse | 3 | pending |
| line-3 | line-3-0419-0202-s004608 | forward | 3 | pending |
| line-3 | line-3-0419-0202-s004608 | reverse | 3 | pending |
| line-3 | line-3-0572-0072-s009213 | reverse | 3 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Kenya/Meru-Ke/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
