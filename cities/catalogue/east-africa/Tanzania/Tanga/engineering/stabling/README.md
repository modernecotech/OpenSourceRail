# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **108 trainsets at 20 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0364-0285-s000000 | forward | 4 | pending |
| line-1 | line-1-0487-0372-s004046 | forward | 4 | pending |
| line-1 | line-1-0487-0372-s004046 | reverse | 4 | pending |
| line-1 | line-1-0494-0481-s007068 | forward | 4 | pending |
| line-1 | line-1-0494-0481-s007068 | reverse | 4 | pending |
| line-1 | line-1-0542-0517-s010082 | forward | 4 | pending |
| line-1 | line-1-0542-0517-s010082 | reverse | 4 | pending |
| line-1 | line-1-0614-0584-s013090 | forward | 4 | pending |
| line-1 | line-1-0614-0584-s013090 | reverse | 4 | pending |
| line-1 | line-1-0774-0645-s017227 | forward | 4 | pending |
| line-1 | line-1-0774-0645-s017227 | reverse | 3 | pending |
| line-1 | line-1-0930-0771-s021391 | reverse | 3 | pending |
| line-2 | line-2-0603-0186-s000000 | forward | 3 | pending |
| line-2 | line-2-0549-0369-s005055 | forward | 3 | pending |
| line-2 | line-2-0549-0369-s005055 | reverse | 3 | pending |
| line-2 | line-2-0550-0459-s007102 | forward | 3 | pending |
| line-2 | line-2-0550-0459-s007102 | reverse | 3 | pending |
| line-2 | line-2-0546-0549-s009170 | forward | 3 | pending |
| line-2 | line-2-0546-0549-s009170 | reverse | 3 | pending |
| line-2 | line-2-0495-0609-s011079 | forward | 3 | pending |
| line-2 | line-2-0495-0609-s011079 | reverse | 2 | pending |
| line-2 | line-2-0419-0600-s013120 | forward | 2 | pending |
| line-2 | line-2-0419-0600-s013120 | reverse | 2 | pending |
| line-2 | line-2-0356-0657-s015183 | reverse | 2 | pending |
| line-3 | line-3-0376-0685-s000000 | forward | 3 | pending |
| line-3 | line-3-0468-0626-s003012 | forward | 3 | pending |
| line-3 | line-3-0468-0626-s003012 | reverse | 3 | pending |
| line-3 | line-3-0546-0549-s005574 | forward | 3 | pending |
| line-3 | line-3-0546-0549-s005574 | reverse | 3 | pending |
| line-3 | line-3-0497-0462-s008223 | forward | 3 | pending |
| line-3 | line-3-0497-0462-s008223 | reverse | 3 | pending |
| line-3 | line-3-0512-0354-s010872 | forward | 3 | pending |
| line-3 | line-3-0512-0354-s010872 | reverse | 3 | pending |
| line-3 | line-3-0461-0244-s013506 | reverse | 3 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Tanzania/Tanga/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
