# Distributed station stabling candidate

Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.

Operating allocation: **115 trainsets at 19 stations**; largest initial station queue **13**. Physical release: **open**.

This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.

| Line | Station | Direction | Initial trainsets | Verified track slots |
|---|---|---|---:|---|
| line-1 | line-1-0784-0410-s000000 | forward | 3 | pending |
| line-1 | line-1-0655-0460-s003378 | forward | 3 | pending |
| line-1 | line-1-0655-0460-s003378 | reverse | 3 | pending |
| line-1 | line-1-0568-0505-s005859 | forward | 3 | pending |
| line-1 | line-1-0568-0505-s005859 | reverse | 3 | pending |
| line-1 | line-1-0543-0556-s007242 | forward | 3 | pending |
| line-1 | line-1-0543-0556-s007242 | reverse | 3 | pending |
| line-1 | line-1-0486-0591-s008868 | forward | 3 | pending |
| line-1 | line-1-0486-0591-s008868 | reverse | 3 | pending |
| line-1 | line-1-0423-0544-s011609 | forward | 2 | pending |
| line-1 | line-1-0423-0544-s011609 | reverse | 2 | pending |
| line-1 | line-1-0347-0630-s014345 | forward | 2 | pending |
| line-1 | line-1-0347-0630-s014345 | reverse | 2 | pending |
| line-1 | line-1-0232-0603-s017091 | reverse | 2 | pending |
| line-2 | line-2-0906-1035-s000000 | forward | 7 | pending |
| line-2 | line-2-0638-0635-s012053 | forward | 7 | pending |
| line-2 | line-2-0638-0635-s012053 | reverse | 6 | pending |
| line-2 | line-2-0543-0556-s015219 | forward | 6 | pending |
| line-2 | line-2-0543-0556-s015219 | reverse | 6 | pending |
| line-2 | line-2-0504-0502-s018077 | forward | 6 | pending |
| line-2 | line-2-0504-0502-s018077 | reverse | 6 | pending |
| line-2 | line-2-0449-0306-s023627 | reverse | 6 | pending |
| line-3 | line-3-0393-0347-s000000 | forward | 3 | pending |
| line-3 | line-3-0438-0474-s003018 | forward | 3 | pending |
| line-3 | line-3-0438-0474-s003018 | reverse | 3 | pending |
| line-3 | line-3-0543-0556-s006413 | forward | 3 | pending |
| line-3 | line-3-0543-0556-s006413 | reverse | 3 | pending |
| line-3 | line-3-0497-0630-s008970 | forward | 3 | pending |
| line-3 | line-3-0497-0630-s008970 | reverse | 3 | pending |
| line-3 | line-3-0434-0658-s010869 | forward | 3 | pending |
| line-3 | line-3-0434-0658-s010869 | reverse | 2 | pending |
| line-3 | line-3-0411-0736-s012742 | reverse | 2 | pending |

- Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.
- The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.
- Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.
- Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.
- Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.

Regenerate this report and its local runnable scenario with:

```bash
.venv/bin/python tools/automation/generate-stabling-plan.py --design 'cities/catalogue/east-africa/Kenya/Kisumu/design.toml'
```

The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.
