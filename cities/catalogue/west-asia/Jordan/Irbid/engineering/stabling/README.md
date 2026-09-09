# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **107 trainsets at 21 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0840-0623-s000000 | forward | 3 | pending |
| line-1 | line-1-0736-0627-s003572 | forward | 3 | pending |
| line-1 | line-1-0736-0627-s003572 | reverse | 3 | pending |
| line-1 | line-1-0673-0623-s005189 | forward | 3 | pending |
| line-1 | line-1-0673-0623-s005189 | reverse | 3 | pending |
| line-1 | line-1-0555-0553-s008515 | forward | 3 | pending |
| line-1 | line-1-0555-0553-s008515 | reverse | 3 | pending |
| line-1 | line-1-0471-0526-s010965 | forward | 3 | pending |
| line-1 | line-1-0471-0526-s010965 | reverse | 3 | pending |
| line-1 | line-1-0402-0548-s013405 | forward | 3 | pending |
| line-1 | line-1-0402-0548-s013405 | reverse | 3 | pending |
| line-1 | line-1-0312-0567-s015842 | reverse | 3 | pending |
| line-2 | line-2-0700-0815-s000000 | forward | 3 | pending |
| line-2 | line-2-0620-0704-s003010 | forward | 3 | pending |
| line-2 | line-2-0620-0704-s003010 | reverse | 3 | pending |
| line-2 | line-2-0545-0613-s006026 | forward | 3 | pending |
| line-2 | line-2-0545-0613-s006026 | reverse | 3 | pending |
| line-2 | line-2-0555-0553-s007527 | forward | 3 | pending |
| line-2 | line-2-0555-0553-s007527 | reverse | 3 | pending |
| line-2 | line-2-0578-0475-s009669 | forward | 2 | pending |
| line-2 | line-2-0578-0475-s009669 | reverse | 2 | pending |
| line-2 | line-2-0577-0389-s011828 | forward | 2 | pending |
| line-2 | line-2-0577-0389-s011828 | reverse | 2 | pending |
| line-2 | line-2-0634-0323-s013970 | reverse | 2 | pending |
| line-3 | line-3-0351-0708-s000000 | forward | 4 | pending |
| line-3 | line-3-0453-0614-s003006 | forward | 4 | pending |
| line-3 | line-3-0453-0614-s003006 | reverse | 4 | pending |
| line-3 | line-3-0555-0553-s005777 | forward | 4 | pending |
| line-3 | line-3-0555-0553-s005777 | reverse | 3 | pending |
| line-3 | line-3-0635-0506-s009037 | forward | 3 | pending |
| line-3 | line-3-0635-0506-s009037 | reverse | 3 | pending |
| line-3 | line-3-0712-0447-s011502 | forward | 3 | pending |
| line-3 | line-3-0712-0447-s011502 | reverse | 3 | pending |
| line-3 | line-3-0808-0447-s013947 | forward | 3 | pending |
| line-3 | line-3-0808-0447-s013947 | reverse | 3 | pending |
| line-3 | line-3-0944-0336-s018870 | reverse | 3 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Jordan/Irbid/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
