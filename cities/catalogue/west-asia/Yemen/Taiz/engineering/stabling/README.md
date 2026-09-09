# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **94 trainsets at 17 stations**; largest initial station queue **10**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0637-1074-s000000 | forward | 4 | pending |
| line-1 | line-1-0637-0724-s007000 | forward | 4 | pending |
| line-1 | line-1-0637-0724-s007000 | reverse | 4 | pending |
| line-1 | line-1-0606-0590-s010007 | forward | 4 | pending |
| line-1 | line-1-0606-0590-s010007 | reverse | 3 | pending |
| line-1 | line-1-0556-0541-s012026 | forward | 3 | pending |
| line-1 | line-1-0556-0541-s012026 | reverse | 3 | pending |
| line-1 | line-1-0568-0466-s014071 | forward | 3 | pending |
| line-1 | line-1-0568-0466-s014071 | reverse | 3 | pending |
| line-1 | line-1-0536-0380-s016118 | forward | 3 | pending |
| line-1 | line-1-0536-0380-s016118 | reverse | 3 | pending |
| line-1 | line-1-0526-0296-s018154 | reverse | 3 | pending |
| line-2 | line-2-0405-0445-s000000 | forward | 3 | pending |
| line-2 | line-2-0487-0496-s002062 | forward | 3 | pending |
| line-2 | line-2-0487-0496-s002062 | reverse | 3 | pending |
| line-2 | line-2-0556-0541-s004124 | forward | 2 | pending |
| line-2 | line-2-0556-0541-s004124 | reverse | 2 | pending |
| line-2 | line-2-0530-0628-s006427 | forward | 2 | pending |
| line-2 | line-2-0530-0628-s006427 | reverse | 2 | pending |
| line-2 | line-2-0483-0717-s008749 | reverse | 2 | pending |
| line-3 | line-3-1040-0281-s000000 | forward | 5 | pending |
| line-3 | line-3-0764-0463-s007028 | forward | 5 | pending |
| line-3 | line-3-0764-0463-s007028 | reverse | 5 | pending |
| line-3 | line-3-0653-0536-s010036 | forward | 4 | pending |
| line-3 | line-3-0653-0536-s010036 | reverse | 4 | pending |
| line-3 | line-3-0556-0541-s012228 | forward | 4 | pending |
| line-3 | line-3-0556-0541-s012228 | reverse | 4 | pending |
| line-3 | line-3-0425-0612-s015889 | reverse | 4 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Yemen/Taiz/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
