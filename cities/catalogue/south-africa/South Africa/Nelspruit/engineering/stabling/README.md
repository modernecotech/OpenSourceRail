# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **80 trainsets at 16 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0300-0176-s000000 | forward | 3 | pending |
| line-1 | line-1-0303-0283-s003017 | forward | 3 | pending |
| line-1 | line-1-0303-0283-s003017 | reverse | 3 | pending |
| line-1 | line-1-0374-0372-s006118 | forward | 3 | pending |
| line-1 | line-1-0374-0372-s006118 | reverse | 3 | pending |
| line-1 | line-1-0314-0427-s008352 | forward | 3 | pending |
| line-1 | line-1-0314-0427-s008352 | reverse | 2 | pending |
| line-1 | line-1-0339-0524-s010599 | forward | 2 | pending |
| line-1 | line-1-0339-0524-s010599 | reverse | 2 | pending |
| line-1 | line-1-0266-0580-s012842 | reverse | 2 | pending |
| line-2 | line-2-0164-0368-s000000 | forward | 3 | pending |
| line-2 | line-2-0282-0357-s003025 | forward | 3 | pending |
| line-2 | line-2-0282-0357-s003025 | reverse | 3 | pending |
| line-2 | line-2-0374-0372-s005434 | forward | 3 | pending |
| line-2 | line-2-0374-0372-s005434 | reverse | 3 | pending |
| line-2 | line-2-0466-0345-s007682 | forward | 3 | pending |
| line-2 | line-2-0466-0345-s007682 | reverse | 3 | pending |
| line-2 | line-2-0538-0385-s009926 | forward | 3 | pending |
| line-2 | line-2-0538-0385-s009926 | reverse | 3 | pending |
| line-2 | line-2-0732-0367-s014426 | reverse | 3 | pending |
| line-3 | line-3-0345-0134-s000000 | forward | 4 | pending |
| line-3 | line-3-0382-0263-s003019 | forward | 4 | pending |
| line-3 | line-3-0382-0263-s003019 | reverse | 4 | pending |
| line-3 | line-3-0374-0372-s005613 | forward | 4 | pending |
| line-3 | line-3-0374-0372-s005613 | reverse | 4 | pending |
| line-3 | line-3-0471-0564-s011431 | reverse | 4 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/south-africa/South Africa/Nelspruit/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
