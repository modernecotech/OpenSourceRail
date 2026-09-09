# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **99 trainsets at 18 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0594-0760-s000000 | forward | 3 | pending |
| line-1 | line-1-0592-0640-s003015 | forward | 3 | pending |
| line-1 | line-1-0592-0640-s003015 | reverse | 3 | pending |
| line-1 | line-1-0548-0543-s005827 | forward | 3 | pending |
| line-1 | line-1-0548-0543-s005827 | reverse | 3 | pending |
| line-1 | line-1-0495-0424-s009018 | forward | 3 | pending |
| line-1 | line-1-0495-0424-s009018 | reverse | 3 | pending |
| line-1 | line-1-0461-0336-s011196 | forward | 3 | pending |
| line-1 | line-1-0461-0336-s011196 | reverse | 3 | pending |
| line-1 | line-1-0412-0263-s013371 | reverse | 3 | pending |
| line-2 | line-2-0169-0808-s000000 | forward | 4 | pending |
| line-2 | line-2-0307-0732-s003510 | forward | 3 | pending |
| line-2 | line-2-0307-0732-s003510 | reverse | 3 | pending |
| line-2 | line-2-0423-0637-s007025 | forward | 3 | pending |
| line-2 | line-2-0423-0637-s007025 | reverse | 3 | pending |
| line-2 | line-2-0548-0543-s010721 | forward | 3 | pending |
| line-2 | line-2-0548-0543-s010721 | reverse | 3 | pending |
| line-2 | line-2-0626-0527-s013054 | forward | 3 | pending |
| line-2 | line-2-0626-0527-s013054 | reverse | 3 | pending |
| line-2 | line-2-0699-0487-s015375 | forward | 3 | pending |
| line-2 | line-2-0699-0487-s015375 | reverse | 3 | pending |
| line-2 | line-2-0785-0507-s017696 | reverse | 3 | pending |
| line-3 | line-3-0698-0406-s000000 | forward | 4 | pending |
| line-3 | line-3-0608-0448-s003005 | forward | 4 | pending |
| line-3 | line-3-0608-0448-s003005 | reverse | 4 | pending |
| line-3 | line-3-0548-0543-s005766 | forward | 4 | pending |
| line-3 | line-3-0548-0543-s005766 | reverse | 4 | pending |
| line-3 | line-3-0428-0455-s009037 | forward | 4 | pending |
| line-3 | line-3-0428-0455-s009037 | reverse | 4 | pending |
| line-3 | line-3-0191-0361-s014899 | reverse | 4 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/south-asia/Bangladesh/Rangpur/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
