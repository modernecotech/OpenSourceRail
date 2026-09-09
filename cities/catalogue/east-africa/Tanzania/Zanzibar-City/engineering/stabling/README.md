# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **134 trainsets at 21 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0178-0650-s000000 | forward | 4 | pending |
| line-1 | line-1-0415-0602-s005984 | forward | 4 | pending |
| line-1 | line-1-0415-0602-s005984 | reverse | 4 | pending |
| line-1 | line-1-0511-0529-s009005 | forward | 4 | pending |
| line-1 | line-1-0511-0529-s009005 | reverse | 4 | pending |
| line-1 | line-1-0545-0520-s010623 | forward | 3 | pending |
| line-1 | line-1-0545-0520-s010623 | reverse | 3 | pending |
| line-1 | line-1-0615-0556-s013625 | forward | 3 | pending |
| line-1 | line-1-0615-0556-s013625 | reverse | 3 | pending |
| line-1 | line-1-0724-0594-s016358 | forward | 3 | pending |
| line-1 | line-1-0724-0594-s016358 | reverse | 3 | pending |
| line-1 | line-1-0826-0578-s019084 | reverse | 3 | pending |
| line-2 | line-2-0363-0136-s000000 | forward | 4 | pending |
| line-2 | line-2-0503-0420-s006840 | forward | 4 | pending |
| line-2 | line-2-0503-0420-s006840 | reverse | 4 | pending |
| line-2 | line-2-0553-0494-s008786 | forward | 4 | pending |
| line-2 | line-2-0553-0494-s008786 | reverse | 4 | pending |
| line-2 | line-2-0551-0556-s010187 | forward | 4 | pending |
| line-2 | line-2-0551-0556-s010187 | reverse | 4 | pending |
| line-2 | line-2-0536-0618-s011796 | forward | 4 | pending |
| line-2 | line-2-0536-0618-s011796 | reverse | 4 | pending |
| line-2 | line-2-0611-0671-s014802 | forward | 4 | pending |
| line-2 | line-2-0611-0671-s014802 | reverse | 3 | pending |
| line-2 | line-2-0712-0922-s021027 | reverse | 3 | pending |
| line-3 | line-3-1069-0872-s000000 | forward | 4 | pending |
| line-3 | line-3-0832-0703-s007015 | forward | 4 | pending |
| line-3 | line-3-0832-0703-s007015 | reverse | 4 | pending |
| line-3 | line-3-0741-0616-s010035 | forward | 4 | pending |
| line-3 | line-3-0741-0616-s010035 | reverse | 4 | pending |
| line-3 | line-3-0637-0565-s013060 | forward | 4 | pending |
| line-3 | line-3-0637-0565-s013060 | reverse | 4 | pending |
| line-3 | line-3-0551-0556-s015235 | forward | 4 | pending |
| line-3 | line-3-0551-0556-s015235 | reverse | 4 | pending |
| line-3 | line-3-0482-0632-s018821 | forward | 4 | pending |
| line-3 | line-3-0482-0632-s018821 | reverse | 4 | pending |
| line-3 | line-3-0434-0670-s021743 | reverse | 3 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Tanzania/Zanzibar-City/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
