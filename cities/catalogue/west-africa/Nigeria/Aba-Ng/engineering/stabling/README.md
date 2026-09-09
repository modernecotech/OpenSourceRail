# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **70 trainsets at 13 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0615-0713-s000000 | forward | 4 | pending |
| line-1 | line-1-0580-0580-s003009 | forward | 4 | pending |
| line-1 | line-1-0580-0580-s003009 | reverse | 4 | pending |
| line-1 | line-1-0558-0547-s004364 | forward | 3 | pending |
| line-1 | line-1-0558-0547-s004364 | reverse | 3 | pending |
| line-1 | line-1-0608-0494-s006014 | forward | 3 | pending |
| line-1 | line-1-0608-0494-s006014 | reverse | 3 | pending |
| line-1 | line-1-0723-0266-s012357 | reverse | 3 | pending |
| line-2 | line-2-0575-0330-s000000 | forward | 3 | pending |
| line-2 | line-2-0569-0455-s003334 | forward | 3 | pending |
| line-2 | line-2-0569-0455-s003334 | reverse | 3 | pending |
| line-2 | line-2-0588-0545-s006336 | forward | 3 | pending |
| line-2 | line-2-0588-0545-s006336 | reverse | 3 | pending |
| line-2 | line-2-0657-0561-s008063 | reverse | 3 | pending |
| line-3 | line-3-0879-0306-s000000 | forward | 5 | pending |
| line-3 | line-3-0715-0482-s006214 | forward | 4 | pending |
| line-3 | line-3-0715-0482-s006214 | reverse | 4 | pending |
| line-3 | line-3-0592-0549-s009229 | forward | 4 | pending |
| line-3 | line-3-0592-0549-s009229 | reverse | 4 | pending |
| line-3 | line-3-0541-0610-s011521 | reverse | 4 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/west-africa/Nigeria/Aba-Ng/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
