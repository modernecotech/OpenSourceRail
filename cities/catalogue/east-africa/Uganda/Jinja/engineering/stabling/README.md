# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **87 trainsets at 16 stations**; largest initial station queue **8**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0143-0732-s000000 | forward | 4 | pending |
| line-1 | line-1-0267-0590-s004716 | forward | 3 | pending |
| line-1 | line-1-0267-0590-s004716 | reverse | 3 | pending |
| line-1 | line-1-0342-0483-s007726 | forward | 3 | pending |
| line-1 | line-1-0342-0483-s007726 | reverse | 3 | pending |
| line-1 | line-1-0384-0378-s011295 | forward | 3 | pending |
| line-1 | line-1-0384-0378-s011295 | reverse | 3 | pending |
| line-1 | line-1-0463-0382-s013520 | forward | 3 | pending |
| line-1 | line-1-0463-0382-s013520 | reverse | 3 | pending |
| line-1 | line-1-0556-0341-s015753 | reverse | 3 | pending |
| line-2 | line-2-0648-0466-s000000 | forward | 4 | pending |
| line-2 | line-2-0546-0435-s003016 | forward | 4 | pending |
| line-2 | line-2-0546-0435-s003016 | reverse | 3 | pending |
| line-2 | line-2-0421-0430-s006028 | forward | 3 | pending |
| line-2 | line-2-0421-0430-s006028 | reverse | 3 | pending |
| line-2 | line-2-0384-0378-s007450 | forward | 3 | pending |
| line-2 | line-2-0384-0378-s007450 | reverse | 3 | pending |
| line-2 | line-2-0277-0213-s012303 | reverse | 3 | pending |
| line-3 | line-3-0732-0095-s000000 | forward | 4 | pending |
| line-3 | line-3-0512-0297-s007013 | forward | 4 | pending |
| line-3 | line-3-0512-0297-s007013 | reverse | 4 | pending |
| line-3 | line-3-0422-0313-s010021 | forward | 4 | pending |
| line-3 | line-3-0422-0313-s010021 | reverse | 4 | pending |
| line-3 | line-3-0384-0378-s011702 | forward | 4 | pending |
| line-3 | line-3-0384-0378-s011702 | reverse | 3 | pending |
| line-3 | line-3-0315-0459-s014008 | reverse | 3 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Uganda/Jinja/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
