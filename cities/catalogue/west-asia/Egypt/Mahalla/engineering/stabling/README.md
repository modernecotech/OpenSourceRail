# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **84 trainsets at 14 stations**; largest initial station queue **10**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0700-0463-s000000 | forward | 4 | pending |
| line-1 | line-1-0639-0491-s001601 | forward | 4 | pending |
| line-1 | line-1-0639-0491-s001601 | reverse | 4 | pending |
| line-1 | line-1-0556-0555-s004018 | forward | 3 | pending |
| line-1 | line-1-0556-0555-s004018 | reverse | 3 | pending |
| line-1 | line-1-0564-0711-s007621 | forward | 3 | pending |
| line-1 | line-1-0564-0711-s007621 | reverse | 3 | pending |
| line-1 | line-1-0594-0921-s012269 | reverse | 3 | pending |
| line-2 | line-2-1091-0156-s000000 | forward | 6 | pending |
| line-2 | line-2-0747-0479-s010791 | forward | 5 | pending |
| line-2 | line-2-0747-0479-s010791 | reverse | 5 | pending |
| line-2 | line-2-0659-0592-s013803 | forward | 5 | pending |
| line-2 | line-2-0659-0592-s013803 | reverse | 5 | pending |
| line-2 | line-2-0610-0680-s016225 | forward | 5 | pending |
| line-2 | line-2-0610-0680-s016225 | reverse | 5 | pending |
| line-2 | line-2-0574-0783-s018642 | reverse | 5 | pending |
| line-3 | line-3-0647-0470-s000000 | forward | 3 | pending |
| line-3 | line-3-0575-0506-s001894 | forward | 3 | pending |
| line-3 | line-3-0575-0506-s001894 | reverse | 3 | pending |
| line-3 | line-3-0556-0555-s003790 | forward | 3 | pending |
| line-3 | line-3-0556-0555-s003790 | reverse | 2 | pending |
| line-3 | line-3-0505-0671-s007373 | reverse | 2 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-asia/Egypt/Mahalla/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
