# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **76 trainsets at 16 stations**; largest initial station queue **6**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0476-0588-s000000 | forward | 3 | pending |
| line-1 | line-1-0452-0462-s003017 | forward | 3 | pending |
| line-1 | line-1-0452-0462-s003017 | reverse | 3 | pending |
| line-1 | line-1-0372-0388-s005569 | forward | 3 | pending |
| line-1 | line-1-0372-0388-s005569 | reverse | 3 | pending |
| line-1 | line-1-0391-0320-s007632 | forward | 2 | pending |
| line-1 | line-1-0391-0320-s007632 | reverse | 2 | pending |
| line-1 | line-1-0341-0217-s010401 | reverse | 2 | pending |
| line-2 | line-2-0096-0563-s000000 | forward | 3 | pending |
| line-2 | line-2-0204-0460-s003013 | forward | 3 | pending |
| line-2 | line-2-0204-0460-s003013 | reverse | 3 | pending |
| line-2 | line-2-0297-0436-s005072 | forward | 3 | pending |
| line-2 | line-2-0297-0436-s005072 | reverse | 3 | pending |
| line-2 | line-2-0372-0388-s007148 | forward | 3 | pending |
| line-2 | line-2-0372-0388-s007148 | reverse | 3 | pending |
| line-2 | line-2-0445-0380-s009033 | forward | 3 | pending |
| line-2 | line-2-0445-0380-s009033 | reverse | 3 | pending |
| line-2 | line-2-0689-0283-s015065 | reverse | 3 | pending |
| line-3 | line-3-0525-0111-s000000 | forward | 4 | pending |
| line-3 | line-3-0416-0275-s004310 | forward | 3 | pending |
| line-3 | line-3-0416-0275-s004310 | reverse | 3 | pending |
| line-3 | line-3-0372-0388-s007462 | forward | 3 | pending |
| line-3 | line-3-0372-0388-s007462 | reverse | 3 | pending |
| line-3 | line-3-0296-0406-s009330 | forward | 3 | pending |
| line-3 | line-3-0296-0406-s009330 | reverse | 3 | pending |
| line-3 | line-3-0218-0436-s011214 | reverse | 3 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Kenya/Nyeri/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
