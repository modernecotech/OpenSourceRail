# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **134 trainsets at 25 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0283-0726-s000000 | forward | 3 | pending |
| line-1 | line-1-0362-0640-s003001 | forward | 3 | pending |
| line-1 | line-1-0362-0640-s003001 | reverse | 3 | pending |
| line-1 | line-1-0462-0570-s006028 | forward | 3 | pending |
| line-1 | line-1-0462-0570-s006028 | reverse | 3 | pending |
| line-1 | line-1-0531-0533-s007802 | forward | 3 | pending |
| line-1 | line-1-0531-0533-s007802 | reverse | 3 | pending |
| line-1 | line-1-0557-0496-s009036 | forward | 3 | pending |
| line-1 | line-1-0557-0496-s009036 | reverse | 2 | pending |
| line-1 | line-1-0506-0376-s012055 | forward | 2 | pending |
| line-1 | line-1-0506-0376-s012055 | reverse | 2 | pending |
| line-1 | line-1-0569-0240-s015785 | forward | 2 | pending |
| line-1 | line-1-0569-0240-s015785 | reverse | 2 | pending |
| line-1 | line-1-0582-0176-s017374 | forward | 2 | pending |
| line-1 | line-1-0582-0176-s017374 | reverse | 2 | pending |
| line-1 | line-1-0548-0120-s018987 | reverse | 2 | pending |
| line-2 | line-2-0000-0301-s000000 | forward | 4 | pending |
| line-2 | line-2-0134-0317-s003125 | forward | 4 | pending |
| line-2 | line-2-0134-0317-s003125 | reverse | 4 | pending |
| line-2 | line-2-0277-0406-s006757 | forward | 4 | pending |
| line-2 | line-2-0277-0406-s006757 | reverse | 3 | pending |
| line-2 | line-2-0399-0459-s009769 | forward | 3 | pending |
| line-2 | line-2-0399-0459-s009769 | reverse | 3 | pending |
| line-2 | line-2-0531-0533-s013133 | forward | 3 | pending |
| line-2 | line-2-0531-0533-s013133 | reverse | 3 | pending |
| line-2 | line-2-0626-0556-s015786 | forward | 3 | pending |
| line-2 | line-2-0626-0556-s015786 | reverse | 3 | pending |
| line-2 | line-2-0752-0514-s018787 | forward | 3 | pending |
| line-2 | line-2-0752-0514-s018787 | reverse | 3 | pending |
| line-2 | line-2-0804-0434-s021286 | reverse | 3 | pending |
| line-3 | line-3-0259-1031-s000000 | forward | 4 | pending |
| line-3 | line-3-0363-0788-s007018 | forward | 4 | pending |
| line-3 | line-3-0363-0788-s007018 | reverse | 4 | pending |
| line-3 | line-3-0461-0682-s010032 | forward | 4 | pending |
| line-3 | line-3-0461-0682-s010032 | reverse | 4 | pending |
| line-3 | line-3-0529-0614-s012025 | forward | 4 | pending |
| line-3 | line-3-0529-0614-s012025 | reverse | 3 | pending |
| line-3 | line-3-0531-0533-s014028 | forward | 3 | pending |
| line-3 | line-3-0531-0533-s014028 | reverse | 3 | pending |
| line-3 | line-3-0602-0496-s016053 | forward | 3 | pending |
| line-3 | line-3-0602-0496-s016053 | reverse | 3 | pending |
| line-3 | line-3-0678-0391-s019072 | forward | 3 | pending |
| line-3 | line-3-0678-0391-s019072 | reverse | 3 | pending |
| line-3 | line-3-0729-0230-s022764 | reverse | 3 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Saudi Arabia/Tabuk/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
