# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **63 trainsets at 14 stations**; largest initial station queue **7**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0020-0297-s000000 | forward | 4 | pending |
| line-1 | line-1-0301-0382-s006506 | forward | 4 | pending |
| line-1 | line-1-0301-0382-s006506 | reverse | 3 | pending |
| line-1 | line-1-0376-0374-s008219 | forward | 3 | pending |
| line-1 | line-1-0376-0374-s008219 | reverse | 3 | pending |
| line-1 | line-1-0449-0374-s010201 | forward | 3 | pending |
| line-1 | line-1-0449-0374-s010201 | reverse | 3 | pending |
| line-1 | line-1-0528-0329-s012182 | reverse | 3 | pending |
| line-2 | line-2-0431-0420-s000000 | forward | 3 | pending |
| line-2 | line-2-0376-0374-s001720 | forward | 3 | pending |
| line-2 | line-2-0376-0374-s001720 | reverse | 3 | pending |
| line-2 | line-2-0390-0236-s004686 | forward | 3 | pending |
| line-2 | line-2-0390-0236-s004686 | reverse | 3 | pending |
| line-2 | line-2-0413-0102-s007646 | reverse | 2 | pending |
| line-3 | line-3-0208-0369-s000000 | forward | 3 | pending |
| line-3 | line-3-0291-0339-s002061 | forward | 3 | pending |
| line-3 | line-3-0291-0339-s002061 | reverse | 3 | pending |
| line-3 | line-3-0376-0374-s004114 | forward | 3 | pending |
| line-3 | line-3-0376-0374-s004114 | reverse | 2 | pending |
| line-3 | line-3-0412-0270-s006574 | forward | 2 | pending |
| line-3 | line-3-0412-0270-s006574 | reverse | 2 | pending |
| line-3 | line-3-0390-0161-s009055 | reverse | 2 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Kenya/Machakos/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
